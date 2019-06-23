# Frequently Asked Questions

## How are wins calculated when a game hits the timeout?

    The win is given to the player with the most production.  In the case of a
    tie, the player with most ships wins.

## Can I use the same license key for two bots?

    Somewhat. You may change the name of your bot anytime you want. However,
    on a given server they will compete as a single bot, sharing the same 
    score and never battling.

## What is the order of precedence for configuration sources?

    1. Command line options
    2. Configuration file
    3. Default values

## What does -speed=0 do?

    When setting the speed to zero, the game will run in a turn-based mode.
    Bots will be given up to one second to reply before continuing.  Locally
    this will appear about the same as speed=12.  With remote users with lag,
    speeds will vary.

## Why has the game slowed to one tick per second when using -speed=0?

    If a bot stops responding, the game will continue to give it one tick per
    second to respond before continuing.  Once the bot disconnects, the round
    will end.

## What is -wait for?

    Wait determines the maximum wait between rounds.  This should usually be set
    to a value greater than zero to ensure that the bot pairing changes from
    round to round.  However, when only battling two bots, a zero wait will work
    as expected.

## How do I tell if a planet is neutral?

    isNeutral := (Items[planet.Owner].Team == 0)