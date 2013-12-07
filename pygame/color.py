

class Color(object):
    def __init__(self, *args):
        if len(args) == 4:
            r, g, b, a = args
        else:
            raise NotImplementedError("implement me")
        self.r = r
        self.g = g
        self.b = b
        self.a = a
