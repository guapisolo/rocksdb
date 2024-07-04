#include "rdb_client.h"

NetClient::NetClient(std::shared_ptr<Channel> channel) : stub_(NetService::NewStub(channel)) {}
OperationRequest request;

std::string NetClient::GetBatchData(const std::string& key, const std::string& value) {
    request.add_keys(key);
    request.add_values(value);
    return "OK";
}

bool NetClient::StartStream() {
    stream_writer_ = stub_->OperationService(&stream_context_, &stream_response_);
    return stream_writer_ != nullptr;
}

bool NetClient::WriteToStream(const std::string& operation, const std::string& key, const std::string& value) {
    if (!stream_writer_) return false;

    if (operation == "Put") {
        request.set_operation(OperationRequest::Put);
    } else if (operation == "Get") {
        request.set_operation(OperationRequest::Get);
    } else if (operation == "Delete") {
        request.set_operation(OperationRequest::Delete);
    } else if (operation == "BatchPut") {
        request.set_operation(OperationRequest::BatchPut);
    } else {
        return "Invalid operation";
    }

    request.add_keys(key);
    request.add_values(value);

    fprintf(stderr, "Operation: %d\n", request.operation());

    return stream_writer_->Write(request);
}

std::string NetClient::FinishStream() {
    if (!stream_writer_) return "Stream not started";

    stream_writer_->WritesDone();
    Status status = stream_writer_->Finish();

    if (status.ok()) {
        return stream_response_.result();
    } else {
        return "RPC failed";
    }
}
