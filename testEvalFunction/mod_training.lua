require("mod_map_wrapper")
require("mod_features")

local gameData
function training_startGame()
    gameData = {}
end

-- eval in range [0, 1] represents confidence in one player winning
-- TODO: make it work for teams or players
function training_example(items, user)
    local m = Map.new(items)
    if user == nil then
        -- may happen at the end of a game when one player is dead...
        print("ERROR: testEval: there is only one player")
        return
    end
    local f = features.getAll(m, user)
    for _, val in ipairs(f) do
        -- if any feature is undefined, don't add training data
        -- TODO: stop NaNs in the first place
        if val ~= val then
            print("invalid training data")
            return
        end
    end
    gameData[#gameData + 1] = {userN = user.n, f = copy(f)}
end

function training_endGame(winner)
    -- z = game result
    for _, data in ipairs(gameData) do
        if data.userN == winner.n then
            data.z = 1
        else
            data.z = 0
        end
        data.userN = nil
        for i, feature in ipairs(data.f) do
            data.f[i] = with_precision(feature, 5)
        end
        --data.Q = with_precision(data.Q, 5)
    end
    g2.data = json.encode(gameData)
end

function copy(o)
    if type(o) ~= "table" then
        return o
    end
    local r = {}
    for k, v in pairs(o) do
        r[k] = copy(v)
    end
    return r
end

function with_precision(num, numDecimalPlaces)
    local mult = 10 ^ (numDecimalPlaces or 0)
    return math.floor(num * mult + 0.5) / mult
end
