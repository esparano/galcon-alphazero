local sparky = require "sparky/sparky_main"

function distance(a, b)
    local dx, dy = b.x - a.x, b.y - a.y
    return math.sqrt(dx * dx + dy * dy)
end

function main()
    g = {you = 0, state = "unknown", items = {}}
    while true do
        local line = recv()
        if line == nil then
            break
        end
        parse(g, line)
    end
end

function recv()
    return io.stdin:read()
end
function send(msg)
    --logln(msg)
    io.stdout:write(msg .. "\n")
    io.stdout:flush()
end
function split(str, delim)
    local r = {}
    for k in (str .. delim):gmatch("([^" .. delim .. "]*)" .. delim) do
        r[#r + 1] = k
    end
    return r
end
function join(t, delim)
    return table.concat(t, delim)
end
function slice(t, a, b)
    local r = {}
    for i = a, b do
        r[i - a + 1] = t[i]
    end
    return r
end
function logln(line)
    io.stderr:write(line .. "\n")
    io.stderr:flush()
end
function toint(v)
    return math.floor(tonumber(v))
end

local meta = {
    __tostring = function(t)
        return t.n
    end,
    __concat = function(a, b)
        return tostring(a) .. tostring(b)
    end
}

local mem = {}
function parse(g, line)
    if #line == 0 then
        return
    end
    local t = split(line, "\t")
    if t[1]:sub(1, 1) ~= "/" then
        return sync(g, t)
    end
    if t[1] == "/TICK" then
        sparky.loop(g, mem)
        send("/TOCK")
    elseif t[1] == "/PRINT" then
        logln(join(slice(t, 2, #t), "\t"))
    elseif t[1] == "/RESULTS" then
        logln(join(slice(t, 2, #t), "\t"))
    elseif t[1] == "/RESET" then
        for k, v in pairs(g.items) do
            g.items[k] = nil
        end
        g.you = 0
        mem = {}
    elseif t[1] == "/SET" then
        if t[2] == "YOU" then
            g.you = toint(t[3])
        elseif t[2] == "STATE" then
            g.state = t[3]
        end
    elseif t[1] == "/USER" then
        local n = toint(t[2])
        g.items[n] =
            setmetatable(
            {
                n = n,
                type = "user",
                name = t[3],
                color = tonumber(t[4], 16),
                team = toint(t[5]),
                user_neutral = n == 1
            },
            meta
        )
    elseif t[1] == "/PLANET" then
        local n = toint(t[2])
        g.items[n] =
            setmetatable(
            {
                n = n,
                type = "planet",
                owner = toint(t[3]),
                ships = tonumber(t[4]),
                x = tonumber(t[5]),
                y = tonumber(t[6]),
                production = tonumber(t[7]),
                radius = tonumber(t[8]),
                owner_n = toint(t[3]),
                ships_value = tonumber(t[4]),
                ships_production = tonumber(t[7]),
                neutral = toint(t[3]) == 1,
                ships_production_enabled = toint(t[3]) ~= 1,
                distance = distance,
                fleet_send = function(f, p, t)
                    local action = string.format("/SEND %d %d %d", math.floor(p + 0.5), f.n, t.n)
                    send(action)
                end
            },
            meta
        )
    elseif t[1] == "/FLEET" then
        local n = toint(t[2])
        g.items[n] =
            setmetatable(
            {
                n = n,
                type = "fleet",
                owner = toint(t[3]),
                owner_n = toint(t[3]),
                ships = tonumber(t[4]),
                fleet_ships = tonumber(t[4]),
                x = tonumber(t[5]),
                y = tonumber(t[6]),
                source = toint(t[7]),
                target = toint(t[8]),
                fleet_target = toint(t[8]),
                radius = tonumber(t[9]),
                neutral = toint(t[3]) == 1,
                distance = distance,
                fleet_redirect = function(self, t)
                    local action = string.format("/REDIR %d %d", n, t.n)
                    send(action)
                end
            },
            meta
        )
    elseif t[1] == "/DESTROY" then
        local n = toint(t[2])
        g.items[n] = nil
    elseif t[1] == "/ERROR" then
        logln(join(slice(t, 2, #t), "\t"))
    else
        logln("unhandled command " .. join(t, "\t"))
    end
end

function sync(g, t)
    local nFields, fields = #t[1], t[1]:upper()
    local i = 2
    while i <= #t do
        local n = toint(t[i])
        i = i + 1
        local o = g.items[n]
        if o ~= nil then
            for j = 1, nFields do
                local v = t[i]
                i = i + 1
                local f = fields:sub(j, j)
                if f == "X" then
                    o.x = tonumber(v)
                elseif f == "Y" then
                    o.y = tonumber(v)
                elseif f == "S" then
                    o.ships = tonumber(v)
                    o.ships_value = o.ships
                    o.fleet_ships = o.ships
                elseif f == "R" then
                    o.radius = tonumber(v)
                elseif f == "O" then
                    o.owner = toint(v)
                    o.owner_n = o.owner
                    o.neutral = o.owner == 1
                    o.ships_production_enabled = o.owner ~= 1
                elseif f == "T" then
                    o.target = toint(v)
                end
            end
        else
            i = i + nFields
        end
    end
end

main()
