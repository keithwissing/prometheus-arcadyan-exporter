import json
import logging
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

from prometheus_client import start_http_server
from prometheus_client.core import (REGISTRY, GaugeMetricFamily, InfoMetricFamily)

class CustomCollector(object):
    def __init__(self, _ip_address):
        self.ip_address = _ip_address
        self.process_stats = {}

    def get_json_body(self):
        if '.' in self.ip_address:
            try:
                return urlopen(f'http://{self.ip_address}/TMI/v1/gateway?get=all').read()
            except URLError as e:
                logging.error('Error getting data from gateway')
                logging.error(e)
                return None
        else:
            with open('response.json', 'r') as file:
                return ''.join(file.readlines())

    def collect(self):
        body = self.get_json_body()
        if not body:
            return
        stats = json.loads(body)
        if not stats:
            logging.warning('not stats')
            return
        signal = stats.get('signal', None)
        if not signal:
            logging.warning('No signal data in returned body')
            logging.warning(body)
            return
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

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

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
