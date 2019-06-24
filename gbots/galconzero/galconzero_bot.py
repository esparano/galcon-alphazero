import sys
import random
from galconZeroMcts import getBestMove


def send(msg): sys.stdout.write(msg+"\n"); sys.stdout.flush()


def log(msg): sys.stderr.write(msg+"\n"); sys.stderr.flush()

################################################################################


def bot(g):
    (source, target, perc) = getBestMove(g, iterationLimit=200)
    moveString = "/SEND {} {} {}\n".format(perc, source, target)
    print("SENDING MOVESTRING: " + moveString)
    send(moveString)

################################################################################


class Item:
    def __init__(self, **args):
        self.__dict__ = args


class Galaxy:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = ''
        self.items = {}
        self.you = 0


def main():
    g = Galaxy()
    while True:
        try:
            line = sys.stdin.readline()
        except:
            break
        if not line:
            break
        line = line.rstrip()
        if len(line) == 0:
            continue
        parse(g, line)


def parse(g, line):
    t = line.split("\t")
    if t[0][0] != "/":
        sync(g, t)
        return
    if t[0] == "/TICK":
        bot(g)
        send("/TOCK")
    elif t[0] == "/PRINT":
        log("\t".join(t[1:]))
    elif t[0] == "/RESULTS":
        log("\t".join(t[1:]))
    elif t[0] == "/RESET":
        g.reset()
    elif t[0] == "/SET":
        if t[1] == "YOU":
            g.you = int(t[2])
        elif t[1] == "STATE":
            g.state = t[2]
    elif t[0] == "/USER":
        o = Item(
            n=int(t[1]),
            type="user",
            name=t[2],
            color=int(t[3], 16),
            team=int(t[4]),
            xid=int(t[5]),
            neutral=int(t[1]) == 1,  # TODO: this is probably unstable?
        )
        g.items[o.n] = o
    elif t[0] == "/PLANET":
        o = Item(
            n=int(t[1]),
            type="planet",
            owner=int(t[2]),
            ships=float(t[3]),
            x=float(t[4]),
            y=float(t[5]),
            production=float(t[6]),
            radius=float(t[7]),
            neutral=int(t[2]) == 1,  # TODO: this is probably unstable???
        )
        g.items[o.n] = o
    elif t[0] == "/FLEET":
        o = Item(
            n=int(t[1]),
            type="fleet",
            owner=int(t[2]),
            ships=float(t[3]),
            x=float(t[4]),
            y=float(t[5]),
            source=int(t[6]),
            target=int(t[7]),
            radius=float(t[8]),
            xid=int(t[9]),
        )
        g.items[o.n] = o
    elif t[0] == "/DESTROY":
        n = int(t[1])
        if n in g.items:
            del(g.items[n])
    elif t[0] == "/ERROR":
        log("\t".join(t[1:]))
    else:
        log("unhandled command: " + "\t".join(t))


def sync(g, t):
    nFields, fields = len(t[0]), t[0].upper()
    i = 1
    while i < len(t):
        n = int(t[i])
        i += 1
        if n in g.items:
            o = g.items[n]
            for k in fields:
                v = t[i]
                i += 1
                if k == 'X':
                    o.x = float(v)
                elif k == 'Y':
                    o.y = float(v)
                elif k == 'S':
                    o.ships = float(v)
                elif k == 'R':
                    o.radius = float(v)
                elif k == 'O':
                    o.owner = float(v)
                    o.neutral = o.owner == 1
                elif k == 'T':
                    o.target = float(v)
        else:
            i += nFields


if __name__ == "__main__":
    main()
