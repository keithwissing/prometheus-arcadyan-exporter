from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, REGISTRY
from prometheus_client import start_http_server
from urllib.request import urlopen
import json
import re
import time
import sys
import logging

class CustomCollector(object):
    def __init__(self, _ip_address):
        self.ip_address = _ip_address
        self.process_stats = {}

    def collect(self):
        if '.' in self.ip_address:
            stats = json.loads(urlopen(f'http://{self.ip_address}/TMI/v1/gateway?get=all').read())
        else:
            with open('response.json', 'r') as file:
                stats = json.loads(''.join(file.readlines()))
        signal = stats['signal']

        family = GaugeMetricFamily('gateway_uptime', 'Gateway uptime')
        value = float(stats.get('time', {}).get('upTime', 0))
        family.add_metric([], value)
        yield family

        family = GaugeMetricFamily('gateway_signal', 'Gateway cellular signal', labels=['network', 'key'])
        for k in ['bars', 'cid', 'rsrp', 'rsrq', 'rssi', 'sinr']:
            for network in ['4g', '5g']:
                val = signal.get(network, {}).get(k, None)
                if val is not None:
                    family.add_metric([network, k], float(val))
        yield family
        return

        items =[ ('bars', 'gateway_cell_bars', 'Bars of cellular signal') ] 
        for k in ["rsrp", "rsrq", "rssi", "sinr"]:
            items.append((k, f'gateway_signal_{k}', f'Cellular signal {k}'))

        for i in items:
            family = GaugeMetricFamily(i[1], i[2], labels=['network'])
            for network in ['4g', '5g']:
                if network in signal:
                    net_signal = signal[network]
                    if i[0] in net_signal:
                        value = float(net_signal[i[0]])
                        family.add_metric([network], value)
            yield family

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    try:
        url = sys.argv[1]
        REGISTRY.register(CustomCollector(url))
    except IndexError:
        logging.error(
            "Provide gateway ip address as environment variable to container, "
            "e.g. GATEWAY_IP_ADDRESS=192.168.12.1")
        exit()

    start_http_server(9100)

    logging.info('Started, Gateway IP Address: ' + sys.argv[1])
    logging.info('Metrics at: http://localhost:9100/metrics')

    while True:
        time.sleep(1)
