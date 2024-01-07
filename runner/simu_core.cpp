#include "simu_core.h"

Navigation nav = Navigation();

void init(pose_t* init_pose) {
	nav.init();
	nav.overwrite_current_pose(init_pose);
	nav.set_pose(init_pose); //prevent the robot from going to 0,0,0
}
void update(int dt_ms) {
	nav.update(dt_ms);
}