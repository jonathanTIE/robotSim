config = require("config")
utils = require("utils")
machine = require("statemachine") -- Library


local state = {}
state.__index = state

state.Recovery = {
    CNL = {},
    PUSHBCK = {},
    AROUND = {},
    WAIT = {}, --Do nothing until ennemy move
}

state.recovery_method = state.Recovery.CNL -- Default state
state.destination = nil -- Default state

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


--local function reach_around_S6(fsm, name, from, to)
--    --UNFINISHED
--    start_x, start_y = get_pose()
--    end_x, end_y = table_coordinates["S6"].x, table_coordinates["S6"].y
--    reach_around(start_x, start_y, end_x, end_y)
--
--end



function state.scan_and_wait_us(fsm, name, from, to, action_fsm, timestamp)
    action_fsm:scan_and_wait_inf()
    scan_channels(tonumber("1111111111", 2)) -- full scan (mask of 10 bits)
    if state.timer.start ~= nil then
        error("state.can_and_wait_us: timer already set - resseting it")
    end

    state.timer.set(timestamp, config.SCAN_DURATION_MS, 
        function() fsm:transition(name) action_fsm:end_scan() end)

    return fsm.ASYNC
end

-- function to be called to find a solution after 1. robot is blocked 2. one scan has been done 
function state.recover_from_blocked(fsm, name, from, to, timestamp)
    local opfor_x, opfor_y = utils.get_opfor_position(timestamp)
    local dest_waypt = utils.reach_closest_waypoint(start_x, start_y, opfor_x, opfor_y)
    if state.recovery_method == state.Recovery.CNL then
        error("unimplemented cancel")
    elseif state.recovery_method == state.Recovery.PUSHBCK then
        error("unimplemented pushback")
    elseif state.recovery_method == state.Recovery.WAIT then
        error("unimplemented wait")
    elseif state.recovery_method == state.Recovery.AROUND then
        utils.pathfind(dest_waypt, state.destination)
    else
        error("state.recover_from_blocked: invalid recovery method")
    end
    
end



-- 2 MACHINES --
-- one for displacement, & the rest

state.movement_state = machine.create( {
    initial = "done",
    events = {
        { name = "move_safe", from = {"done", "stopped"} , to = "moving_safe"},
        { name = "move_blind", from = {"done", "stopped"}, to = "moving_blind"},
        { name = "set_done", from = {"moving_blind", "moving_safe"}, to = "done"},
        { name = "set_stopped", from = "moving_safe", to = "stopped"},

    },
    callbacks = {
        onmove_safe = function(fsm, name, from, to, waypoint, theta)
            if path_settings.table_coordinates[waypoint] == nil then
                error("state.movement_state.onmove_safe: invalid waypoint : " .. tostring(waypoint))
            end
            local x = path_settings.table_coordinates[waypoint].x
            local y = path_settings.table_coordinates[waypoint].y
            set_pose(x, y, theta, true)
        end,
--        onset_stopped = function(fsm, name, from, to, timestamp)  
--            state.scan_and_wait_us(fsm, name, from, to, state.action_state, timestamp)
--        end,
    },
})

state.action_state = machine.create ( {
    initial = "idle",
    events = {
        {name = "scan_and_wait_inf", from = "idle", to = "scanning"},
        {name = "end_scan", from = "scanning", to = "idle"},
        {name = "do_nothing", from = '*', to = "idle"}, -- Used to make sure that the machine is idle when beggining a new action
        {name = "move_S1", from = '*', to = "sticking_wall_S1"},
        {name = "follow_wall_S1", from = '*', to = "following_wall_S1"}---- Deploy arm

    },
    callbacks = {
        -- EVENTS

--        onend_scan = function(fsm, name, from, to, timestamp)
--            utils.get_opfor_position(timestamp) end,

        -- STATES
        -- onidle = ... Moved to state.loop to make it called on first loop
    },
})

state.actions = {}

state.action_state.onmove_S1 = function(fsm, name, from, to, timestamp)
    print("beg act_solar_S1_to_S1_init")
    state.movement_state:move_safe("S1", -0.52359877559) -- 60° in radians

    -- Stick to wall with UNsafe move : 
    state.movement_state.ondone = function (self, event, from, to)
        local x,y = get_pose()
        local x_dest, y_dest = x, config.ROBOT_CENTER_Y_BOTTOM - config.OVERSHOOT_MM
        state.movement_state:move_blind(x_dest, y_dest, -0.52359877559)
        state.movement_state.ondone = function (self, event, from, to)
            state.action_state:follow_wall_S1()
            state.movement_state.ondone = nil
        end
    end

end

state.action_state.onfollow_wall_S1 = function(fsm, name, from, to)
    move_servo(1, 4000)
    state.movement_state:move_safe("INI", -0.52359877559) -- 60° in radians

end

-- Test function that doesn't use the contactor
state.actions.following_wall_S1 = {
    start_stamp = nil,
    panel_count = 0,
    left_contactor = 0,     -- 0 = Unpressed, 1 = pressed, 2 = is unpressed since config.proximity_panel_timeout (100ms ?)
    loop = nil,
}

state.actions.following_wall_S1.loop = function(timestamp)
    local start_stamp = state.actions.following_wall_S1.start_stamp
    if start_stamp == nil then
        start_stamp = timestamp
    end
    if timestamp - start_stamp > config.PANEL_ARM_TIMEOUT_MS then
        move_servo(1, 2000)
        state.movement_state.ondone = function (self, event, from, to)
            print("follow_wall_S1_over")
            state.action_state:do_nothing()
            state.movement_state.ondone = nil
        end
        
    end
    print("CXZ")
    -- TODO : ontrigger_left_contactor : moving servo !!
end


-- action order

state.action_order = {}
state.action_order[1] = state.action_state.move_S1
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

    -- ACTION LOOP
    if state.action_state.current == "idle" then
        if state.action_order[1] ~= nil or true then
            print("dequeuing action ".. tostring(state.action_order[1]))
            table.remove(state.action_order, 1)(state.action_state, timestamp)
        end
    end

    print(state.movement_state.current)
    -- SENSOR LOOP
    --[[ 
    if state.sensor_state.current == "unpressed_left_conn" then
        if is_left_connector_pressed() then
            state.sensor_state:trigger_left_connector()
        end
    end
    if state.sensor_state.current == "triggered_left_con" then
        if not is_left_connector_pressed() then
            state.sensor_state:disable_left_connector()
        end
    end
    --]]
end




return state