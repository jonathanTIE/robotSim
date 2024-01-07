function on_init() 
	print("init")
end

function on_run()
	print("on_run")
end

main_loop = coroutine.create( function ()
	i = 0
	while true do
		print(i)
		coroutine.yield(100)
	end
end
)

function on_end()
	print("end")
end

