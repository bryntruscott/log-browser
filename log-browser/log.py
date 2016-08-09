import pymongo

class Log(object):

    def __init__(self, system, log_name):
        self.__database = system
        self.__collection_name = log_name
        self.__collection = pymongo.MongoClient()[self.__database][self.__collection_name]

    def get_first(self):
        cursor = self.__collection.find().sort("time", pymongo.ASCENDING)
        return cursor.next()

    def get_last(self):
        cursor = self.__collection.find().sort("time", pymongo.DESCENDING)
        return cursor.next()

class LogFactory(object):

    @classmethod
    def create_log(cls, system, log_name):
        return Log(system, log_name)