local utils = {}


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

-- PATH FUNCTIONS --
-- TODO : Make a check for path_settings input

--TODO : find a use for this or delete :
function utils.get_edges(edges_table)
    for vertice,v in pairs(edges_table) do
            print(vertice)
        for _,w in pairs(v) do
            print(w)
        end
    end
    return
end

function utils.backtrace(parents, start_vertice, end_vertice)
    local path = {}
    local vertice = end_vertice
    while vertice ~= start_vertice do
        table.insert(path, 1, vertice)
        vertice = parents[vertice]
    end
    table.insert(path, 1, start_vertice)
    return path
end

function utils.get_shortest_path(edges_table, start_vertice, end_vertice)
    -- BFS algorithm, based on wikipedia
    local parents = {}
    local explored = {}
    local queue = Queue.new()
    explored[start_vertice] = true
    Queue.push(queue, start_vertice)
    while not Queue.is_empty(queue) do
        local vertice = Queue.pop(queue)
        if vertice == end_vertice then
            return utils.backtrace(parents, start_vertice, end_vertice)
        end
        for _,w in pairs(edges_table[vertice]) do
            if not explored[w] then
                explored[w] = true
                parents[w] = vertice
                Queue.push(queue, w)
            end
        end
    end
end

-- TIME FUNCTIONS --

return utils