#pragma once

#include <iostream>
#include <memory>
#include <string>

#include "absl/flags/flag.h"
#include "absl/flags/parse.h"
#include "absl/strings/str_format.h"

// GRPC
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>

#include "netservice.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using grpc::ClientWriter;

using netservice::OperationRequest;
using netservice::OperationResponse;
using netservice::NetService;


class NetClient {
public:
    NetClient(std::shared_ptr<Channel> channel);

    std::string GetBatchData(const std::string& key, const std::string& value);
    bool StartStream();
    bool WriteToStream(const std::string& operation, const std::string& key, const std::string& value);
    std::string FinishStream();

private:
    std::unique_ptr<NetService::Stub> stub_;
    ClientContext stream_context_;
    std::unique_ptr<ClientWriter<OperationRequest>> stream_writer_;
    OperationResponse stream_response_;
};
