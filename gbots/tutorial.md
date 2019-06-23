# Tutorial

At its heart, Galcon BOTS is a set of command line tools to enable you to
engage in Galcon bot battles. All of the options can be changed via command line
or via the config file. 

Galcon BOTS includes a GUI to assist in launching all the sub-processes. On
Windows click on `run-launcher`.  On Mac just click on the app. You will be able
to modify the config file via the config tab (or your favorite text editor.)

    gbots launcher

![Launcher](https://www.galcon.com/bots/shots/launcher.png)

## Setup

Click on the app to start the setup process. Be ready to paste in your license
keys. You will get to name `len(keys)-1` bots.

    gbots setup

## Practice

If you are new to Galcon, try out the [practice] tab. You can adjust the
difficulty in the config tab by giving yourself or the enemy a handicap.

    gbots practice -handicap player+100,enemy+0

## Server

Next, check out the [server] tab and watch some bots battle it out.  You can
adjust the speed of the battles, which bots, and handicap via the config.

    gbots server -speed 12 -bots rand,sqrt,classic -handicap sqrt+100

![Server](https://www.galcon.com/bots/shots/server-16.png)

## Client

You can play on the local server yourself by starting up the [client].

    gbots client -name phil

## Bots

You can also add your own bots to the server. In config, set the exec command
of your bots. Then press enter in the [bots] tab to start your bots.

    gbots pipe -name bot -exec 'python bot.py'

To run a pipe/bot command from the launcher, update the config:

    [cuzco]
    name=cuzco
    action=pipe
    exec=python cuzco.py

The name you give to the ini section can be launched directly from the command
line:

    gbots cuzco

For bots to work you must first start the server or proxy.

![Bots](https://www.galcon.com/bots/shots/bots-live.png)

## Replays

If logging is enabled, you can use the [replays] tab to re-watch previous
matches.

    gbots replay logs/1234567890.log

![Replays](https://www.galcon.com/bots/shots/replays.png)

## Proxy

Once your bots are ready you can pit them against the world.  Start up the
[proxy] instead of the server and your bots will play online.

    gbots proxy
    
    gbots proxy -headless

![Proxy](https://www.galcon.com/bots/shots/proxy-4.png)

## Stats

See how your bots are competing world wide in the [stats] tab.

## Config

Use the config tab to change the options. Any section that has `action=pipe`
will appear in the bots tab. Any other section with an `action` will appear
as its own tab.

    vi config.ini

![Config](https://www.galcon.com/bots/shots/config.png)

## Help

For further help, please check out the [faq], or read the documentation for
each of the [actions].  There is also a spec for the [protocol] available.

    less tutorial.md
    less faq.md
    less actions.md
    less protocol.md






