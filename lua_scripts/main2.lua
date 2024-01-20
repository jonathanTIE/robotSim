local utils = require("utils")
local machine = require("statemachine")

local movement_state = machine.create( {
    initial = "done",
    events = {
        { name = "move", from = "done", to = "moving" },
        { name = "stop", from = "moving", to = "done" },
    }
})

MATCH_DURATION_MS = 87000
DEFAULT_LOOP_PERIOD_MS = 50

x_initial, y_initial, theta_initial = 0, 0, 0

main_loop = nil -- coroutine/thread
is_right = nil -- boolean
start_time = nil

moved = false
function on_init(side)
    is_right = side
    overwrite_pose(x_initial, y_initial, theta_initial)
    print("init done ! ")
end

function on_loop(timestamp)
    --here we do our shit
    --print(timestamp - start_time)
    --utils.escrcall(print, "escrall")
    if (timestamp - start_time) > 10000 and not moved then -- TEST
        moved = true
        utils.escrall(set_pose, 200.0, 200.0, 0.0, false)
        --set_pose(200.0, 200.0, 0.0, false)
        print("displacement")
    end
    --print("t " .. tostring(timestamp))
    return DEFAULT_LOOP_PERIOD_MS
end

function create_coroutine()
    main_loop = coroutine.create( function (timestamp)
        start_time = timestamp
        while true do
            if (timestamp - start_time) > MATCH_DURATION_MS then
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
		main_loop = nil
		return -1
    end
	return value

end

function on_end()
    print("Score: 0")
end
