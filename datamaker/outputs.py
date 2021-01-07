class StdOutOutputer:
    def __init__(self, output_key=False):
        self.output_key = output_key

    def handle(self, key, value):
        if self.output_key:
            print('%s -> %s' % (key, value))
        else:
            print(value)

    def finished_record(self):
        pass


class TemplateOutput:
    def __init__(self, template_engine):
        self.engine = template_engine
        self.current = {}

    def handle(self, key, value):
        self.current[key] = value

    def finished_record(self):
        rendered = self.engine.process(self.current)
        print(rendered)
        self.current.clear()
