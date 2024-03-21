config = {}

config.MATCH_DURATION_MS = 87000
config.DEFAULT_LOOP_PERIOD_MS = 50


config.ENNEMY_RADIUS_MM = 200
config.SCAN_DURATION_MS = 330 -- 30ms margin

config.US_DECAY_TIME_MS = 500 -- US reading is invalid after 500ms

config.OVERSHOOT_MM = 100 -- distance to overshoot when sticking to wall
config.ROBOT_CENTER_Y_BOTTOM = 200 -- distance wall/center robot when following bottom wall

config.PANEL_ARM_TIMEOUT_MS = 250

config.theta_pince_mur = -0.52359877559
return config