import pymongo

class LogTemplate(object):
    def __init__(self):
        self._fields = []
        self._layout = ""

    def add_field(self, name):
        self._fields.append(name)

    def set_layout(self, layout):
        self._layout = layout

    def to_string(self, entry):
        values = []
        for name in self._fields:
            values.append(entry.get(name))
        return self._layout.format(*values)

class Log(object):

    def __init__(self, system, log_name, template):
        self._database = system
        self._collection_name = log_name
        self._template = template
        self._collection = pymongo.MongoClient()[self._database][self._collection_name]

    def template(self):
        return self._template

    def collection(self):
        return self._collection

    # def get_first(self):
    #     cursor = self.__collection.find().sort("time", pymongo.ASCENDING)
    #     return cursor.next()
    #
    # def get_last(self):
    #     cursor = self.__collection.find().sort("time", pymongo.DESCENDING)
    #     return cursor.next()

class ApacheAccessTemplate(LogTemplate):
    def __init__(self):
        super(ApacheAccessTemplate, self).__init__()
        self.add_field('_id')
        self.add_field('cloudwatch_log_stream_name')
        self.add_field('host')
        self.add_field('user')
        self.add_field('time')
        self.add_field('path')
        self.add_field('code')
        self.add_field('size')
        self.add_field('referer')
        self.add_field('agent')
        self.set_layout("{} {} {} {} [{}] \"{}\" {} {} \"{}\" \"{}\"")


class ApacheErrorTemplate(LogTemplate):
    def __init__(self):
        super(ApacheErrorTemplate, self).__init__()
        self.add_field('_id')
        self.add_field('cloudwatch_log_stream_name')
        self.add_field('time')
        self.add_field('level')
        self.add_field('pid')
        self.add_field('tid')
        self.add_field('client')
        self.add_field('message')
        self.set_layout("{} {} [{}] [{}] [pid {}:tid {}] [client {}] {}")


class LogFactory(object):

    def __init__(self):
        self._templates = {
            'apache_access': ApacheAccessTemplate(),
            'apache_error': ApacheErrorTemplate(),
        }

    def create_log(self, system, log_name):
        return Log(system, log_name, self._templates[log_name])