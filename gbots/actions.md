# Actions Reference

At its heart, Galcon BOTS is a set of command line tools to enable you to
engage in Galcon bot battles. All of the options can be changed via command line
or via the config file. 

---

## LAUNCHER

Use launcher to start up a server and bots using a human user interface.

    ./gbots launcher

The launcher will start automatically when gbots is started non-interactively.

### options

    -config string
        config file
    -cols int
        screen cols [80 ... 160] (default "80")
    -rows int
        screen rows [25 ... 80] (default "25")
    -window string
        set fixed window size (e.g. 1920x1080)

---

## PRACTICE

Use practice to try out the game as a human.

    ./gbots practice

The practice mode has a basic user interface, not the full human centric UI.

### options

    -handicap string
        user handicap e.g. "player+100,enemy+50"
    -config string
        config file
    -window string
        set fixed window size (e.g. 1920x1080)

---

## SERVER

Use server to start up your own server to host bot battles.

    ./gbots server

Server has many customization flags.  You can adjust the bots and their
handicaps.

    ./gbots server -bots=min,max,classic -handicap=classic+100

You can also adjust the speed and wait between rounds.

    ./gbots server -speed=0 -wait=1

You may also allow multiple of the same bot to connect for more concurrency.

    ./gbots server -clones=16

You can log all matches played.

    ./gbots server -logs=./logs

### options

    -headless bool
        disable graphical view
    -speed float
        simulation speed [0=turns, 0 ... 12] (default "1.0")
    -timeout float
        turn timeout (only applies when -speed=0) [0=none, 0 ... 60] (default "1.0")
    -timer int
        round timer [5 ... 3600] (default "60")
    -wait int
        maximum wait between rounds [0 ... 60] (default "5")
    -bots string
        enable builtin bots [all,noop,rand,min,max,sqrt,xor,mixor,classic,none] (default "all")
    -clones int
        clones per player [1 ... 16] (default "1")
    -port int
        port (default "2600")
    -handicap string
        user handicap e.g. "player+100,enemy+50"
    -key string
        license key (required)
    -config string
        config file
    -logs string
        log folder
    -gzip bool
        gzip logs
    -verbose bool
        verbose error handling
    -window string
        set fixed window size (e.g. 1920x1080)

---

## CLIENT

Use client to join the server with a human user interface.

    ./gbots client

The client mode user interface is limited.

### options

    -name string
        user name (default "anonymous")
    -port int
        port (default "2600")
    -key string
        license key (required)
    -config string
        config file
    -window string
        set fixed window size (e.g. 1920x1080)

---

## PROXY

Use proxy to watch online server games in realtime and log matches for replay
and analysis.

    ./gbots proxy -logs=./logs

To save CPU run the proxy in -headless.  To save disk space, run the proxy with
the -gzip flag.

### options

    -headless bool
        disable graphical view
    -port int
        port (default "2600")
    -host string
        hostname (default "bots.galcon.com")
    -config string
        config file
    -logs string
        log folder
    -gzip bool
        gzip logs
    -proxy int
        proxy port (default "2600")
    -window string
        set fixed window size (e.g. 1920x1080)

---

## PIPE

Use pipe to connect bots to a server.

    ./gbots pipe -exec 'lua bot.lua'

Use pipe to connect multiple clones of a single bot.

    ./gbots pipe -clones 16 -exec 'lua bot.lua'

Or just:

    ./gbots pipe lua bot.lua

Use pipe without -exec when your bot is starting the process.

    r,w = popen("./gbots pipe") # pseudocode

Pipe will automatically log in your bot.  Be sure to supply -name and -key.

### options

    -name string
        user name (default "anonymous")
    -clones int
        clones per player [1 ... 16] (default "1")
    -port int
        port (default "2600")
    -host string
        hostname (default "localhost")
    -key string
        license key (required)
    -config string
        config file
    -exec string
        command

---

## REPLAY

Use replay to replay logs recorded by the proxy.

    ./gbots replay -file=<log_name>

Or just:

    ./gbots replay [options] <log_name>

You may use -speed to watch replays in slow or fast-motion.

### options

    -speed float
        simulation speed [0=turns, 0 ... 12] (default "1.0")
    -config string
        config file
    -file string
        log name (required)
    -window string
        set fixed window size (e.g. 1920x1080)
