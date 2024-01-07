termination = false

function on_init() 
	print("init")
	set_pump(1, true)
end

function on_run()
	print("set pose to 1.0 1.0 0.0")
	set_pose(200.0, 200.0, 0.0, true)
	sleep(3.0)
	set_pose(300.0, 250.0, 0.0, true)
	sleep(3.0)
	set_pose(400, 400, 0.0, true)
end

function on_end()
	print("end")
end

