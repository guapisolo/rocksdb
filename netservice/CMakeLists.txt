cmake_minimum_required(VERSION 3.8)
set(CMAKE_CXX_STANDARD 17)

# Project name
project(netservice C CXX)

# Setup Paths for Protobuf and Hadoop
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

# CMake Related options
set(CMAKE_COMPILE_WARNING_AS_ERROR OFF)
set(CMAKE_BUILD_TYPE RelWithDebInfo)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ------------------------------------------------------------------------------
# Protobuf
set(protobuf_MODULE_COMPATIBLE TRUE)
find_package(Protobuf CONFIG REQUIRED)
message(STATUS "Using protobuf ${protobuf_VERSION}")

set(_PROTOBUF_LIBPROTOBUF protobuf::libprotobuf)
set(_REFLECTION gRPC::grpc++_reflection)

# Protobuf-compiler
set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)

# gRPC
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")
set(_GRPC_GRPCPP gRPC::grpc++)
set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>)

# Proto file
get_filename_component(ns_proto "./netservice.proto" ABSOLUTE)
get_filename_component(ns_proto_path "${ns_proto}" PATH)

# ------------------------------------------------------------------------------
# Generated sources
set(ns_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/netservice.pb.cc")
set(ns_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/netservice.pb.h")
set(ns_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/netservice.grpc.pb.cc")
set(ns_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/netservice.grpc.pb.h")

add_custom_command(
      OUTPUT "${ns_proto_srcs}" "${ns_proto_hdrs}" "${ns_grpc_srcs}" "${ns_grpc_hdrs}" "${ns_client_src}" "${ns_client_hdr}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${ns_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${ns_proto}"
      DEPENDS "${ns_proto}")

# Include generated *.pb.h files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# ------------------------------------------------------------------------------
# Source code files
set(ns_servers_src "${CMAKE_CURRENT_SOURCE_DIR}/rdb_server.cc")

# netservice
add_library(netservice
  ${ns_grpc_srcs}
  ${ns_grpc_hdrs}
  ${ns_proto_srcs}
  ${ns_proto_hdrs})

target_link_libraries(netservice
  absl::check
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

# Targets rdb_[async_](client|server)
# foreach(_target
#   rdb_server)
#   add_executable(${_target} "${_target}.cc")
#   target_link_libraries(${_target}
#     netservice
#     absl::check
#     absl::flags
#     absl::flags_parse
#     absl::log
#     ${_REFLECTION}
#     ${_GRPC_GRPCPP}
#     ${_PROTOBUF_LIBPROTOBUF})
# endforeach()

# add_executable(rdb_client rdb_client.cc)
