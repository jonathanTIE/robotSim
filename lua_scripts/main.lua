termination = false

function on_init() 
	print("init")
	set_pump(1, true)
end

function on_run() 
	print("run4242ing")
	sleep(10.0)
	print("runni4242ng_ending")
end

function on_end()
	print("end")
end

