#include "game_actions_ecal.h"

eCAL_Com::eCAL_Com()
{
}

eCAL_Com::~eCAL_Com()
{
}


void eCAL_Com::init()
{
	eCAL::SDataTypeInformation topic_info;
	// Generate all publishers
	#define X(action_name, function, ARGUMENTS, OUTPUT) \
		topic_info = eCAL::SDataTypeInformation(); \
		topic_info.encoding = "proto"; \
		topic_info.name = game_actions::action_name##_args().GetTypeName(); \
		publishers[#action_name] = eCAL::CPublisher(#action_name, topic_info); \
		if (game_actions::action_mname##_out().GetDescriptor()->field_count() != 0 ) { \
			is_client_method[#action_name] = true; \
		}

	DEFINE_GAME_ACTION_FUNCTIONS
	#undef X

}


