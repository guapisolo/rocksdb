# Network-Based Service for RocksDB

This plugin provides a network-based service for RocksDB. It allows you to access RocksDB over the network using a simple protocol. The service is implemented using gRPC.

## Building

1. Install the gRPC C++ library. You can find instructions [here](https://grpc.io/docs/languages/cpp/quickstart/)
2. Build RocksDB with a simple `make static_lib` command in the parent directory.
3. Build the plugin:
    ```bash
    mkdir build
    cd build
    cmake ..
    make
    ```
4. The plugin will be built in the `build` directory. Run `./rdb_server` on the server side and `./rdb_client` on the client side.
