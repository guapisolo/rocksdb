#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "Net.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;

using Net::OperationRequest;
using Net::OperationResponse;
using Net::NetService;

class NetClient {
public:
    NetClient(std::shared_ptr<Channel> channel) : stub_(NetService::NewStub(channel)) {}

    std::string PutService(const std::string& key, const std::string& value) {
        OperationRequest request;
        request.set_operation(OperationRequest::PUT);
        request.set_key(key);
        request.set_value(value);

        OperationResponse response;
        ClientContext context;
        Status status = stub_->NetOperation(&context, request, &response);
        if (status.ok()) {
            return response.result();
        } else {
            return "RPC failed: " + status.error_message();
        }
    }

    std::string GetService(const std::string& key) {
        OperationRequest request;
        request.set_operation(OperationRequest::GET);
        request.set_key(key);

        OperationResponse response;
        ClientContext context;
        Status status = stub_->NetOperation(&context, request, &response);
        if (status.ok()) {
            return response.result();
        } else {
            return "RPC failed: " + status.error_message();
        }
    }

    std::string DeleteService(const std::string& key) {
        OperationRequest request;
        request.set_operation(OperationRequest::DELETE);
        request.set_key(key);

        OperationResponse response;
        ClientContext context;
        Status status = stub_->NetOperation(&context, request, &response);
        if (status.ok()) {
            return response.result();
        } else {
            return "RPC failed: " + status.error_message();
        }
    }

private:
    std::unique_ptr<NetService::Stub> stub_;
};

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <server_address> <operation> <key> [value]" << std::endl;
        return 1;
    }
    std::string server_address(argv[1]);
    std::string operation(argv[2]);
    std::string key(argv[3]);
    std::string value;
    if (argc == 5) {
        value = argv[4];
    }

    NetClient client(grpc::CreateChannel(server_address, grpc::InsecureChannelCredentials()));

    std::string result;
    if (operation == "PUT") {
        result = client.Put(key, value);
    } else if (operation == "GET") {
        result = client.Get(key);
    } else if (operation == "DELETE") {
        result = client.Delete(key);
    } else {
        result = "Invalid operation";
    }

    std::cout << "Result: " << result << std::endl;
    return 0;
}
