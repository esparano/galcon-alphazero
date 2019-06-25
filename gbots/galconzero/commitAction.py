from log import send
from actions import SEND_ACTION, REDIRECT_ACTION


def commitAction(action):
    if action[0] == SEND_ACTION:
        (_, source, target, perc) = action
        send("/SEND {} {} {}\n".format(perc, source, target))
    elif action[0] == REDIRECT_ACTION:
        (_, source, target) = action
        send("/REDIR {} {}\n".format(source, target))
