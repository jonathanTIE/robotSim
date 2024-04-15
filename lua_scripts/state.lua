config = require("config")
utils = require("utils")
machine = require("statemachine") -- Library


local state = {}
state.__index = state

state.Recovery = {
    CNL = {},
    PUSHBCK = {},
    WAIT_2S = {}, --Do nothing until ennemy move
}

state.score = 0
state.recovery_method = state.Recovery.CNL -- Default state
state.destination = {} -- Default state
state.stop_stamp = 0
state.end_scan_stamp = nil

-- TIMER FUNCTION --
state.timer = {} -- SINGLETON => Only one timer at a time

state.timer.set = function (timestamp, duration, --[[optional]] callback)
    state.timer.start = timestamp
    state.timer.duration_left = duration
    state.timer.callback = callback or nil
end

-- If timer done, call callback if any & reset timer
state.timer.is_done = function (timestamp)
    if (timestamp - state.timer.start) > state.timer.duration_left then
        if state.timer.callback ~= nil then
            state.timer.callback()
        state.timer.start = nil
        state.timer.duration_left = nil
        state.timer.callback = nil
        end
        return true
    else
        return false
    end
end


-- 2 MACHINES --
-- one for displacement, & the rest

state.movement_state = machine.create( {
    initial = "done",
    events = {
        { name = "move_safe", from = {"done", "recovering"} , to = "moving_safe"},
        { name = "move_blind", from = {"done", "recovering"}, to = "moving_blind"},
        { name = "set_done", from = {"moving_blind", "moving_safe"}, to = "done"},
        { name = "stop", from = "moving_safe", to = "stopped"},
        { name = "wait_bck_cnl", from = "stopped", to = "full_recovering"},
        { name = "cnl", from = "stopped", to = "canceled"},

    },

})

state.get_wpt_coords = function(waypoint)
    if path_settings.table_coordinates[waypoint] == nil then
        error("state.get_wpt_coords: invalid waypoint : " .. tostring(waypoint))
    end
    return path_settings.table_coordinates[waypoint].x, path_settings.table_coordinates[waypoint].y
end

state.movement_state.onmove_safe = function(fsm, name, from, to, x, y, theta)
    state.destination.x = x
    state.destination.y = y
    state.destination.theta = theta
    set_pose(x, y, theta, true)
end

state.movement_state.onmove_blind = function(fsm, name, from, to, x, y, theta)
    state.destination.x = x
    state.destination.y = y
    state.destination.theta = theta
    set_pose(x, y, theta, false)
end

state.movement_state.onset_stopped = function(fsm, name, from, to, timestamp)  
    scan_channels(tonumber("1111111111", 2)) -- full scan (mask of 10 bits)
    state.end_scan_stamp = timestamp + config.SCAN_DURATION_MS
    state.stop_stamp = timestamp
end

state.movement_state.onscan_over = function (fsm, name, from, to, timestamp)
        -- IMPLEMENT MEGA LOGIC
    
    -- TODO : Implement a function to check if the scan is over
    --if timestamp > state.end_scan_stamp then
    --    fsm:transition(name)
    --end
    state.movement_state:move_safe(state.destination.x, state.destination.y, state.destination.theta)
end

state.movement_state.onwait_bck_cnl = function(fsm, name, from, to)
    --TODO : do something else than just waiting
    state.timer.set(state.stop_stamp, state.end_scan_stamp, function()
        state.movement_state:move_safe(state.destination.x, state.destination.y, state.destination.theta)
    end)
end


state.action_state = machine.create ( {
    initial = "idle",
    events = {
        {name = "scan_and_wait_inf", from = "idle", to = "scanning"},
        {name = "end_scan", from = "scanning", to = "idle"},
        {name = "do_nothing", from = '*', to = "idle"}, -- Used to make sure that the machine is idle when beggining a new action
        {name = "move_S1", from = '*', to = "sticking_wall_S1"},
        {name = "follow_wall_S1", from = '*', to = "following_wall_S1"}, ---- Deploy arm
        {name = "move_PB11", from = '*', to = "moving_PB11"},
        {name = "push_PB11", from = '*', to = "pushing_PB11"},
        {name = "fetch_plant", from = '*', to = "fetching_plant"},
        {name= "move_JTOP", from = '*', to = "moving_JTOP"},
        {name= "depose_plant", from = "*", to = "deposing_plant"},
        {name = "home_TOP", from = "*", to = "homing_TOP"},
        
        

    },
    --callbacks = {
        -- EVENTS

--        onend_scan = function(fsm, name, from, to, timestamp)
--            utils.get_opfor_position(timestamp) end,

        -- STATES
        -- onidle = ... Moved to state.loop to make it called on first loop
    --},
})

