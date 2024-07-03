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
set(ns_proto_srcs "netservice.pb.cc")
set(ns_proto_hdrs "netservice.pb.h")
set(ns_grpc_srcs "netservice.grpc.pb.cc")
set(ns_grpc_hdrs "netservice.grpc.pb.h")

add_custom_command(
      OUTPUT "${ns_proto_srcs}" "${ns_proto_hdrs}" "${ns_grpc_srcs}" "${ns_grpc_hdrs}"
      COMMAND ${_PROTOBUF_PROTOC}
      ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
        --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
        -I "${ns_proto_path}"
        --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
        "${ns_proto}"
      DEPENDS "${ns_proto}")

# ------------------------------------------------------------------------------
# netservice
add_library(netservice SHARED
  ${ns_grpc_srcs}
  ${ns_grpc_hdrs}
  ${ns_proto_srcs}
  ${ns_proto_hdrs})

target_link_libraries(netservice
  absl::check
  ${_REFLECTION}
  ${_GRPC_GRPCPP}
  ${_PROTOBUF_LIBPROTOBUF})

if(MSVC)
  target_compile_options(netservice PRIVATE /W4 /WX)
else()
  target_compile_options(netservice PRIVATE -Wall -Wextra -pedantic)
endif()

target_include_directories(netservice INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# ------------------------------------------------------------------------------
install(TARGETS netservice 
        DESTINATION lib)

install(FILES
  ${ns_proto_hdrs}
  ${ns_grpc_hdrs}
  DESTINATION include/netservice)
