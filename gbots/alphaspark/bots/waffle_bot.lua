-- Lua bot must use ./gbots pipe -exec lua bot.lua

--------------------------------------------------------------------------------
--[[local file = io.open("C:/Users/Owner/Desktop/Folder/gbots/log", "w")
print = function(...)
	local t = {...}
	for i = 1, select("#", ...) do
		t[i] = tostring(t[i])
	end
	file:write(table.concat(t, "\t").."\n")
end]]

local json = require "alphaspark/bots/json"

local trainingDataFile = io.open("D:\\GalconZero\\Waffle\\train.jsonl", "a")
local trainingGame = {}
function bot(g)
	g = deepcopy(g)
	for i,item in pairs(g.items) do
		if item.ships ~= nil and item.ships < 0 then 
			logln('ERROR, NEGATIVE SHIPS ENCOUNTERED')
			logln(item.ships)
			
		end
	end
	trainingGame.frames = trainingGame.frames or {}
	trainingGame.playerN = trainingGame.playerN or g.you

	local savedData = {}
	savedData.items = CleanNils(g.items)

	local action = _bot(g)
	local actions = {}
	if action then actions[1] = action end
	savedData.actions = actions
	table.insert(trainingGame.frames, savedData)
end

function bot_gameOver(g, winner)
	trainingGame.winnerN = winner
	trainingDataFile:write(json.encode(trainingGame), "\n")

	trainingGame = {}
end

function deepcopy(orig)
    local orig_type = type(orig)
    local copy
    if orig_type == 'table' then
        copy = {}
        for orig_key, orig_value in next, orig, nil do
            copy[deepcopy(orig_key)] = deepcopy(orig_value)
        end
        setmetatable(copy, deepcopy(getmetatable(orig)))
    else -- number, string, boolean, etc
        copy = orig
    end
    return copy
end

function CleanItem(orig)
	local item = deepcopy(orig)
	item.is_fleet = nil
	item.is_planet = nil
	item.is_user = nil
	item.name = nil
	item.color = nil
	item.radius = nil
	-- rename and delete
	if item.ships ~= nil and item.ships < 0 then 
		logln(item.ships)
	end
	item.s = item.ships
	item.ships = nil
	item.p = item.production
	item.production = nil
	-- INCLUDED FOR DEBUGGING PURPOSES FOR NOW
	-- item.n = nil
	return item
end

