# -*- coding: utf-8 -*-
from phylter.backends.base import Backend
from phylter.conditions import Condition, EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, \
    LessThanCondition, LessThanOrEqualCondition, AndOperator, OrOperator, ConditionGroup, Operator
from conditions import RegexMatchCondition
import pymongo
import datetime


class MongoLogBackend(Backend):

    @staticmethod
    def supports(o):
        return isinstance(o, pymongo.collection.Collection)

    def apply(self, query, iterable):
        # don't see how I would handle multiple queries here, so just return the results of the first one
        for o in query.query:
            q = self._to_query(o)
            print q
            return iterable.find(q)

    def _to_query(self, obj):
        if isinstance(obj, Condition):
            op = {
                EqualsCondition: "$eq",
                GreaterThanCondition: "$gt",
                GreaterThanOrEqualCondition: "$gte",
                LessThanCondition: "$lt",
                LessThanOrEqualCondition: "$lte",
                RegexMatchCondition: "$regex",
            }[obj.__class__]

            # exp = '"%s": {"%s": %s}' % (obj.left, op, obj.right)
            exp = {obj.left: {op: self.get_compatible_value(obj.right)}}
            return exp
            # return Q(**{f: self.get_compatible_value(obj.right)})

        # if isinstance(obj, ConditionGroup):
        #     return Q(self.to_q(obj.item))
        #
        if isinstance(obj, Operator):
            if isinstance(obj, AndOperator):
                return {"$and": [self._to_query(obj.left), self._to_query(obj.right)]}
                # return '$and: [{%s}, {%s}]' % (self._to_query(obj.left), self._to_query(obj.right))

            if isinstance(obj, OrOperator):
                return {"$and": [self._to_query(obj.left), self._to_query(obj.right)]}
                # return '$or: [{%s}, {%s}]' % (self._to_query(obj.left), self._to_query(obj.right))

        raise Exception("Unexpected item found in query: %s" % obj)

    def get_compatible_value(self, value, field_type=None):
        if field_type is None:
            # see if we have a datetime value
            try:
                dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                return dt
            except Exception, e:
                # not a datetime. never mind
                pass

        return super(MongoLogBackend, self).get_compatible_value(value, field_type)

