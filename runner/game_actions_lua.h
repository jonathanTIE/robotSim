#pragma once

#include "lua.hpp"
#include "game_actions.h"
#include <ecal/ecal_service_info.h>
#include <chrono>

uint64_t get_time();
void register_lua_functions(lua_State* L);