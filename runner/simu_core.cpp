#include "simu_core.h"

Navigation nav = Navigation();

void init(pose_t* init_pose) {
	nav.init();
	nav.set_pose(init_pose);
}
void update(int dt_ms) {
	nav.update(dt_ms);
}