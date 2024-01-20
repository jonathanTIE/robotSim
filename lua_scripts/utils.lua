local utils = {}

function utils.escrall(func, ...) --protected call, tailored for E.S.C.Ro.C.S
    local status, err = pcall(func, ...)
    if not status then
        print(err)
    end
end

return utils