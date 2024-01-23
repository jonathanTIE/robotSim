local states = {}

-- 2 states machines : one for displacement, & the rest
local movement_state = machine.create( {
    initial = "done",
    events = {
        { name = "move", from = "done", to = "moving" },
        { name = "stop", from = "moving", to = "done" },
    }
})

local action_state = machine.create( {
    initial= "start",
    events = { 

    }
})


return states