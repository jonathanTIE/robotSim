# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.8)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("ecal_lua")

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# ECAL
find_package(eCAL REQUIRED)
find_package(Protobuf REQUIRED)

# Protobuf
set(protobuf_files 
    ${CMAKE_CURRENT_SOURCE_DIR}/ecal_lua/proto_messages/game_actions.proto
)
# Include sub-projects.
add_subdirectory ("ecal_lua")