state.actions = {}

state.action_state.onmove_S1 = function(fsm, name, from, to, timestamp)
    print("beg act_solar_S1_to_S1_init")
    move_servo(1, 3000)
    local x, y = state.get_wpt_coords("S1")
    state.movement_state:move_safe(x, y, config.theta_pince_mur) -- 60° in radians
    state.movement_state.on_stopped = function (self, event, from, to)
        state.movement_state:wait_bck_cnl()
    end

    -- Stick to wall with UNsafe move : 
    state.movement_state.ondone = function (self, event, from, to)
        local x,y = get_pose()
        local x_dest, y_dest = x, config.ROBOT_CENTER_Y_BOTTOM - config.OVERSHOOT_MM
        state.movement_state:move_blind(x_dest, y_dest, config.theta_pince_mur - 0.1 * 1) -- Increment at each travel along wall -> Todo : convert to a variable
        state.movement_state.ondone = function (self, event, from, to)
            state.action_state:follow_wall_S1()
            state.movement_state.ondone = nil
        end
    end

end

state.action_state.onfollow_wall_S1 = function(fsm, name, from, to)
    state.movement_state.onstopped = function (self, event, from, to)
        state.movement_state:cnl()
    end
    --state.movement_state:move_safe("INI", -0.52359877559) -- 60° in radians

end

state.actions.following_wall_S1 = {}

state.actions.following_wall_S1.start_stamp = nil
state.actions.following_wall_S1.pos_x = nil
state.actions.following_wall_S1.panel_count = 0
state.actions.following_wall_S1.contactor = 0   -- 0 = Unpressed, 1 = pressed, 2 = is unpressed since config.proximity_panel_timeout (100ms ?)
state.actions.following_wall_S1.loop = function(timestamp)
    if state.movement_state.current == "done" then
        local x,y, theta = get_pose()
        local x_dest, y_dest, theta_dest = x + config.STEP_DISTANCE, y + config.OVERSHOOT_MM, theta - config.OVERSHOOT_THETA
        state.movement_state:move_safe(x_dest, y_dest, theta_dest)
    end
    if get_button(101) == true and state.actions.following_wall_S1.contactor == 0 then
        move_servo(1, 6000)
        state.actions.following_wall_S1.panel_count = state.actions.following_wall_S1.panel_count + 1
        state.actions.following_wall_S1.contactor = 1
        state.actions.following_wall_S1.pos_x = get_pose()
    end

    if state.actions.following_wall_S1.contactor == 1 and get_button(101) == false and
    get_pose() > state.actions.following_wall_S1.pos_x + config.DIST_BEF_ARM then
        state.actions.following_wall_S1.contactor = 0
        move_servo(1, 3000)
    end

    if state.actions.following_wall_S1.panel_count > 3 then
        state.movement_state.onstopped = nil
        state.movement_state:stop()
        state.action_state:do_nothing()
    
    end

end

state.action_state.onmove_PB11 = function(fsm, name, from, to)
    local x, y = state.get_wpt_coords("P11B")
    state.movement_state:move_safe(x, y, - config.pi / 2 + 0.17) -- Correction to allow robot to be on good angle
    state.movement_state.onstopped = function (self, event, from, to)
        -- retry
    end
    state.movement_state.ondone = function (self, event, from, to)
        state.action_state:push_PB11()
    end
end

state.action_state.onpush_PB11 = function(fsm, name, from, to)
    state.movement_state.onstopped = function (self, event, from, to)
        state.movement_state:wait_bck_cnl()
    end
end

