class Item:
    def __init__(self, **args):
        self.__dict__ = args

    def getCopy(self):
        newone = Item()
        newone.__dict__.update(self.__dict__)
        return newone


class Galaxy:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = ''
        self.items = {}
        self.you = 0
