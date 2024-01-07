# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.8)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("runner")


set(CMAKE_CXX_STANDARD 14)
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# ECAL
find_package(eCAL REQUIRED)
find_package(Protobuf REQUIRED)

# Protobuf
set(protobuf_files 
    ${CMAKE_CURRENT_SOURCE_DIR}/../proto/game_actions.proto
)

# Add source to this project's executable.
#include_directories(${CMAKE_CURRENT_BINARY_DIR})
#protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${protobuf_files})
 

# Add source to this project's executable.
#add_executable (ecal_lua ${PROTO_SRCS} ${PROTO_HDRS} "ecal_lua.cpp" "ecal_lua.h"  "ecal_functions.cpp" "ecal_functions.h" )
add_executable (runner "runner.cpp" "navigation.h" "navigation.cpp" "game_actions_lua.h" "game_actions_lua.cpp" "game_actions.h" "game_actions.cpp" "simu_avoidance.h" "simu_avoidance.cpp"  "simu_core.h" "simu_core.cpp")
add_executable (protogen "protogen.cpp" "protogen.h")

PROTOBUF_TARGET_CPP(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/../proto ${protobuf_files})

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET runner PROPERTY CXX_STANDARD 20)
endif()

target_link_libraries(${PROJECT_NAME}

  eCAL::core 
  protobuf::libprotobuf

)

add_subdirectory(lua)
target_link_libraries(runner lua_static)