#include <ecal/ecal.h>
#include <ecal/msg/string/publisher.h>
#include <ecal/msg/protobuf/publisher.h>

#include "lua.hpp"

#include <iostream>
#include <thread>

#include "messages.pb.h"

#define LUA_ON_INIT_FUNCTION        "on_init"
#define LUA_ON_RUN_FUNCTION         "on_run"
#define LUA_ON_END_FUNCTION         "on_end"

int main(int argc, char** argv)

{
    lua_State* L;
    L = luaL_newstate();
    luaL_openlibs(L);

    eCAL::Initialize(argc, argv, "lua_interpreter");
    eCAL::protobuf::CPublisher<messages::Position> publisher("hello_world_protobuf");

    // Create a String Publisher that publishes on the topic "hello_world_topic"


    // Create a counter, so something changes in our message

    int counter = 0;


    // Infinite loop (using eCAL::Ok() will enable us to gracefully shutdown the

    // Process from another application)

    while (eCAL::Ok())

    {

        // Create a message with a counter an publish it to the topic

        //messages::Position msg;
        //msg.set_x(1.0);
        //msg.set_y(2.0);
        //msg.set_theta(3.0);
        //publisher.Send(msg);


        // Sleep 500 ms

        std::this_thread::sleep_for(std::chrono::milliseconds(500));

    }


    // finalize eCAL API

    eCAL::Finalize();
 
}