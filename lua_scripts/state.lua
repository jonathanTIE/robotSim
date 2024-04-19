config = require("config")
utils = require("utils")


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
state.action_order[1] = state.move_P11B
state.action_order[2] = state.push_P11B
state.action_order[3] = state.fetch_plant
state.action_order[4] = state.move_JTOP
state.action_order[5] = state.depose_plant
state.action_order[6] = state.home_top


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




return state