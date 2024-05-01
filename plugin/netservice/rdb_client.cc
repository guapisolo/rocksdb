#include <iostream>
#include <memory>
#include <string>

// GRPC
#include <grpcpp/grpcpp.h>
#include "netservice.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;

using netservice::OperationRequest;
using netservice::OperationResponse;
using netservice::NetService;

class NetClient {
public:
    NetClient(std::shared_ptr<Channel> channel) : stub_(NetService::NewStub(channel)) {}

    std::string OperationService(const std::string& operation, const std::string& key, const std::string& value) {
        OperationRequest request;

        if (operation == "PUT") {
            request.set_operation(OperationRequest::PUT);
        } else if (operation == "GET") {
            request.set_operation(OperationRequest::GET);
        } else if (operation == "DELETE") {
            request.set_operation(OperationRequest::DELETE);
        } else {
            return "Invalid operation";
        }

        request.set_key(key);
        request.set_value(value);

        OperationResponse response;
        ClientContext context;

        Status status = stub_->OperationService(&context, request, &response);

        if (status.ok()) {
            return response.result();
        } else {
            return "RPC failed";
        }
    }

private:
    std::unique_ptr<NetService::Stub> stub_;
};

int main() {
    std::string server_address = "0.0.0.0:50050";
    
    // To be supplied by the benchmark
    std::string operation = "PUT";
    std::string key = "key";
    std::string value = "value";

    NetClient client(grpc::CreateChannel(server_address, grpc::InsecureChannelCredentials()));

    std::string result;
    result = client.OperationService(operation, key, value);

    std::cout << "Result: " << result << std::endl;
    return 0;
}