function CleanNils(t)
	local ans = {}
	for _,v in pairs(t) do
	  ans[ #ans+1 ] = CleanItem(v)
	end
	return ans
end

local memory = {}
function _bot(g)
	local abs, floor, ceil, max, min, HUGE, random, PI, sqrt, sort = math.abs, math.floor, math.ceil, math.max, math.min, math.huge, math.random, math.pi, math.sqrt, table.sort
	local function distance(a,b)local dx,dy=b.x-a.x,b.y-a.y return sqrt(dx*dx+dy*dy)end
	local G,USER=g.items,g.you
	local FIRST=not memory.init
	if FIRST then memory.init=true end
	local uteam=G[USER].team
	local homes,eteam=memory.homes,memory.eteam
	if not homes or (homes[uteam] and homes[uteam].owner ~= USER) then
		homes={}
		for _,v in pairs(G)do
			if v.is_planet and not v.neutral then
				local o=v.team
				local h=homes[o]
				if not h or h.production<v.production then
					homes[o]=v
				end
			end
		end
		for k,v in pairs(homes)do if k~=uteam then memory.eteam,eteam=k,k end end
		if homes[uteam] then
			memory.homes=homes
		end
	end
	homes = memory.homes
	local home,ehome=homes[uteam],homes[eteam]
	local ships,total,tprod,myprod=0,0,0,0
	local enemies,eprod={},{}
	local data={planets={},neutral={},myplanets={},myteam={},eplanets={},others={},fleets={},myfleets={},efleets={},mystuff={}}
	for _,p in pairs(G)do
		local o,s=p.team,p.ships
		if not p.is_user and not p.neutral then
			if o==uteam then
				ships=ships+s
			elseif not enemies[o]then
				enemies[o]=s
			else
				enemies[o]=enemies[o]+s
			end
			total=total+s
		end
		if p.is_planet then
			data.planets[#data.planets+1]=p
			if p.neutral then
				data.neutral[#data.neutral+1]=p
				data.others[#data.others+1]=p
			else
				tprod=tprod+p.production
				if o==uteam then
					data.myteam[#data.myteam+1]=p
					if p.owner==USER then
						myprod=myprod+p.production
						data.myplanets[#data.myplanets+1]=p
						data.mystuff[#data.mystuff+1]=p
					end
				else
					local x=eprod[o]
					if not x then
						eprod[o]=p.production
					else
						eprod[o]=x+p.production
					end
					data.others[#data.others+1]=p
					data.eplanets[#data.eplanets+1]=p
				end
			end
		elseif p.is_fleet then
			data.fleets[#data.fleets+1]=p
			if p.team==uteam then
				data.myfleets[#data.myfleets+1]=p
				data.mystuff[#data.mystuff+1]=p
			else
				data.efleets[#data.efleets+1]=p
			end
		end
	end
	if ehome and tprod >= myprod*2 then
		local dist, closest = HUGE, home
		for _, a in pairs(data.myplanets) do
			for _, b in pairs(data.eplanets) do
				local d = distance(a, b)
				if dist > d then dist, closest = d, a end
			end
		end
		ships = ships + dist*closest.production/2000
	end
	local planets,control=data.myplanets,ships/total
	if FIRST and home and #data.neutral~=0 then
		local function path(f,t,set)
			local ft=distance(f,t)
			for i=1,#set do local p=set[i]
				if p~=f and p~=t then
					local pt=distance(p,t)
					if pt<ft then
						local fp=distance(f,p)
						if fp<ft and(pt+fp-p.r*2)<ft then
							t,ft=p,fp
						end
					end
				end
			end
			return t
		end
		local function recovertime(a,b)
			local r=b.ships-a.ships
			if r<0 then
				return distance(a,b)/20+b.ships*50/b.production
			elseif a.is_planet then
				return distance(a,b)/20+b.ships*50/b.production+r*50/a.production
			else
				return HUGE
			end
		end
		local function pathlength(f,t,set)
			local d=0
			for i=1,20 do
				if f==t then break end
				local F=path(f,t,set)
				d=d+distance(f,F)
				f=F
			end
			return d
		end
		local eeval,enemy=HUGE
		for _,v in pairs(data.eplanets)do
			local n=distance(v,home)
			if eeval>n then eeval,enemy=n,v end
		end
		if not enemy then
			local eeval=-HUGE
			for _,v in pairs(data.others)do
				local n=distance(v,home)
				if n>eeval then eeval,enemy=n,v end
			end
		end
		local p,expand=data.neutral,{}
		local rt={}for _,v in pairs(p)do rt[v]=recovertime(home,v)end
		sort(p,function(a,b)return rt[a]<rt[b]end)
		local c=home.ships
		local cinit,ships,n,excess=c,c,0,0
		local benefit=home.production*distance(enemy,home)/2000
		local prod=home.production
		for i=1,#p do local v=p[i]
			if home and enemy and distance(enemy,v)<distance(home,v)then break end
			local s=max(1,v.ships+1)
			local ben=((distance(enemy,v)-pathlength(home,v,expand))/40)*v.production/50-s
			local liability = s - max(c, 0)
			if c<s then
				ben=ben-(excess+liability)*v.production/prod
			end
			if benefit+ben+c>cinit then
				if c < s then
					excess = excess + liability
				end
				benefit=benefit+ben
				c=c-s
				if c>0 then prod=prod+v.production end
				expand[#expand+1]=v
			end
		end
		memory.expand=expand
	end
	local stuff=data.mystuff
	sort(stuff,function(a,b)return a.ships>b.ships end)
	local targets = {}
	for _, p in pairs(data.eplanets) do
		targets[#targets+1] = p
	end
	local defend = myprod/tprod>.5 and control<.8
	if memory.expand then
		local finished = true
		for _,v in pairs(memory.expand)do
			local v=G[v.n]
			if v and v.neutral then
				targets[#targets+1]=v
				finished = false
			end
		end
	end
	local function tunnel(f, t)
		if not t then return end
		local ft = distance(f, t)
		local closest = HUGE
		local final = t
		for _, p in pairs(data.myteam) do
			local fp = distance(f, p)
			if p ~= f and fp < closest then
				local pt = distance(p, t)
				if fp + pt - p.r*2 < ft then
					final, closest = p, fp
				end
			end
		end
		return final
	end
	local selected,maintarget,percent={}
	local danger,help={},{}
	local efleetmap = {}
	local imminent = {}
	local enemyincoming = {}
	for _, f in pairs(data.efleets) do
		local t = f.target
		if not efleetmap[t] then efleetmap[t] = {} end
		efleetmap[t][f.n] = true
		enemyincoming[t] = (enemyincoming[t] or 0) + f.n
		if distance(f, G[t]) < 100 then
			imminent[t] = true
		end
	end
	local attackclosest = tprod > myprod*2 and ships*2 > (total + (tprod - myprod)*distance(home, ehome)/2000*1.5)
	attackclosest = false
	local GetTarget = function(f)
		local teval,t=HUGE
		for _,v in pairs(targets)do
			local s=v.ships
			local dist=distance(f,v)
			if v.neutral then
				for _,x in pairs(data.myfleets)do
					if x~=f and x.target==v.n and distance(x, v) < dist then
						s=s-floor(x.ships)
					end
				end
			else
				s=s+ceil(v.production*dist/2000)
			end
			local defense = v.ships*(v.neutral and 1 or max(1, (enemies[v.owner] or 0)/control))
			local newtotal, newships = total + myprod*dist/2000, ships + myprod*dist/2000
			for _, p in pairs(eprod) do
				newtotal = newtotal + p*dist/2000
			end
			local newcontrol = (ships-defense)/(newtotal-v.ships*(v.neutral and 1 or 2))
			if floor(s)>=0 then
				local n = dist
				if attackclosest then
					if v.neutral then
						n = HUGE
					end
				else
					n = s - v.production/4 + dist/10
					if v.neutral then n = dist/100 end
				end
				if teval>n then teval, t = n, v end
			end
		end
		return t
	end
	for ind, p in pairs(data.myplanets) do
		for ind2, p2 in pairs(data.myplanets) do
			if p ~= p2 and efleetmap[p2.n] and distance(p, p2) < 40 then
				if not efleetmap[p.n] then efleetmap[p.n] = {} end
				for v, _ in pairs(efleetmap[p2.n]) do
					if distance(p, G[v]) < distance(p2, G[v]) then
						efleetmap[p.n][v] = true
						efleetmap[p2.n][v] = nil
					end
				end
			end
		end
	end
	local captureTime = {}
	for ind,f in pairs(data.myplanets)do
		local available,dist=floor(f.ships),HUGE
		for _, n in pairs(data.neutral) do
			if efleetmap[n.n] and distance(n, f) < 100 then
				if not efleetmap[f.n] then efleetmap[f.n] = {} end
				for v, _ in pairs(efleetmap[n.n]) do
					efleetmap[f.n][v] = true
				end
			end
		end
		if efleetmap[f.n] then
			for v, _ in pairs(efleetmap[f.n]) do
				local v = G[v]
				available = available - ceil(v.ships)
				dist = min(dist, distance(v, f) - f.r - v.r)
			end
		end
		captureTime[f.n] = dist
		if dist == HUGE then dist = 0 end
		local h=0
		for _,v in pairs(data.myfleets)do
			if v.target==f.n then
				h=h+v.ships
			end
		end
		help[f]=h
		danger[f]=floor(available+f.production*dist/2000)
	end
	for ind,f in pairs(stuff)do
		if f.is_planet then
			local available=danger[f]or f.ships
			local t0=GetTarget(f)
			local t=tunnel(f,t0)
			local low,t2=0
			for _,v in pairs(data.myplanets)do
				local d=(danger[v]or v.ships)+(help[v]or 0)
				if d<low then low,t2=d,v end
			end
			local defend = defend
			if t2 and imminent[t2.n] then defend = true end
			if t2 and defend then
				if t then
					local d = distance(t, f)
					if not t.neutral and (d>distance(t2,f)*1.5 or distance(t2, t) < d) and t2 ~= f then t=t2 end
				else
					t=t2
				end
			end
			if t then
				if distance(f, t)*2 < (captureTime[f.n] or math.huge) then
					available = f.ships
				end
				if available > 0 then
					if not maintarget then maintarget=t end
					if maintarget~=t and t0 then
						if distance(f,t0)+10>distance(f,maintarget)+distance(maintarget,t0)-maintarget.r*2 then
							t=maintarget
						end
					end
					local a=floor(available*20/f.ships)*5
					a = math.floor(a/25)*25
					if a > 0 and a < math.huge then
						if t.neutral then a=min(a,ceil((t.ships+1)*20/f.ships)*10)end
						if not percent then percent=a end
						f.ships=f.ships-floor(ceil(a*20/f.ships)*f.ships/20+.5)
						local action = string.format("/SEND %d %d %d", math.floor(a+.5), f.n, t.n)
						send(action)
						return action
					end
				end
			end
		else
			local newtarget = GetTarget(f)
			local t=tunnel(f, newtarget)
			local low,t2=0
			local targ=G[f.target]
			for _,v in pairs(data.myplanets)do
				local d=(danger[v]or v.ships)+(help[v]or 0)
				if v==targ then d=d-f.ships end
				if d<low then low,t2=d,v end
			end
			local defend = defend
			if t2 and imminent[t2.n] then defend = true end
			if t2 and defend then
				if t then
					local d = distance(t, f)
					if not t.neutral and (d>distance(t2,f)*1.5 or distance(t2, t) < d) then t=t2 end
				else
					t=t2
				end
			end
			if t and f.target ~= t.n then
				if not maintarget then maintarget=t end
				f.target=t.n
				local action = string.format("/REDIR %d %d", f.n, t.n)
				send(action)
				return action
			end
		end
	end
end

--------------------------------------------------------------------------------

function main()
    local g = {you=0,state='unknown',items={}}
    while true do
        local line = recv()
        if line == nil then break end
        parse(g, line)
    end
end

function writeTrainingSample(g, actions)
	local gameStateJson = "some game state"
	trainingDataFile:write(gameStateJson, "\n")
end

function recv() return io.stdin:read() end
function send(msg)
	io.stdout:write(msg..'\n') ; 
	io.stdout:flush() 
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
function logln(line) 
	if line ~= nil then 
		io.stderr:write(line .. '\n')
	else
		io.stderr:write('NIL\n')
	end
	io.stderr:flush() 
end
function toint(v) return math.floor(tonumber(v)) end

function parse(g,line)
    if #line == 0 then return end
    local t = split(line,'\t')
	if t[1]:sub(1,1) ~= '/' then return sync(g,t) end
    if t[1] == "/TICK" then
        bot(g)
        send("/TOCK")
    elseif t[1] == "/PRINT" then
        logln(join(slice(t,2,#t),'\t'))
	elseif t[1] == "/RESULTS" then
		bot_gameOver(g,toint(t[5]))
		logln(join(slice(t,2,#t),'\t'))
    elseif t[1] == "/RESET" then
        for k,v in pairs(g.items) do g.items[k] = nil end
        g.you = 0
		memory = {}
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
			neutral = toint(t[5]) == 0, -- compatibility
			is_user = true, -- compatibility
			is_fleet = false, -- compatibility
			is_planet = false, -- compatibility
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
			r = tonumber(t[8]), -- compatibility
			is_planet = true, -- compatibility
			is_fleet = false, -- compatibility
			neutral = toint(t[3]) == 1, -- compatibility
			team = g.items[toint(t[3])].team, -- compatibility
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
			r = tonumber(t[9]), -- compatibility
			is_planet = false, -- compatibility
			is_fleet = true, -- compatibility
			neutral = toint(t[3]) == 1, -- compatibility
			team = g.items[toint(t[3])].team, -- compatibility
		}
	elseif t[1] == "/DESTROY" then
		local n = toint(t[2])
        g.items[n] = nil
    elseif t[1] == "/ERROR" then
        logln(join(slice(t,2,#t),'\t'))
    else
        logln("unhandled command " .. join(t,'\t'))
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
				if toint(v) ~= tonumber(v) then logln("FOUND ONEEEE " .. v) end
                if f == 'X' then o.x = tonumber(v)
                elseif f == 'Y' then o.y = tonumber(v)
                elseif f == 'S' then o.ships = tonumber(v)
                elseif f == 'R' then o.radius = tonumber(v)
                elseif f == 'O' then o.owner = toint(v) o.neutral = toint(v) == 1 o.team = g.items[o.owner].team
                elseif f == 'T' then o.target = toint(v)
                end
            end
        else
            i = i + nFields
        end
    end
end

main()