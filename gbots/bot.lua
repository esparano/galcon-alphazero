-- bot.lua
-- Copyright (c) 2019 Phil Hassey

-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:

-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.

-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

-- Galcon is a registered trademark of Phil Hassey
-- For more information see http://www.galcon.com/

function send(msg) io.stdout:write(msg..'\n') ; io.stdout:flush() end
function log(line) io.stderr:write(line .. '\n') ; io.stderr:flush() end

--------------------------------------------------------------------------------

function bot(g)
    local all,mine = {},{}
    for _,o in pairs(g.items) do
        if o.type == "planet" then
            all[#all+1] = o
            if o.owner == g.you then
                mine[#mine+1] = o
            end
        end
    end
    if #all == 0 or #mine == 0 then return end
    local source = mine[math.random(1,#mine)]
    local target = all[math.random(1,#all)]
    send(string.format("/SEND %d %d %d", 5*(math.random(1,20)), source.n, target.n))
end

--------------------------------------------------------------------------------

function main()
    local g = {you=0,state='',items={}}
    while true do
        local line = io.stdin:read()
        if line == nil then break end
        if #line > 0 then
            parse(g, line)
        end
    end
end

function split(str,delim)
    local r = {}
    for k in (str..delim):gmatch("([^"..delim.."]*)"..delim) do
        r[#r+1] = k
    end
    return r
end
function join(t,delim) return table.concat(t,delim) end
function slice(t,a,b)
    local r = {}
    for i=a,b do r[i-a+1] = t[i] end
    return r
end
function toint(v) return math.floor(tonumber(v)) end

function parse(g,line)
    local t = split(line,'\t')
	if t[1]:sub(1,1) ~= '/' then return sync(g,t) end
    if t[1] == "/TICK" then
        bot(g)
        send("/TOCK")
    elseif t[1] == "/PRINT" then
        log(join(slice(t,2,#t),'\t'))
    elseif t[1] == "/RESULTS" then
        log(join(slice(t,2,#t),'\t'))
    elseif t[1] == "/RESET" then
        for k,v in pairs(g) do g[k] = nil end
        g.you = 0; g.state=''; g.items={}
    elseif t[1] == "/SET" then
        if t[2] == "YOU" then g.you = toint(t[3])
        elseif t[2] == "STATE" then g.state = t[3] end
    elseif t[1] == "/USER" then
		local n = toint(t[2])
		g.items[n] = {
			n=     n,
			type=  "user",
			name=  t[3],
			color= tonumber(t[4],16),
			team=  toint(t[5]),
		}
    elseif t[1] == "/PLANET" then
		local n = toint(t[2])
		g.items[n] = {
			n=          n,
			type=       "planet",
			owner=      toint(t[3]),
			ships=      tonumber(t[4]),
			x=          tonumber(t[5]),
			y=          tonumber(t[6]),
			production= tonumber(t[7]),
			radius=     tonumber(t[8]),
		}
    elseif t[1] == "/FLEET" then
		local n = toint(t[2])
		g.items[n] = {
			n=      n,
			type=   "fleet",
			owner=  toint(t[3]),
			ships=  tonumber(t[4]),
			x=      tonumber(t[5]),
			y=      tonumber(t[6]),
			source= toint(t[7]),
			target= toint(t[8]),
			radius= tonumber(t[9]),
		}
    elseif t[1] == "/DESTROY" then
        local n = toint(t[2])
        g.items[n] = nil
    elseif t[1] == "/ERROR" then
        log(join(slice(t,2,#t),'\t'))
    else
        log("unhandled command: " .. join(t,'\t'))
    end
end

function sync(g,t)
	local nFields, fields = #t[1], t[1]:upper()
    local i = 2
    while i <= #t do
		local n = toint(t[i])
        i = i + 1
        local o = g.items[n]
        if o ~= nil then
			for j=1,nFields do
				local v = t[i]
                i = i + 1
                local f = fields:sub(j,j)
                if f == 'X' then o.x = tonumber(v)
                elseif f == 'Y' then o.y = tonumber(v)
                elseif f == 'S' then o.ships = tonumber(v)
                elseif f == 'R' then o.radius = tonumber(v)
                elseif f == 'O' then o.owner = toint(v)
                elseif f == 'T' then o.target = toint(v)
                end
            end
        else
            i = i + nFields
        end
    end
end

main()