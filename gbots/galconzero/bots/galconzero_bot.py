import sys
import random
import cProfile

from uctsearch.galconZeroMcts import GalconZeroMcts
from domain.models import Galaxy, Item
from gzutils import logger, actionUtils
from evaluator.nnEval import NNEval

galconZeroMcts = GalconZeroMcts()
evaluator = NNEval()

from evaluator.simpleEvaluator import SimpleEvaluator
# evaluator = SimpleEvaluator()


################################################################################


def bot(g):
    action = galconZeroMcts.getBestMove(
        g, iterationLimit=10, evaluator=evaluator, batchSize=2, surrenderEnabled=True, saveTrainingData=True)
    actionUtils.commit(action)

################################################################################


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
        logger.send("/TOCK")
    elif t[0] == "/PRINT":
        logger.log("\t".join(t[1:]))
    elif t[0] == "/RESULTS":
        galconZeroMcts.reportGameOver(g, int(t[4]))
        logger.log("\t".join(t[1:]))
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
            ships=float(t[3])/100,
            x=float(t[4])/100,
            y=float(t[5])/100,
            production=float(t[6])/100,
            radius=float(t[7])/100,
            neutral=int(t[2]) == 1,  # TODO: this is probably unstable???
        )
        g.items[o.n] = o
    elif t[0] == "/FLEET":
        o = Item(
            n=int(t[1]),
            type="fleet",
            owner=int(t[2]),
            ships=float(t[3])/100,
            x=float(t[4])/100,
            y=float(t[5])/100,
            source=int(t[6]),
            target=int(t[7]),
            radius=float(t[8])/100,
            xid=int(t[9]),
        )
        g.items[o.n] = o
    elif t[0] == "/DESTROY":
        n = int(t[1])
        if n in g.items:
            del(g.items[n])
    elif t[0] == "/ERROR":
        logger.log("\t".join(t[1:]))
    else:
        logger.log("unhandled command: " + "\t".join(t))


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
                    o.x = float(v)/100  # TODO: verify normalization is working
                elif k == 'Y':
                    o.y = float(v)/100
                elif k == 'S':
                    o.ships = float(v)/100
                elif k == 'R':
                    o.radius = float(v)/100
                elif k == 'O':
                    o.owner = float(v)
                    o.neutral = o.owner == 1
                elif k == 'T':
                    o.target = float(v)
        else:
            i += nFields


if __name__ == "__main__":
    # cProfile.run('main()', "savedStats")
    main()
