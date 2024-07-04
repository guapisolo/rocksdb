#include <iostream>
#include <memory>
#include <string>
#include <thread>

// GRPC
#include <grpcpp/grpcpp.h>
#include "netservice.grpc.pb.h"

// RocksDB
#include "rocksdb/cache.h"
#include "rocksdb/compaction_filter.h"
#include "rocksdb/db.h"
#include "rocksdb/options.h"
#include "rocksdb/slice.h"
#include "rocksdb/table.h"
#include "rocksdb/utilities/options_util.h"

// HDFS + RocksDB-HDFS Plugin
#include "plugin/hdfs/env_hdfs.h"
#include "hdfs.h"

// UDP
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
using grpc::ServerReader;
using grpc::ServerWriter;
using grpc::ServerReaderWriter;

using netservice::OperationRequest;
using netservice::OperationResponse;
using netservice::NetService;

using ROCKSDB_NAMESPACE::BlockBasedTableOptions;
using ROCKSDB_NAMESPACE::ColumnFamilyDescriptor;
using ROCKSDB_NAMESPACE::ColumnFamilyHandle;
using ROCKSDB_NAMESPACE::ColumnFamilyOptions;
using ROCKSDB_NAMESPACE::CompactionFilter;
using ROCKSDB_NAMESPACE::ConfigOptions;
using ROCKSDB_NAMESPACE::DB;
using ROCKSDB_NAMESPACE::DBOptions;
using ROCKSDB_NAMESPACE::NewLRUCache;
using ROCKSDB_NAMESPACE::Options;
using ROCKSDB_NAMESPACE::Slice;

// queue shared across multiple thread
std::queue<std::string> optimizationQueue;

class NetServiceImpl final : public NetService::Service {
public:
    NetServiceImpl(const std::string& db_path) {
        Options options;
        options.create_if_missing = true;
        // Load options from a file
        ConfigOptions config_options;
        std::vector<ColumnFamilyDescriptor> cf_descs;

        rocksdb::Status status = rocksdb::LoadOptionsFromFile(config_options, "../db_bench_options.ini", &options, &cf_descs);

        std::unique_ptr<rocksdb::Env> hdfs;
        rocksdb::NewHdfsEnv("hdfs://localhost:9000/", &hdfs);

        options.env = hdfs.get();

        status = DB::Open(options, db_path, &db_);
        if (!status.ok()) {
            std::cerr << "Error opening database: " << status.ToString() << std::endl;
            exit(1);
        }
    }

    ~NetServiceImpl() {
        delete db_;
    }

    Status OperationService(ServerContext* context,
                            ServerReader<OperationRequest>* stream, OperationResponse* response) override {
        OperationRequest request;

        while (stream->Read(&request)) {
            switch (request.operation()) {
                case OperationRequest::Put: {
                    rocksdb::Status status = db_->Put(rocksdb::WriteOptions(), request.keys(0), request.values(0));
                    if (status.ok()) {
                        response->set_result("OK");
                    } else {
                        response->set_result(status.ToString());
                    }
                    break;
                }
                case OperationRequest::BatchPut: {
                    rocksdb::WriteBatch batch;
                    for (int i = 0; i < request.keys_size(); i++) {
                        batch.Put(request.keys(i), request.values(i));
                    }
                    rocksdb::Status status = db_->Write(rocksdb::WriteOptions(), &batch);
                    printf("BatchPut status: %s\n", status.ToString().c_str());
                    if (status.ok()) {
                        response->set_result("OK");
                    } else {
                        response->set_result(status.ToString());
                    }
                    break;
                }
                case OperationRequest::Get: {
                    std::string value;
                    rocksdb::Status status = db_->Get(rocksdb::ReadOptions(), request.keys(0), &value);
                    if (status.ok()) {
                        response->set_result(value);
                    } else {
                        response->set_result(status.ToString());
                    }
                    break;
                }
                case OperationRequest::Delete: {
                    rocksdb::Status status = db_->Delete(rocksdb::WriteOptions(), request.keys(0));
                    if (status.ok()) {
                        response->set_result("OK");
                    } else {
                        response->set_result(status.ToString());
                    }
                    break;
                }
                default:
                    response->set_result("Unknown operation");
            }
        }

        // This bit effectively is useless for now
        // stream->Write(response);
        fprintf(stderr, "Response: %s\n", response->result().c_str());
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
    // std::shared_ptr<grpc::ThreadPoolInterface> thread_pool = grpc::CreateDefaultThreadPool(thread_pool_size);
    // builder.SetThreadPool(thread_pool);

    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << server_address << std::endl;
    server->Wait();
}


// An additional UDP server to constantly listen for Optimization requests.
void RunUDPServer() {
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
        socklen_t cliAddrSize = sizeof(cliaddr);
        int bytesReceived = recvfrom(sockfd, buffer, sizeof(buffer), 0, (struct sockaddr *)&cliaddr, &cliAddrSize);
        if (bytesReceived < 0) {
            std::cerr << "Error receiving data." << std::endl;
            continue;
        }

        buffer[bytesReceived] = '\0';
        optimizationQueue.push(buffer);
        std::cout << "Received data: " << buffer << std::endl;
        buffer[0] = '\0';
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

int main() {
    std::string server_address = "0.0.0.0:50050";
    std::string db_path = "/data/viraj/tmp_db";
    int thread_pool_size = 10;
 
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
