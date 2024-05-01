#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <grpcpp/grpcpp.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/health_check_service_interface.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>
#include <grpcpp/security/server_credentials.h>
#include <rocksdb/db.h>
#include <rocksdb/options.h>
#include "NetService.grpc.pb.h"

#include <bits/stdc++.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <queue>

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

using Net::OperationRequest;
using Net::OperationResponse;
using Net::NetService;

// queue shared across multiple thread
std::queue<std::string> optimizationQueue;

class NetServiceImpl final : public NetService::Service {
public:
    NetServiceImpl(const std::string& db_path) {
        rocksdb::Options options;
        options.create_if_missing = true;
        rocksdb::Status status = rocksdb::DB::Open(options, db_path, &db_);
        if (!status.ok()) {
            std::cerr << "Error opening database: " << status.ToString() << std::endl;
            exit(1);
        }
    }

    ~NetServiceImpl() {
        delete db_;
    }

    Status RunNetService(ServerContext* context, const OperationRequest* request,
                             OperationResponse* response) override {
        // Maybe just implement a data structure here and have another piece of code that actually does the operation?
        switch (request->operation()) {
            case OperationRequest::PUT: {
                rocksdb::Status status = db_->Put(rocksdb::WriteOptions(), request->key(), request->value());
                if (status.ok()) {
                    response->set_result("OK");
                } else {
                    response->set_result(status.ToString());
                }
                break;
            }
            case OperationRequest::GET: {
                std::string value;
                rocksdb::Status status = db_->Get(rocksdb::ReadOptions(), request->key(), &value);
                if (status.ok()) {
                    response->set_result(value);
                } else {
                    response->set_result(status.ToString());
                }
                break;
            }
            case OperationRequest::DELETE: {
                rocksdb::Status status = db_->Delete(rocksdb::WriteOptions(), request->key());
                if (status.ok()) {
                    response->set_result("OK");
                } else {
                    response->set_result(status.ToString());
                }
                break;
            }
            case OperationRequest::SCAN: {
                std::unique_ptr<rocksdb::Iterator> it(db_->NewIterator(rocksdb::ReadOptions()));
                std::string result;
                // Note: This has not been implemented yet. There is nothing from the request yet.
                for (it->SeekToFirst(); it->Valid(); it->Next()) {
                    result += it->key().ToString() + ": " + it->value().ToString() + "\n";
                }
                response->set_result(result);
                break;
            }
            default:
                response->set_result("Unknown operation");
        }
        return Status::OK;
    }

private:
    rocksdb::DB* db_;
};

void RunServer(const std::string& server_address, const std::string& db_path, int thread_pool_size) {
    NetServiceImpl service(db_path);
    
    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    // Create and attach a thread pool to the server
    std::shared_ptr<grpc::ThreadPoolInterface> thread_pool = grpc::CreateDefaultThreadPool(thread_pool_size);
    builder.SetThreadPool(thread_pool);

    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;
    server->Wait();
}


// An additional UDP server to constantly listen for Optimization requests.
void RunUDPServer(const std::string& server_address) {
    int sockfd; 
    char buffer[1024]; 
    struct sockaddr_in servaddr, cliaddr; 
      
    sockfd = socket(AF_INET, SOCK_DGRAM, 0); 
    if (sockfd < 0) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
      
    memset(&servaddr, 0, sizeof(servaddr)); 
    memset(&cliaddr, 0, sizeof(cliaddr)); 
      
    servaddr.sin_family = AF_INET; 
    servaddr.sin_addr.s_addr = INADDR_ANY; 
    servaddr.sin_port = htons(8080); 
      
    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) { 
        perror("bind failed"); 
        exit(EXIT_FAILURE); 
    }

    while (true) {
        senderAddrSize = sizeof(senderAddr);
        bytesReceived = recvfrom(serverSocket, buffer, sizeof(buffer), 0, (struct sockaddr *)&senderAddr, &senderAddrSize);
        if (bytesReceived < 0) {
            std::cerr << "Error receiving data." << std::endl;
            continue;
        }

        optimizationQueue.push(buffer);
        std::cout << "Received data: " << buffer << std::endl;
    }
 
    close(sockfd); 
    return;
}

void RunOptimizationService() {
    while (true) {
        if (!optimizationQueue.empty()) {
            std::string data = optimizationQueue.front();
            optimizationQueue.pop();
            std::cout << "Processing data: " << data << std::endl;
        }
    }
}


int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <server_address> <db_path> <thread_pool_size>" << std::endl;
        return 1;
    }
    std::string server_address(argv[1]);
    std::string db_path(argv[2]);
    int thread_pool_size = std::stoi(argv[3]);
 
    // Create a thread to run the UDP server
    std::thread udp_server(RunUDPServer);
    udp_server.detach();

    // Run the Optimization service
    std::thread optimization_service(RunOptimizationService);
    optimization_service.detach();

    // Run the gRPC server
    RunServer(server_address, db_path, thread_pool_size);

    return 0;
}
