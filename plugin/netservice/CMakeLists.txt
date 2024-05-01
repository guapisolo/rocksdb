cmake_minimum_required(VERSION 3.8)
set(CMAKE_CXX_STANDARD 17)

# Paths
if(NOT DEFINED ENV{Protobuf_DIR})
  set(Protobuf_DIR /data/viraj/projects/network-project/protobuf-3.7-src/)
else()
  set(Protobuf_DIR $ENV{Protobuf_DIR})
endif()

if(NOT DEFINED ENV{HADOOP_HOME})
  set(HADOOP_HOME /data/viraj/projects/network-project/codebase/work-env/hadoop-op-aware/hadoop-dist/target/hadoop-3.3.1/)
else()
  set(HADOOP_HOME $ENV{HADOOP_HOME})
endif()

# Project name
project(NetService C CXX)

# Protobuf
set(protobuf_MODULE_COMPATIBLE TRUE)
find_package(Protobuf CONFIG REQUIRED)
message(STATUS "Using protobuf ${protobuf_VERSION}")

# Protobuf-compiler
set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)

# gRPC
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")
set(_GRPC_GRPCPP gRPC::grpc++)
set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>)

# RocksDB
add_library(rocksdb STATIC IMPORTED)
set_target_properties(rocksdb PROPERTIES IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/../../librocksdb.a)
link_libraries(lz4 snappy bz2)

# HDFS
add_library(hdfs STATIC IMPORTED)
set_target_properties(hdfs PROPERTIES IMPORTED_LOCATION ${HADOOP_HOME}/lib/native/libhdfs.so)
link_directories(${HADOOP_HOME}/lib/native)

# Proto file
get_filename_component(ns_proto "./netservice.proto" ABSOLUTE)
get_filename_component(ns_proto_path "${ns_proto}" PATH)

# Generated sources
set(ns_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/netservice.pb.cc")
set(ns_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/netservice.pb.h")
set(ns_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/netservice.grpc.pb.cc")
set(ns_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/netservice.grpc.pb.h")
add_custom_command(
      OUTPUT "${ns_proto_srcs}" "${ns_proto_hdrs}" "${ns_grpc_srcs}" "${ns_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${ns_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${ns_proto}"
      DEPENDS "${ns_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# ns_grpc_proto
add_library(ns_grpc_proto
  ${ns_grpc_srcs}
  ${ns_grpc_hdrs}
  ${ns_proto_srcs}
  ${ns_proto_hdrs})
target_link_libraries(ns_grpc_proto
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Targets rdb_[async_](client|server)
foreach(_target
  rdb_client rdb_server)
  add_executable(${_target} "${_target}.cc")
  target_link_libraries(${_target}
    ns_grpc_proto
    ${_REFLECTION}
    ${_GRPC_GRPCPP}
    ${_PROTOBUF_LIBPROTOBUF}
    rocksdb
    hdfs)
  target_include_directories(${_target} 
    PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/../../include
    ${HADOOP_HOME}/include)
endforeach()