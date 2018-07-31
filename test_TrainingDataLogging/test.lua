function init()
    GLOBAL = {
        sw=400,
        sh=300,
    }
    init_pause()
end

function init_game()
    GLOBAL.t=0
    GLOBAL.score=0
    game_over = false

    g2.game_reset()
    g2.state = "pause"
    g2.view_set(0,0,GLOBAL.sw,GLOBAL.sh)
    g2.status = "Score: "..GLOBAL.score
    
    GLOBAL.score_label = g2.new_label("Score: "..GLOBAL.score,GLOBAL.sw/2,20,0xffffff)
end

function loop(t)
    if game_over and g2.state == "pause" then return end
    if game_over and g2.state == "scene" then init_game() end
    if game_over and g2.state == "play" then init_game() end
    GLOBAL.t = GLOBAL.t + t 
    GLOBAL.score_label.label_text = "Score: "..GLOBAL.score
end

function event(e)
    if (e["type"] == "onclick" and e["value"] == "resume") then
        g2.state = "scene"
    end
    if (e["type"] == "onclick" and e["value"] == "restart") then
        init_game()
    end
    if (e["type"] == "onclick" and e["value"] == "add") then
        add()
    end
    if (e["type"] == "onclick" and e["value"] == "continue") then
        local score = GLOBAL.score
        init_game()
        GLOBAL.score = score
    end
    if (e["type"] == "onclick" and e["value"] == "quit") then
        g2.state = "quit"
    end
    if (e["type"] == "pause") then
        init_pause()
    end
end

function init_pause() 
    g2.state = "pause"
    g2.html = ""..
    "<table>"..
    "<tr><td><input type='button' value='ADD' onclick='add' />"..
    "<tr><td><input type='button' value='Resume' onclick='resume' />"..
    "<tr><td><input type='button' value='Restart' onclick='restart' />"..
    "<tr><td><input type='button' value='Quit' onclick='quit' />"..
    "";
end

function add() 
    asdf = {};
    for i=1,2500 do
        asdf[math.random(0, 1000000)] = math.random();
    end
    g2.data = json.encode(asdf);
end

