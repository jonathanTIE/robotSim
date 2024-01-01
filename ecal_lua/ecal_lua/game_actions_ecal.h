#pragma once
#include <ecal/ecal.h>
#include <ecal/ecal_types.h>
#include <ecal/msg/publisher.h>
#include <ecal/ecal_client.h>

#include <map>
#include <unordered_map>

#include "game_actions.h"
#include "game_actions.pb.h"
#include <google/protobuf/message.h>

class eCAL_Com
{

	public:
		eCAL_Com();
		~eCAL_Com();
		void init();

		//Publishers & clients - Every lua function have a publisher (for monitoring purposes), some also use the client (if return values)
		// When there is a client, both publisher & client are sending the message. (Not where there is only publisher to avoid blocking service call from client)
		typedef std::unordered_map<std::string, eCAL::CPublisher> PublisherMap;
		PublisherMap publishers;
		typedef std::unordered_map<std::string, bool> IsValidMap;
		IsValidMap is_client_method;
		eCAL::CServiceClient service_client = eCAL::CServiceClient("lua_interpreter");




};