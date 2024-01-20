#include "navigation.h"

#include <thread>



Navigation::Navigation() {

}

void Navigation::init() {
	pose_pub = eCAL::protobuf::CPublisher<game_actions::get_pose_out>("get_pose");
	std::cout << "init nav" << std::endl;
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
	current_pose = *pose;
	update(0); //force update to send the new pose through eCAL
}

void Navigation::stop_motion()
{
}

bool Navigation::is_motion_done()
{
	return false;
}

bool Navigation::is_blocked()
{
	return false;
}

void Navigation::update(int dt_ms) {
	lapsed_time+=dt_ms;
	if (lapsed_time > 500 && lapsed_time < 10000) {
		lapsed_time = 10000;
		current_pose = target;
	}
	game_actions::get_pose_out pose_out;
	pose_out.set_x(current_pose.x);
	pose_out.set_y(current_pose.y);
	pose_out.set_theta(current_pose.theta);
	pose_pub.Send(pose_out);
}