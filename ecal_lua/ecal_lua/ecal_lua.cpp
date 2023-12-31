#include <ecal/ecal.h>
#include <ecal/msg/string/publisher.h>
#include <ecal/msg/protobuf/publisher.h>

#include <iostream>
#include <thread>

#include "lua.hpp"

#include "ecal_com.h"

#define LUA_ON_INIT_FUNCTION        "on_init"
#define LUA_ON_RUN_FUNCTION         "on_run"
#define LUA_ON_END_FUNCTION         "on_end"

int main(int argc, char** argv)
{
    lua_State* L;
    L = luaL_newstate();
    luaL_openlibs(L);

    eCAL_Com ecal_com = eCAL_Com();
    eCAL::Initialize(argc, argv, "lua_interpreter");

    ecal_com.init();

    while (eCAL::Ok())
    {

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }


    // finalize eCAL API

    eCAL::Finalize();
 
}