local g2 = {}

function logln(line)
    io.stderr:write(line .. "\n")
    io.stderr:flush()
end

function g2.search(g, s)
    -- supports "user", "planet", "fleet", "fleet target:", "planet owner:", "planet -neutral -team:", "user -team:"
    local args = {}
    for v in s:gmatch("%S+") do
        args[#args + 1] = v
    end
    local notNeutral = args[2] == "-neutral"
    local filter = notNeutral and args[3] or args[2]
    local filterType, n
    if filter then
        filterType, n = filter:match("(.+):(.+)")
    end
    local objects = {}
    for _, o in pairs(g.items) do
        if o.type == args[1] then
            if not notNeutral or not o.neutral then
                if
                    not filter or (filterType == "target" and tonumber(n) == o.target) or
                        (filterType == "owner" and tonumber(n) == o.owner) or
                        (filterType == "-team" and tonumber(n) ~= (o.team or g.items[o.owner].team))
                 then
                    objects[#objects + 1] = o
                end
            end
        end
    end
    return objects
end

return g2
