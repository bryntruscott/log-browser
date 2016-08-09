# -*- coding: utf-8 -*-
from phylter.backends.base import Backend
from phylter.conditions import Condition, EqualsCondition, GreaterThanCondition, GreaterThanOrEqualCondition, \
	LessThanCondition, LessThanOrEqualCondition, AndOperator, OrOperator, ConditionGroup, Operator
import pymongo


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
			}[obj.__class__]

			# exp = '"%s": {"%s": %s}' % (obj.left, op, obj.right)
			exp = {obj.left: {op: self.get_compatible_value(obj.right)}}
			return exp
			# return Q(**{f: self.get_compatible_value(obj.right)})

		# if isinstance(obj, ConditionGroup):
		# 	return Q(self.to_q(obj.item))
        #
		if isinstance(obj, Operator):
			if isinstance(obj, AndOperator):
				return {"$and": [self._to_query(obj.left), self._to_query(obj.right)]}
				# return '$and: [{%s}, {%s}]' % (self._to_query(obj.left), self._to_query(obj.right))

			if isinstance(obj, OrOperator):
				return {"$and": [self._to_query(obj.left), self._to_query(obj.right)]}
				# return '$or: [{%s}, {%s}]' % (self._to_query(obj.left), self._to_query(obj.right))

		raise Exception("Unexpected item found in query: %s" % obj)

