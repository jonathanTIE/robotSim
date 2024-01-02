#include "simu_navigation.h"

#include <thread>

uint64_t temp_time() {
	using namespace std::chrono;
	return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
}

void Navigation::set_pose(pose_t* pose)
{
	target = *pose;
	lapsed_time = 0;
}

pose_t Navigation::get_current_pose()
{
	return current_pose;
}

void Navigation::overwrite_current_pose(pose_t* pose)
{
}

void Navigation::stop_motion()
{
}

bool Navigation::is_motion_done()
{
	return false;
}

void Navigation::update(int dt_ms) {
	eCAL::protobuf::CPublisher<game_actions::get_pose_args> pose_pub("get_pose");
	lapsed_time+=dt_ms;
	if (lapsed_time > 500 && lapsed_time < 10000) {
		lapsed_time = 10000;
		current_pose = target;
	}
}