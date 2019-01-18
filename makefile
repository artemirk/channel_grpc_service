
generate-proto:
	python3 -m grpc_tools.protoc -I=proto/ -I=.  --python_out=. --grpc_python_out=. acquired.proto

run-server-1:
	python3 server.py --port=50051 --graceful_shutdown_timeout=180

run-server-2:
	python3 server.py --port=50052 --graceful_shutdown_timeout=180

run-client:
	python3 client.py