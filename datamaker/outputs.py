class StdOutOutputer(object):
    def __init__(self, output_key=False):
        self.output_key = output_key

    def handle(self, key, value):
        if self.output_key:
            print('%s -> %s' % (key, value))
        else:
            print(value)
