#include "rdb_client.h"

NetClient::NetClient(std::shared_ptr<Channel> channel) : stub_(NetService::NewStub(channel)) {}
OperationRequest request;

std::string NetClient::GetBatchData(const std::string& key, const std::string& value) {
    request.add_keys(key);
    request.add_values(value);
    return "OK";
}

std::string NetClient::OperationService(const std::string& operation, const std::string& key, const std::string& value) {
    if (operation == "PUT") {
        request.set_operation(OperationRequest::PUT);
    } else if (operation == "GET") {
        request.set_operation(OperationRequest::GET);
    } else if (operation == "DELETE") {
        request.set_operation(OperationRequest::DELETE);
    } else if (operation == "BatchPut") {
        request.set_operation(OperationRequest::BatchPut);
    } else {
        return "Invalid operation";
    }

    if (operation != "BatchPut") {
        request.add_keys(key);
        request.add_values(value);
    }

    OperationResponse response;
    ClientContext context;

    Status status = stub_->OperationService(&context, request, &response);

    if (status.ok()) {
        return response.result();
    } else {
        return "RPC failed";
    }
}
