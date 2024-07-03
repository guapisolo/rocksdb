netservice_SOURCES = rdb_client.cc rdb_server.cc
netservice_HEADERS = rdb_client.h
netservice_CXXFLAGS = -I${NETSERVICE_PATH}
netservice_LDFLAGS = -L${NETSERVICE_PATH} -lnetservice