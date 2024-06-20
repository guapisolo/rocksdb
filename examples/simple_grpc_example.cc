// Copyright (c) 2011-present, Facebook, Inc.  All rights reserved.
//  This source code is licensed under both the GPLv2 (found in the
//  COPYING file in the root directory) and Apache 2.0 License
//  (found in the LICENSE.Apache file in the root directory).

#include <cstdio>
#include <string>

#include "plugin/netservice/rdb_client.h"

int main() {
    std::string server_address = "0.0.0.0:50050";
    
    // To be supplied by the benchmark
    std::string operation = "PUT";
    std::string key_prefix = "key";
    std::string value_prefix = "value";

    // Loop 1000000 times
    for (int i = 0; i < 1000000; i++) {
        std::string key = key_prefix + std::to_string(i);
        std::string value = value_prefix + std::to_string(i);

        NetClient client(grpc::CreateChannel(server_address, grpc::InsecureChannelCredentials()));

        std::string result;
        result = client.OperationService(operation, key, value);

        std::cout << "Result: " << result << std::endl;
    }

    return 0;
}