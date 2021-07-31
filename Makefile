proto: messages.proto
	protoc --proto_path=./ --python_out=./ messages.proto
