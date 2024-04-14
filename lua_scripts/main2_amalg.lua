path_settings = {}

path_settings.table_coordinates = {
    INI = {x=200, y= 200}, -- starting position
    S6 = {x=2000, y=200}, -- 6th solar panel
    S1 = {x=250, y=150}, -- 1st solar panel
    S1EO = {x=450, y=0}, -- End 1st solar panel with Overshoot
    S1ER = {x = 450, y=120}, -- End 1st solar panel with Recalage

    A8 = {x=500, y=400},  -- Aruco bottom left corner (~8 o'clock)
    P6B = {x=1500, y=400}, -- Plant 6, bottom (6 o'clock)

    P11B = {x=1000, y=450},


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


-- https://github.com/kyleconroy/lua-state-machine/blob/master/statemachine.lua

local machine = {}
machine.__index = machine

local NONE = "none"
local ASYNC = "async"

local function call_handler(handler, params)
  if handler then
    return handler(table.unpack(params))
  end
end

local function create_transition(name)
  local can, to, from, params

  local function transition(self, ...)
    if self.asyncState == NONE then
      can, to = self:can(name)
      from = self.current
      params = { self, name, from, to, ...}

      if not can then return false end
      self.currentTransitioningEvent = name

      local beforeReturn = call_handler(self["onbefore" .. name], params)
      local leaveReturn = call_handler(self["onleave" .. from], params)

      if beforeReturn == false or leaveReturn == false then
        return false
      end

      self.asyncState = name .. "WaitingOnLeave"

      if leaveReturn ~= ASYNC then
        transition(self, ...)
      end
      
      return true
    elseif self.asyncState == name .. "WaitingOnLeave" then
      self.current = to

      local enterReturn = call_handler(self["onenter" .. to] or self["on" .. to], params)

      self.asyncState = name .. "WaitingOnEnter"

      if enterReturn ~= ASYNC then
        transition(self, ...)
      end
      
      return true
    elseif self.asyncState == name .. "WaitingOnEnter" then
      call_handler(self["onafter" .. name] or self["on" .. name], params)
      call_handler(self["onstatechange"], params)
      self.asyncState = NONE
      self.currentTransitioningEvent = nil
      return true
    else
    	if string.find(self.asyncState, "WaitingOnLeave") or string.find(self.asyncState, "WaitingOnEnter") then
    		self.asyncState = NONE
    		transition(self, ...)
    		return true
    	end
    end

    self.currentTransitioningEvent = nil
    return false
  end

  return transition
end

local function add_to_map(map, event)
  if type(event.from) == 'string' then
    map[event.from] = event.to
  else
    for _, from in ipairs(event.from) do
      map[from] = event.to
    end
  end
end

function machine.create(options)
  assert(options.events)

  local fsm = {}
  setmetatable(fsm, machine)

  fsm.options = options
  fsm.current = options.initial or 'none'
  fsm.asyncState = NONE
  fsm.events = {}

  for _, event in ipairs(options.events or {}) do
    local name = event.name
    fsm[name] = fsm[name] or create_transition(name)
    if fsm.events[name] == nil then
      fsm.events[name] = { map = {} }
    end
    add_to_map(fsm.events[name].map, event)
  end
  
  for name, callback in pairs(options.callbacks or {}) do
    fsm[name] = callback
  end

  return fsm
end

function machine:is(state)
  return self.current == state
end

function machine:can(e)
  local event = self.events[e]
  local to = event and event.map[self.current] or event.map['*']
  return to ~= nil, to
end

function machine:cannot(e)
  return not self:can(e)
end

function machine:todot(filename)
  local dotfile = io.open(filename,'w')
  dotfile:write('digraph {\n')
  local transition = function(event,from,to)
    dotfile:write(string.format('%s -> %s [label=%s];\n',from,to,event))
  end
  for _, event in pairs(self.options.events) do
    if type(event.from) == 'table' then
      for _, from in ipairs(event.from) do
        transition(event.name,from,event.to)
      end
    else
      transition(event.name,event.from,event.to)
    end
  end
  dotfile:write('}\n')
  dotfile:close()
end

function machine:transition(event)
  if self.currentTransitioningEvent == event then
    return self[self.currentTransitioningEvent](self)
  end
end

function machine:cancelTransition(event)
  if self.currentTransitioningEvent == event then
    self.asyncState = NONE
    self.currentTransitioningEvent = nil
  end
end

machine.NONE = NONE
machine.ASYNC = ASYNC




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
end

state.movement_state.onscan_over = function (fsm, name, from, to, timestamp)
        -- IMPLEMENT MEGA LOGIC
    
    -- TODO : Implement a function to check if the scan is over
    --if timestamp > state.end_scan_stamp then
    --    fsm:transition(name)
    --end
    state.movement_state:move_safe(state.destination.x, state.destination.y, state.destination.theta)
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
    state.movement_state:move_safe(x, y, config.pi / 2)
    state.movement_state.onstopped = function (self, event, from, to)
        -- retry
    end
    state.movement_state.ondone = function (self, event, from, to)
        state.action_state:push_PB11()
    end
end

state.action_state.onpush_PB11 = function(fsm, name, from, to)
    state.movement_state.onstopped = function (self, event, from, to)
        -- TODO CNL !
    end
end

state.actions.pushing_PB11 = {}
state.actions.pushing_PB11.max_jump = 5
state.actions.pushing_PB11.jump_count = 0
state.actions.pushing_PB11.loop = function(timestamp)
    if state.actions.pushing_PB11.jump_count >= state.actions.pushing_PB11.max_jump then
        state.movement_state.onstopped = nil
        state.movement_state:stop()
        state.action_state:do_nothing()
    end
    if state.movement_state.current == "done" then
        local x,y, theta = get_pose()
        local x_dest, y_dest, theta_dest = x + config.STEP_DISTANCE, y, theta
        state.movement_state:move_safe(x_dest, y_dest, theta_dest)
        state.actions.pushing_PB11.jump_count = state.actions.pushing_PB11.jump_count + 1
    end
end

state.actions.fetching_plant = {}
state.actions.fetching_plant.start_stamp = nil
state.actions.fetching_plant.loop = function(timestamp)
    if state.actions.fetching_plant.start_stamp == nil then
        state.actions.fetching_plant.start_stamp = timestamp
        move_stepper(0, 200, 0.15) -- Go_to_bottom
    end
    --if timestamp - state.actions.fetching_plant.start_stamp > ?????????? then
    --    !!!!!!!!!!! move_servo --close
    --end
--
    --if timestamp - state.actions.fetching_plant.start_stamp > ?????????? then
    --    !!!!!!!!!!! 
    --    state.action_state:do_nothing()
    --end
    -- TODO
end
state.action_state.onfetch_plant = function(fsm, name, from, to)
    
    -- TODO
end
-- action order

state.action_order = {}
--state.action_order[1] = state.action_state.move_S1
state.action_order[1] = state.action_state.push_PB11
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





-- CAREFUL TO ORDER OF IMPORTATION : Makes sure it works for dependencies !





x_initial, y_initial, theta_initial = path_settings.table_coordinates.INI.x, path_settings.table_coordinates.INI.y, 0

main_loop = nil -- coroutine/thread
is_right = nil -- boolean
start_time = nil

test_function_done = false
function on_init(side)
    is_right = side
    overwrite_pose(x_initial, y_initial, theta_initial)
    move_servo(1, 6000) --pince droite
    move_stepper(0, 200, 0.15) -- Stepper "initialization"
    move_servo(5, 10000) -- Porte_pince
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