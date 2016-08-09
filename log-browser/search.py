import parser
from phylter.backends import backends
import mongolog_backend
import pymongo
import log
import argparse

backends.insert(0,mongolog_backend.MongoLogBackend)

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--system')
arg_parser.add_argument('--log')
arg_parser.add_argument('query', metavar='query')

args = arg_parser.parse_args()

l = log.LogFactory().create_log(args.system, args.log)

query_parser = parser.Parser()
query = query_parser.parse(args.query)

for item in query.apply(l.collection()):
    print l.template().to_string(item)