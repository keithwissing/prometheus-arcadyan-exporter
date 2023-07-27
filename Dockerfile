FROM alpine
RUN apk update && apk add py3-prometheus-client
WORKDIR /var/python_scripts/
COPY prometheus_arcadyan_exporter.py /var/python_scripts/prometheus_arcadyan_exporter.py
COPY response.json /var/python_scripts/response.json
CMD  /usr/bin/python3 /var/python_scripts/prometheus_arcadyan_exporter.py $GATEWAY_IP_ADDRESS
