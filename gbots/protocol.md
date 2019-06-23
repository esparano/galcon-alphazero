# PROTOCOL

All messages should be tab-delimited with a linebreak '\n' between each command.
CLIENT messages may be space-delimited instead of tab-delimited.  CLIENT
messages may be in any case.  

## CLIENT to SERVER messages:

    /LOGIN NAME TOKEN
    /SEND PERCENT SOURCE TARGET [XID]
    /REDIR SOURCE TARGET
    /SURRENDER
    /TOCK
    /PING VALUE
    MESSAGE

## SERVER to CLIENT messages:

    /SET KEY VALUE
        YOU ID
        SPEED SPEED
        STATE STATE
    /RESET
    /USER ID NAME COLOR TEAM XID
    /PLANET ID OWNER SHIPS X Y PRODUCTION RADIUS
    /FLEET ID OWNER SHIPS X Y SOURCE TARGET RADIUS XID
    /CANCEL XID
    FIELDS (ID VALUES) ...
    /DESTROY ID
    /TICK DURATION
    /RESULTS LOG ...
    /PONG VALUE
    /PRINT MESSAGE
    /ERROR MESSAGE

## Type definitions

    FIELDS:
        X -> X
        Y -> Y
        S -> SHIPS
        R -> RADIUS
        O -> OWNER
        T -> TARGET

    STRING: UTF-8 encoded
    NUMBER: floating point encoded decimal
    NAME: /^[a-zA-Z][a-zA-Z0-9\\.\\_\\-]{2,15}$/
    TOKEN: unspecified
    ID: unsigned integer
    SOURCE, TARGET, TEAM, OWNER: ID
    PERCENT: integer [1,100]
    X, Y, SHIPS, PRODUCTION, RADIUS: NUMBER
    MESSAGE: STRING
    LOG: STRING
    COLOR: /^[a-fA-F0-9]{6}$/
    XID: integer
    KEY, VALUE: STRING
    DURATION: NUMBER in seconds
    


