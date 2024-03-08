path_settings = {}

path_settings.table_coordinates = {
    INI = {x=200, y= 200}, -- starting position
    S6 = {x=2000, y=200}, -- 6th solar panel
    S1 = {x=300, y=200}, -- 1st solar panel
    S1E = {x=250, y=180}, -- end 1st solar panel with overshoot
    A8 = {x=500, y=400},  -- Aruco bottom left corner (~8 o'clock)
    P6B = {x=1500, y=400}, -- Plant 6, bottom (6 o'clock)


}

-- TODO EDGES !!!
path_settings.edges = {
    INI = {"S6", "A8"},
    S6 = { "INI", "P6B"},
    A8 = {"INI", "P6B"},
    P6B = {"S6", "A8"},
}

return path_settings

