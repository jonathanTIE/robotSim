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

return path_settings