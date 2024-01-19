#include <ecal/ecal.h>
#include <ecal/msg/string/subscriber.h>
#include <ecal/msg/protobuf/subscriber.h>

#include <iostream>
#include <thread>

#include "lua.hpp"

#include "game_actions_lua.h"
#include "simu_core.h"

#define LUA_ON_INIT_FUNCTION        "on_init"
#define LUA_RESUME_LOOP_FUNCTION    "resume_loop"
#define RUN_DURATION               900 //0.90s currently

bool lua_ready_to_run = false;
bool is_running = false;
bool is_end = false;
uint64_t run_end_time_ms = 0;


uint64_t time() {
    using namespace std::chrono;
    return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

int lua_loader(lua_State* &L, const char* path, bool is_reversed) {
    std::cout << "Loading lua file: " << path << std::endl;
    lua_State* new_L;
    new_L = luaL_newstate();
    L = new_L;
    luaL_openlibs(L);

    register_lua_functions(L);

    if (luaL_loadfile(L, path) != LUA_OK)
    {
        std::cout << "Error loading file: " << lua_tostring(L, -1) << std::endl;
        return 1;
    }
    if (lua_pcall(L, 0, LUA_MULTRET, 0) != LUA_OK) {
        std::cout << "Error running file: " << lua_tostring(L, -1) << std::endl;
    }
    lua_getglobal(L, LUA_ON_INIT_FUNCTION);
    lua_pushboolean(L, *((int*)is_reversed));

    if (lua_pcall(L, 1, LUA_MULTRET, 0) != LUA_OK) {
        std::cout << "Lua error on_init: " << lua_tostring(L, -1) << std::endl;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    lua_ready_to_run = true;
    return 0;
}

int main(int argc, char** argv)
{
    //Lua init
    lua_State* L;

    //eCAL init
    eCAL::Initialize(argc, argv, "lua_interpreter");
    eCAL::string::CSubscriber<std::string> sub("lua_path_loader");
    eCAL::string::CSubscriber<std::string> sub_side("side");

    //Var inits
    bool is_reversed = false;

    //eCAL subscriptions

    auto callback = [&](const std::string& path) {
        lua_loader(L, path.c_str(), is_reversed);
    };
    sub.AddReceiveCallback(std::bind(callback, std::placeholders::_2));

    auto callback_side = [&](const std::string& side) {
        if (side == "right") {
			is_reversed = true;
		}
        else if(side == "left"){
			is_reversed = false;
		}
        else {
            std::cout << "Error: side not recognized" << std::endl;
	    };
	};
    sub_side.AddReceiveCallback(std::bind(callback_side, std::placeholders::_2));

    //Simulation init
    pose_t pose = { 100.0, 1000.0 ,0.0001 };
    init(&pose);

    //TODO : temp
    lua_loader(L, "D:/Sync/Code/Robotique/CDR2024/robotSim/lua_scripts/main2.lua", is_reversed);

    while (eCAL::Ok())
    {
        //Lua 
        if (!lua_ready_to_run) {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            continue;
        }
        else {
            lua_getglobal(L, LUA_RESUME_LOOP_FUNCTION);
            lua_pushinteger(L, time());

            //arg is the timestamp in ms, receive the sleep time to wait before calling the coroutine again
            if (lua_pcall(L, 1, 1, 0) != LUA_OK) { //It either returns an error message or the sleep time
                std::cout << "error on main_loop: " << lua_tostring(L, -1) << std::endl;
            }
            else {
                lua_Integer sleep_time = lua_tointeger(L, -1);
                std::this_thread::sleep_for(std::chrono::milliseconds(sleep_time));
                update(sleep_time);
            }
        }

    }


    // finalize eCAL API

    eCAL::Finalize();
 
}