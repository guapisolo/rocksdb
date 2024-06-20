cmake_minimum_required(VERSION 3.4)

# Setup Paths for Protobuf and Hadoop
if(NOT DEFINED ENV{Protobuf_DIR})
  set(Protobuf_DIR /data/viraj/projects/network-project/protobuf-3.7-src/)
else()
  set(Protobuf_DIR $ENV{Protobuf_DIR})
endif()

# Protobuf
set(protobuf_MODULE_COMPATIBLE TRUE)
find_package(Protobuf CONFIG REQUIRED PARENT_SCOPE)
message(STATUS "Using protobuf ${protobuf_VERSION}")

set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
set(_REFLECTION gRPC::grpc++_reflection)

# gRPC
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")
set(_GRPC_GRPCPP gRPC::grpc++)

set(netservice_SOURCES "rdb_client.cc" "rdb_server.cc" PARENT SCOPE)
set(netservice_LIBS "netservice" "dl" "verify" ${_REFLECTION} ${_GRPC_GRPCPP} ${_PROTOBUF_LIBPROTOBUF} PARENT_SCOPE)
set(netservice_INCLUDE_PATHS "$ENV{NETSERVICE_PATH}" "$ENV{NETSERVICE_PATH}/build" PARENT_SCOPE)
set(netservice_LINK_PATHS "$ENV{NETSERVICE_PATH}/build" PARENT_SCOPE)
