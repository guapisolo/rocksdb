#include <iostream>
#include <string>

#include "rdb_client.h"

std::string kDBPath = "test/rdb_hdfs";

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
