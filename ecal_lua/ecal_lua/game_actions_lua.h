#pragma once

#include "lua.hpp"
#include "game_actions.h"
#include "game_actions_ecal.h"
#include <ecal/ecal_service_info.h>

void register_lua_functions(lua_State* L);