-- CAREFUL TO ORDER OF IMPORTATION : Makes sure it works for dependencies !

local path_settings = require("path_settings")
local config = require("config")
local utils = require("utils")
local machine = require("statemachine") -- Library
local state = require("state") -- Logic




x_initial, y_initial, theta_initial = path_settings.table_coordinates.INI.x, path_settings.table_coordinates.INI.y, 0

main_loop = nil -- coroutine/thread
is_right = nil -- boolean
start_time = nil

test_function_done = false
function on_init(side)
    is_right = side
    overwrite_pose(x_initial, y_initial, theta_initial)
    move_servo(1, 6000) --pince droite
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
    print("Score: 0")
end