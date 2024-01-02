function on_init() 
	print("shit")
	sleep(2.0)
	print("foo")
	set_pump(1, true)
end

function on_run() 
	print("runnning")
end

function on_end()
	print("end")
end

