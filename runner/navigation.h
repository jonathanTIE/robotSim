#pragma once

#include <ecal/msg/protobuf/publisher.h>
#include <game_actions.pb.h>
typedef struct {
	float x;
	float y;
	float theta;
} pose_t;

class Navigation {
public:
	Navigation();
	void init();
	void set_pose(pose_t* pose);
	pose_t get_current_pose();
	void overwrite_current_pose(pose_t* pose);
	void stop_motion();
	bool is_motion_done();
	bool is_blocked();
	void update(int dt_ms);

private:
	int64_t lapsed_time;
	eCAL::protobuf::CPublisher<game_actions::get_pose_out> pose_pub;
	pose_t target;
	pose_t current_pose;
};