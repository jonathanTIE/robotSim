﻿#include <ecal/ecal.h>
#include <ecal/msg/string/subscriber.h>

#include <iostream>
#include <thread>

#include "lua.hpp"

#include "game_actions_lua.h"
#include "simu_core.h"

#define LUA_ON_INIT_FUNCTION        "on_init"
#define LUA_ON_RUN_FUNCTION         "on_run"
#define LUA_ON_END_FUNCTION         "on_end"
#define RUN_DURATION               90000 //90s

bool lua_ready_to_run = false;
bool is_running = false;
bool is_end = false;
uint64_t run_end_time_ms = 0;


uint64_t time() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

int lua_loader(lua_State* L, const char* path) {
    if (luaL_loadfile(L, path) != LUA_OK)
    {
        std::cout << "Error loading file: " << lua_tostring(L, -1) << std::endl;
        return 1;
    }
    if (lua_pcall(L, 0, LUA_MULTRET, 0) != LUA_OK) {
        std::cout << "Error running file: " << lua_tostring(L, -1) << std::endl;
    }
    lua_getglobal(L, LUA_ON_INIT_FUNCTION);
    lua_call(L, 0, 0);

    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    lua_getglobal(L, LUA_ON_RUN_FUNCTION);
    lua_ready_to_run = true;
    return 0;
}

int main(int argc, char** argv)
{
    //Lua init
    lua_State* L;
    L = luaL_newstate();
    luaL_openlibs(L);

    register_lua_functions(L);
    lua_loader(L, (char *) "D:/Sync/Code/Robotique/CDR2024/robotSim/ecal_lua/ecal_lua/main.lua");

    //eCAL init
    eCAL::Initialize(argc, argv, "lua_interpreter");
    eCAL::string::CSubscriber<std::string> sub("lua_path_loader");

    auto callback = [&](const std::string& path) {
        lua_loader(L, path.c_str());
    };
    sub.AddReceiveCallback(std::bind(callback, std::placeholders::_2));


    while (eCAL::Ok())
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        if (lua_ready_to_run && !is_running) {
            lua_getglobal(L, LUA_ON_RUN_FUNCTION);
            lua_call(L, 0, 0);
            run_end_time_ms = time() + RUN_DURATION;
            is_running = true;
        }
        if (lua_ready_to_run && time() > run_end_time_ms && !is_end) {
			lua_getglobal(L, LUA_ON_END_FUNCTION);
			lua_call(L, 0, 0);
            is_end = true;
		}

    }


    // finalize eCAL API

    eCAL::Finalize();
 
}