# CMakeList.txt : CMake project for ecal_lua, include source and define
# project specific logic here.
#

# Add source to this project's executable.
#include_directories(${CMAKE_CURRENT_BINARY_DIR})
#protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${protobuf_files})
 

# Add source to this project's executable.
#add_executable (ecal_lua ${PROTO_SRCS} ${PROTO_HDRS} "ecal_lua.cpp" "ecal_lua.h"  "ecal_functions.cpp" "ecal_functions.h" )
add_executable (ecal_lua  "ecal_lua.cpp" "game_actions_ecal.cpp" "game_actions_ecal.h" "game_actions_lua.h" "game_actions_lua.cpp")
add_executable (protogen "protogen.cpp" "protogen.h")

PROTOBUF_TARGET_CPP(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/proto_messages ${protobuf_files})

target_link_libraries(${PROJECT_NAME}

  eCAL::core
  protobuf::libprotobuf

)

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET ecal_lua PROPERTY CXX_STANDARD 20)
endif()

add_subdirectory(lua)
target_link_libraries(ecal_lua lua_static)
 
# TODO: Add tests and install targets if needed.
       