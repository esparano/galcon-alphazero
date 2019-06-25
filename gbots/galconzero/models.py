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