state.actions.pushing_PB11 = {}
state.actions.pushing_PB11.max_jump = 5
state.actions.pushing_PB11.jump_count = 0
state.actions.pushing_PB11.loop = function(timestamp)
    if state.actions.pushing_PB11.jump_count >= state.actions.pushing_PB11.max_jump 
    and state.movement_state.current == "done"
    then
        state.movement_state.onstopped = nil
        state.movement_state:stop()
        move_servo(5, 10000) -- Position basse
        state.action_state:fetch_plant()
    end
    if state.movement_state.current == "done" then
        local x,y, theta = get_pose()
        local x_dest, y_dest, theta_dest = x, y + config.STEP_DISTANCE, theta
        state.movement_state:move_safe(x_dest, y_dest, theta_dest)
        state.actions.pushing_PB11.jump_count = state.actions.pushing_PB11.jump_count + 1
        print("JUMPING")
    end
end

state.actions.fetching_plant = {}
state.actions.fetching_plant.start_stamp = nil
state.actions.fetching_plant.loop = function(timestamp)
    if state.actions.fetching_plant.start_stamp == nil then
        print("fetching_plant start_stamping")
        state.actions.fetching_plant.start_stamp = timestamp
        do return end
    end

    print(tostring(timestamp))
    -- if servomoteur verouillé
    if timestamp - state.actions.fetching_plant.start_stamp > 300 then
        move_stepper(0, -2100, 0.05)
    end

    -- wait for palonnier assez haut avant de bouger
    if timestamp - state.actions.fetching_plant.start_stamp > 1500 then
        print("here")
        state.action_state:do_nothing()
    end

end
state.action_state.onfetch_plant = function(fsm, name, from, to)
    
    -- TODO
end

state.action_state.onmove_JTOP = function(fsm, name, from, to)
    state.movement_state.on_stopped = function (self, event, from, to)
        state.movement_state:wait_bck_cnl()
    end
    local x, y = state.get_wpt_coords("AML")
    state.movement_state:move_safe(x, y, - config.pi / 2)
    state.movement_state.ondone = function (self, event, from, to)
        local x1 = get_pose()
        state.movement_state:move_safe(x1, 2000, - config.pi / 2)
        state.movement_state.ondone = function (self, event, from, to)
            state.action_state:depose_plant()
            state.movement_state.on_stopped = nil
        end
    end

end

state.action_state.ondepose_plant = function(fsm, name, from, to)

end

state.actions.deposing_plant = {}
state.actions.deposing_plant.start_stamp = nil
state.actions.deposing_plant.loop = function(timestamp)
    if state.actions.deposing_plant.start_stamp == nil then
        state.actions.deposing_plant.start_stamp = timestamp
        move_stepper(0, -300, 0.05)
        do return end
    end

    if timestamp - state.actions.deposing_plant.start_stamp > 3000 then
        move_servo(5, 2000)
    end

    if timestamp - state.actions.deposing_plant.start_stamp > 3500 then
        move_stepper(0, -1300, 0.05)
    end

    if timestamp - state.actions.deposing_plant.start_stamp > 5000 then
        state.action_state:do_nothing()
    end


end
-- action order

state.action_order = {}
--state.action_order[1] = state.action_state.move_S1
state.action_order[1] = state.action_state.move_PB11
--state.action_order[2] = state.action_state.move_JTOP
--state.action_order[1] = state.action_state.push_PB11
    --state.init_act_reset_pos_corner_btm,
    --state.init_act_plant_PB6_to_closest_area,


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
    if state.timer.duration_left ~= nil then
        state.timer.is_done(timestamp)
    end

    -- MOVEMENT LOOP
    if is_motion_done() then
        state.movement_state:set_done(timestamp)
    end

    --if(state.movement_state.current == "moving" and is_blocked()) {
    --    state.movement_state:stop()
    --}

    if state.movement_state.current == "stopped" and timestamp > state.end_scan_stamp then
        state.movement_state:scan_over(timestamp)
    end


    -- ACTION LOOP
    if state.action_state.current == "idle" then
        if state.action_order[1] ~= nil or true then
            print("dequeuing action ".. tostring(state.action_order[1]))
            table.remove(state.action_order, 1)(state.action_state, timestamp)
        end
    end

    -- shitty workaround due to impossibility to do indexing through state.actions['xxxxxx']
    for k, v in pairs(state.actions) do
        if state.action_state.current == k then
            if v.loop ~= nil then
                v.loop()
            else
                print("strange_behaviour for action_state")
            end
        end

    end
end




return state