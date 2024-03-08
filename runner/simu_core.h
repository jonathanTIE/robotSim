#pragma once

#include <ecal/msg/protobuf/publisher.h>

#include "navigation.h"
#include "game_actions.pb.h"

extern Navigation nav;
extern int us_channels[10];

void init(pose_t* init_pose);
void update(int dt_ms);