path_settings = {}

path_settings.table_coordinates = {
    INI = {x=280, y= 160}, -- starting position
    S6 = {x=2000, y=200}, -- 6th solar panel
    S1 = {x=250, y=150}, -- 1st solar panel
    S1EO = {x=450, y=0}, -- End 1st solar panel with Overshoot
    S1ER = {x = 450, y=120}, -- End 1st solar panel with Recalage

    A8 = {x=500, y=400},  -- Aruco bottom left corner (~8 o'clock)
    P6B = {x=1500, y=400}, -- Plant 6, bottom (6 o'clock)

    P11B = {x=900, y=530},
    AML = {x=700, y=1000}, -- Aruco Middle Left (between the two arucos)

    FAPT = { x = 250, y = 1800} -- Final Approach Point (home Top)


}

-- TODO EDGES !!!
path_settings.edges = {
    INI = {"S6", "A8"},
    S6 = { "INI", "P6B"},
    A8 = {"INI", "P6B"},
    P6B = {"S6", "A8"},
}


config = {}

config.MATCH_DURATION_MS = 87000
config.DEFAULT_LOOP_PERIOD_MS = 50


config.ENNEMY_RADIUS_MM = 200
config.SCAN_DURATION_MS = 330 -- 30ms margin

config.US_DECAY_TIME_MS = 500 -- US reading is invalid after 500ms

config.STEP_DISTANCE = 60 -- mm, increment between each "jump" at wall following
config.OVERSHOOT_MM = 100 -- distance to overshoot when sticking to wall
config.OVERSHOOT_THETA = 0.1 -- rad
config.ROBOT_CENTER_Y_BOTTOM = 200 -- distance wall/center robot when following bottom wall
config.DIST_BEF_ARM = 100 --mm , distance before placing arm on panel

config.PANEL_ARM_TIMEOUT_MS = 250

config.theta_pince_mur = -0.52359877559
config.pi = 3.14159265359



local utils = {}

-- VARIABLES --
-- PATH VARIABLES --
utils.us_channels = {us1=0, us2=0, us3=0, us4=0, us5=0, us6=0, us7=0, us8=0, us9=0, us10=0}
--TODO : VERIFY ANGLE !!!
utils.us_angles = {us1=36, us2=72, us3=108, us4=144, us5=180, us6=216, us7=252, us8=288, us9=324, us10=360}
utils.us_timestamp = {us1=0, us2=0, us3=0, us4=0, us5=0, us6=0, us7=0, us8=0, us9=0, us10=0}
utils.last_pose = {x=0, y=0, theta=0}
-- FUNCTIONS--
-- QUEUE FUNCTIONS --

Queue = {}
function Queue.new ()
    return {first = 0, last = -1}
end

function Queue.push(list, value)
    local last = list.last + 1
    list.last = last
    list[last] = value
end

function Queue.pop(list)
    local first = list.first
    if first > list.last then error("list is empty") end
    local value = list[first]
    list[first] = nil        -- to allow garbage collection
    list.first = first + 1
    return value
end

function Queue.is_empty(list)
    return list.first > list.last
end

-- LUA FUNCTIONS --
function utils.escrall(func, ...) --protected call, tailored for E.S.C.Ro.C.S
    local status, err = pcall(func, ...)
    if not status then
        print(err)
    end
end


-- POSITIONS FUNCTIONS --
function utils.get_distance(x1, y1, x2, y2)
    return math.sqrt((x2-x1)^2 + (y2-y1)^2)
end

-- AVOIDANCE FUNCTIONS --
function utils.is_point_in_circle(x, y, circle_x, circle_y, radius)
    return utils.get_distance(x, y, circle_x, circle_y) <= radius
end

-- returns the closest point from the start point(robot_pose) that isn't in the ennemy's circle
function utils.get_valid_pt(start_x, start_y, ennemy_x, ennemy_y)
    local closest_pt, closest_dist = nil, 100000

    for k,v in pairs(path_settings.table_coordinates) do
        local dist = utils.get_distance(start_x, start_y, v.x, v.y)

        if (dist < closest_dist and 
        utils.is_point_in_circle(v.x, v.y, ennemy_x, ennemy_y, config.ENNEMY_RADIUS_MM)) then
            closest_pt = k
            closest_dist = dist
        end
    end
    return closest_pt
end

-- PATHFINDING FUNCTIONS --
function utils.reach_closest_waypoint(start_x, start_y, opfor_x, opfor_y)
    --todo UNFINISHED
    -- find closest point to start_pose with help of path settings that avoid opfor

end



function utils.update_us_channels(timestamp)
    local readings = {get_us_readings()}
    for k,v in pairs(readings) do
        if utils.us_channels[k] ~= v then
            utils.us_channels[k] = v
            utils.us_timestamp[k] = timestamp
        end
    end
end

function utils.get_opfor_position(timestamp)
    utils.update_us_channels(timestamp)

    -- calculate position
    local x_robot, y_robot, theta_robot = get_pose() 
    local closest_dist = 100000
    local x_OPFOR, y_OPFOR = nil, nil

    for k,v in pairs(utils.us_channels) do
        if timestamp - utils.us_timestamp[k] < config.US_DECAY_TIME_MS then -- if scan still valid
            local angle = utils.us_angles[k]
            local x = x_robot + v * math.cos(theta_robot + angle)
            local y = y_robot + v * math.sin(theta_robot + angle)
            local dist = utils.get_distance(x_robot, y_robot, x, y)
            if dist < closest_dist then
                closest_dist = dist
                x_OPFOR, y_OPFOR = x, y
            end
        end
    end
    return x_OPFOR, y_OPFOR -- can be nil

end

--utils.pushback_target -> get ennemy angle, calculate a point opposite to him, if it's not on table, compensate




local state = {}
state.__index = state

state.score = 0

state.cb_finish = function()
    print("unimplemented cb_finish !")
end
state.movement_state = 0 -- 0 = done, 1 = stopped, 2 = moving
-- scan_channels(tonumber("1111111111", 2)) -- full scan (mask of 10 bits)

state.start_action_stamp = 1


state.jump_count = 0
state.max_jump = 0
state.cb_jump = nil
state.is_jumping = false

state.x_dest = 0
state.y_dest = 0
state.theta_dest = 0


state.get_wpt_coords = function(wpt)
    return path_settings.table_coordinates[wpt].x, path_settings.table_coordinates[wpt].y
end

state.move_safe = function (x, y, theta)
    state.movement_state = 2
    state.x_dest = x
    state.y_dest = y
    state.theta_dest = theta
    set_pose(x,y,theta, true)
    
end


state.move_S1_phase = 0
state.move_S1 = function(timestamp)
    if state.move_S1_phase == 0 then
        state.move_S1_phase = 1
        move_servo(1, 3000)
        local x, y = state.get_wpt_coords("S1")
        state.move_safe(x, y, config.theta_pince_mur) -- 60° in radians
    end

    if state.movement_state == 0 and state.move_S1_phase == 1 then
        state.move_S1_phase = 2
        local x,y = get_pose()
        local x_dest, y_dest = x, config.ROBOT_CENTER_Y_BOTTOM - config.OVERSHOOT_MM
        -- TODO : move_UNSAFE below
        state.move_safe(x_dest, y_dest, config.theta_pince_mur - 0.1 * 1) -- Increment at each travel along wall -> Todo : convert to a variable

    end

    if state.movement_state == 1 and state.move_S1_phase == 2 then
        state.cb_finish(timestamp)
    end
end

state.is_following_S1 = 0
state.follow_S1 = function(timestmap)
    if state.is_following_S1 == 0 then
        state.is_following_S1 = 1
        local x,y = get_pose()
        state.move_safe(900, y - 100,config.theta_pince_mur - 0.1 * 2 )
    end
    if state.movement_state == 0 and state.is_following_S1 == 1 then
        local x,y = get_pose()
        overwrite_pose(x, 130, config.theta_pince_mur)
        state.cb_finish(timestamp)
    end

end
--
--state.action_state.onfollow_wall_S1 = function(fsm, name, from, to)
--    state.movement_state.onstopped = function (self, event, from, to)
--        state.movement_state:cnl()
--    end
--    --state.movement_state:move_safe("INI", -0.52359877559) -- 60° in radians
--
--end
--
--state.actions.following_wall_S1 = {}
--
--state.actions.following_wall_S1.start_stamp = nil
--state.actions.following_wall_S1.pos_x = nil
--state.actions.following_wall_S1.panel_count = 0
--state.actions.following_wall_S1.contactor = 0   -- 0 = Unpressed, 1 = pressed, 2 = is unpressed since config.proximity_panel_timeout (100ms ?)
--state.actions.following_wall_S1.loop = function(timestamp)
--    if state.movement_state.current == "done" then
--        local x,y, theta = get_pose()
--        local x_dest, y_dest, theta_dest = x + config.STEP_DISTANCE, y + config.OVERSHOOT_MM, theta - config.OVERSHOOT_THETA
--        state.movement_state:move_safe(x_dest, y_dest, theta_dest)
--    end
--    if get_button(101) == true and state.actions.following_wall_S1.contactor == 0 then
--        move_servo(1, 6000)
--        state.actions.following_wall_S1.panel_count = state.actions.following_wall_S1.panel_count + 1
--        state.actions.following_wall_S1.contactor = 1
--        state.actions.following_wall_S1.pos_x = get_pose()
--    end
--
--    if state.actions.following_wall_S1.contactor == 1 and get_button(101) == false and
--    get_pose() > state.actions.following_wall_S1.pos_x + config.DIST_BEF_ARM then
--        state.actions.following_wall_S1.contactor = 0
--        move_servo(1, 3000)
--    end
--
--    if state.actions.following_wall_S1.panel_count > 3 then
--        state.movement_state.onstopped = nil
--        state.movement_state:stop()
--        state.action_state:do_nothing()
--    
--    end
--
--end

state.is_move_P11B_started = false
state.move_P11B = function(timestamp)
    if state.movement_state == 0 and state.is_move_P11B_started == false then
        local x, y = state.get_wpt_coords("P11B")
        state.move_safe(x, y, - config.pi / 2 + 0.17) -- Correction to allow robot to be on good angle
        state.is_move_P11B_started = true
    end
    if state.movement_state == 0 and state.is_move_P11B_started == true then
        state.cb_finish(timestamp)
    end
end

state.push_P11B = function (timestamp)
    state.max_jump = 5
    state.cb_jump = function ()
        if state.movement_state == 0 and
        state.jump_count >= state.max_jump then
            move_servo(5, 10000) -- Position basse
            state.is_jumping = false
            state.cb_jump = nil
            state.cb_finish(timestamp)
        end
        if state.movement_state == 0 then
            local x,y, theta = get_pose()
            local x_dest, y_dest, theta_dest = x, y + config.STEP_DISTANCE, theta
            state.move_safe(x_dest, y_dest, theta_dest)
            state.jump_count = state.jump_count + 1
        end
    end
    state.is_jumping = true
end


state.fetch_plant = function (timestamp)

    print("state.start_action_stamp " .. tostring(state.start_action_stamp))

    if state.start_action_stamp == nil or state.start_action_stamp == 1 then
        state.start_action_stamp = timestamp
    end
    -- once servomotor is locked
    if timestamp - state.start_action_stamp > 300 then
        move_stepper(0, -2100, 0.1)
    end
    if timestamp - state.start_action_stamp > 1500 then
        state.cb_finish(timestamp)
        -- stepper is in position
    end
end

state.move_JTOP_started = 0
state.move_JTOP = function(timestamp)
    if state.move_JTOP_started == 0 then
        state.move_JTOP_started = 1
        local x, y = state.get_wpt_coords("AML")
        state.movement_state:move_safe(x, y, - config.pi / 2)
    end
    if state.movement_state == 0 and state.move_JTOP_started == 1 then
        local x1 = get_pose()
        state.movement_state:move_safe(x1, 2000, - config.pi / 2)
        state.move_JTOP_started = 2
    end
    if state.movement_state == 0 and state.move_JTOP_started == 2 then
        state.cb_finish(timestamp)
    end
end

state.depose_plant_started = 0
state.depose_plant = function (timestamp)
    if state.depose_plant_started == 0 then
        move_stepper(0, -300, 0.1)
        state.depose_plant_started = 1
    end
    if state.depose_plant_started == 1 
    and timestamp - state.start_action_stamp > 3000 then
        move_servo(5, 2000)
        state.depose_plant_started = 2
    end

    if state.depose_plant_started == 2 and
    timestamp - state.start_action_stamp > 3500 then
        move_stepper(0, -1300, 0.1)
        state.depose_plant_started = 3
    end

    if state.depose_plant_started == 3 and
    timestamp - state.start_action_stamp > 5000 then
        state.cb_finish(timestamp)
    end

end

state.is_homing_top = false
state.home_top = function (timestamp)
    if state.is_homing_top == false then
        state.is_homing_top = true
        local x, y = state.get_wpt_coords("FAPT")
        state.move_safe(x, y, - config.pi / 2)
    end
    if state.movement_state == 0 and state.is_homing_top == true then
        state.cb_finish(timestamp)
    end

end

-- action order

state.action_order = {}
--state.action_order[1] = state.action_state.move_S1
--state.action_order[1] = state.move_P11B
--state.action_order[2] = state.push_P11B
--state.action_order[3] = state.fetch_plant
--state.action_order[4] = state.move_JTOP
--state.action_order[5] = state.depose_plant
--state.action_order[6] = state.home_top

state.action_order[1] = state.move_S1
state.action_order[2] = state.follow_S1
state.action_order[3] = state.home_top


state.cb_finish = function()
    print("cb_finished !")
    if state.action_order[1] ~= nil or true then
        print("finished action ".. tostring(state.action_order[1]))
        table.remove(state.action_order, 1)
        state.start_action_stamp = timestamp

    end
end
--TEST FUNCTION 
--[[
function state.reach_S6()
    state.action_state:reach(S6)  (-> Modify state.destination)
    state.recovery_method = state.Recovery.AROUND
    state.movement_state.onstopped = scan & wait
    state.movement_state.ondone = check_action(zone, state.action_state:make_S6)
end

function state.make_S6() -- RENAME IT
    state.action_state:perform_action()
    state.onactiondone -> increment point & reach autre action
    set pose (detection = true)
    state.recovery_method = state.Recovery.CNL
    state.movement_state.onstopped = count points, scan & wait
    nb_panneaux = 0
    Mettre un timer : si sensor_state toujours unpressed -> error, reach_autre_action
    state.sensor_state.ontrigger_left_contactor = increment point, bouger la pince, + mettre un timer pour rétracter la pince
    if nb_panneaux > 2, then state.movement_state.ondone -> reach_autre action
end
--]]
function state.loop(timestamp)
 --Weird bug correction of nil
    if state.start_action_stamp == nil or state.start_action_stamp == 1 then
        state.start_action_stamp = timestamp
    end
    -- MOVEMENT LOOP
    if is_motion_done() then
        state.movement_state = 0
    end

    if state.is_jumping then
        state.cb_jump()
    end
    --if(state.movement_state.current == "moving" and is_blocked()) {
    --    state.movement_state:stop()
    --}

    -- ACTION LOOP
    state.action_order[1](timestamp)
    

end





-- CAREFUL TO ORDER OF IMPORTATION : Makes sure it works for dependencies !





--x_initial, y_initial, theta_initial = path_settings.table_coordinates.INI.x, path_settings.table_coordinates.INI.y, 0
x_initial, y_initial, theta_initial = path_settings.table_coordinates.INI.x, path_settings.table_coordinates.INI.y, -config.pi / 2

main_loop = nil -- coroutine/thread
is_right = nil -- boolean
start_time = nil

test_function_done = false
function on_init(side)
    is_right = side
    overwrite_pose(x_initial, y_initial, theta_initial)
    move_servo(1, 6000) --pince droite
    move_stepper(0, 200, 0.15) -- Stepper "initialization"
    move_servo(5, 2000) -- Porte_pince (position haute)
    print("init done ! ")
    -- DEBUG TEST : 

end

function on_loop(timestamp)
    if start_time == nil then
        start_time = timestamp
    end

    state.loop(timestamp)
    --here we do our shit

    --print("t " .. tostring(timestamp))
    return config.DEFAULT_LOOP_PERIOD_MS
end

function create_coroutine()
    main_loop = coroutine.create( function (timestamp)
        start_time = timestamp
        while true do
            if (timestamp - start_time) > config.MATCH_DURATION_MS then
				on_end()
                break
            end
            sleep_period = on_loop(timestamp)
            timestamp = coroutine.yield(sleep_period)
        end
    end)
end


-- resume loop will receive the "start_time timestamp on first call"
function resume_loop(timestamp)
    if main_loop == nil then
        create_coroutine()
    end
    status, value = coroutine.resume(main_loop, timestamp)
    if coroutine.status (main_loop) == "dead" then
        print("lua script crashed at : ")
        print(tostring(value))
        print(debug.traceback(main_loop))

		main_loop = -2
		return -2
    end
	return value

end

function on_end()
    print("Score: " .. state.score)
end