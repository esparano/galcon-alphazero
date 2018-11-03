require("mod_neural_net")
require("mod_map_helper")
require("mod_features")

local weights = {
    {
        {1, 5, 9},
        {2, 6, 10},
        {3, 7, 11},
        {4, 8, 12}
    },
    {
        {1},
        {1.1},
        {1.2}
    }
}

local evalNet
function initTestEval()
    evalNet = nn.new()
    for i=1,#weights - 1 do
        evalNet:addLayer(weights, "relu", true)
    end
    evalNet:addLayer(weights[#weights], "sigmoid", true)
end
initTestEval(); initTestEval = nil

local function getOtherPlayer(user, userList) 
    for _,other in ipairs(userList) do
        if other.n ~= user.n then
            return other
        end
    end
end

-- eval in range [0, 1] represents confidence in one player winning
-- TODO: make it work for teams or players
function getEval(items, user)
    local m = map.new(items)
    local enemy = getOtherPlayer(user, m:getUserList(false))

    if enemy == nil then
        print("ERROR: testEval: there is only one player")
        return
    end
    local f = features.getAll(m, user, enemy)
    print(f[1])
    print(f[2])
    print(f[3]) -- TODO: WHY ARE THESE UNDEFINED
    print(f[4])
    local outputVector = evalNet:predict(f)
    print(outputVector)
end

function rotateVector(v)
    local rotated = {{}}
    for _,val in ipairs(v) do
        table.insert(rotated[1], val)
    end
    return rotated
end
