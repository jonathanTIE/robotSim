#include <ecal/ecal.h>
#include <ecal/msg/protobuf/publisher.h>
#include <ecal/msg/protobuf/subscriber.h>
#include <google/protobuf/message.h>

#include <map>

#include "ecal_com.h"
#include "game_actions.pb.h"



eCAL_Com::eCAL_Com()
{
}

eCAL_Com::~eCAL_Com()
{
}


void eCAL_Com::init()
{
	std::map<std::string, eCAL::protobuf::CPublisher<google::protobuf::Message>> publishers;
	//std::map<std::string, eCAL::protobuf::CSubscriber<google::protobuf::Message>> subscribers;

	// Generate all publishers and subscribers where there is at least one field defined in the protobuf message
	#define X(action_name, function, ARGUMENTS, OUTPUT) \
		if(game_actions::action_name##_args().GetDescriptor()->field_count() != 0) { \
			eCAL::protobuf::CPublisher<game_actions::action_name##_args> publisher(#action_name); \
		} \
		if (game_actions::action_name##_out().GetDescriptor()->field_count() != 0 ) { \
			eCAL::protobuf::CSubscriber<game_actions::action_name##_out> subscriber(std::string(#action_name) + std::string("_out")); \
		}

	DEFINE_GAME_ACTION_FUNCTIONS



	//			publishers[#action_name] = publisher; \
	//			subscribers[#action_name#+"_out"] = subscriber; \
	#undef X
	//eCAL::Initialize(argc, argv, "lua_interpreter");
	//eCAL::protobuf::CPublisher<messages::Position> publisher("hello_world_protobuf");
}


