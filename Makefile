test: build run

build:
	docker build . -t arcadyan
run:
	docker run --rm -p 9100:9100 --env GATEWAY_IP_ADDRESS=127 arcadyan