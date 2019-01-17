
generate-proto:
	python3 -m grpc_tools.protoc -I=proto/ -I=.  --python_out=. --grpc_python_out=. acquired.proto

run-server:
	python3 server.py

run-client:
	python3 client.py