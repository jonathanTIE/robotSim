#pragma once

#include <ecal/msg/protobuf/publisher.h>

#include "simu_avoidance.h"
#include "simu_navigation.h"
#include "game_actions.pb.h"

extern Navigation nav;

void init(pose_t init_pose);
void update(int dt_ms);