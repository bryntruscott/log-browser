# -*- coding: utf-8 -*-
import pyparsing

from phylter.conditions import EqualsCondition, GreaterThanCondition, LessThanCondition, GreaterThanOrEqualCondition, \
	LessThanOrEqualCondition, AndOperator, OrOperator, Condition, Operator, ConditionGroup
from conditions import NotEqualsCondition, RegexMatchCondition
from phylter.query import Query
from phylter import parser

operator_signs = ('==', '!=', '>', '<', '>=', '<=', '~')


# allow underscores as well as alpha-numerics in identifiers
identifier = pyparsing.Word(pyparsing.alphanums+'_')
operator = pyparsing.oneOf(operator_signs)
# allow '+' and ':' in value so that date/time values don't need to be quoted
value = pyparsing.quotedString | pyparsing.Word(pyparsing.alphanums+'-'+':')

# covers foo == bar and (foo == bar)
condition = identifier + operator + value | \
			"(" + identifier + operator + value + ")"

and_or = pyparsing.oneOf(['and', 'or'], caseless=True)
andor_field_op_value = and_or + condition

grouped_andor_field_op_value = and_or + "(" + condition + pyparsing.Optional(pyparsing.OneOrMore(andor_field_op_value)) + ")"

pattern = condition + \
		  pyparsing.Optional(pyparsing.OneOrMore(andor_field_op_value | grouped_andor_field_op_value))



# sub-classing my own Parser class seems the best way to allow underscores as well as alpha-numerics in identifiers
# will also add a regex matching condition operator
class Parser(parser.Parser):

	def __init__(self, *args, **kwargs):
		pass

	def parse(self, query):
		chunks = parser.ConsumableIter(pattern.parseString(query, parseAll=True))
		return self.build_query(chunks)

	def build_query(self, consumable):
		l = []

		# parse groups first
		while consumable.has_more:
			if consumable.current == '(':
				consumable.consume()  # consume (
				end = self.find_group_end(consumable[consumable.pos:])
				sub = consumable[consumable.pos:consumable.pos+end] # extract group content
				consumable.consume(end+1) # consume the whole group
				sub_query = self.build_query(sub) # parse the group
				if len(sub_query.query) != 1:
					raise Exception()
				l.append(ConditionGroup(sub_query.query.iterable[0]))
			else:
				l.append(consumable.consume())

		consumable = parser.ConsumableIter(l)
		l = []

		# replace condition tuples with *Condition instances
		while consumable.has_more:
			if consumable.current in ('and', 'or') or isinstance(consumable.current, ConditionGroup):
				l.append(consumable.consume())
			else:
				if consumable.next in operator_signs:
					left, operator, right = tuple(consumable.consume(3))
					condition = self._get_condition_class(operator)(left, right)
					l.append(condition)
				else:
					raise Exception("Unexpected tokens found: %s" % consumable.iterable[consumable.pos:])

		assert all((isinstance(x, (Condition, ConditionGroup)) or x in ('and', 'or') for x in l))

		l = parser.ConsumableIter(l)
		# replace all operator with *Operator instances, from the lowest to the highest binding
		for op in ('or', 'and'):
			op_clazz = self._get_operator_class(op)
			l2 = []
			last = None

			while l.has_more:
				current = l.consume()

				if isinstance(current, Condition) or isinstance(current, Operator):
					last = current
				else:
					if current == op:
						last = op_clazz(last, l.consume())
					else:
						if last:
							l2.append(last)
							last = None
						l2.append(current)
			if last:
				l2.append(last)

			l = parser.ConsumableIter(l2)

		return Query(l)

	def _get_condition_class(self, operator):
		d = {
			'==': EqualsCondition,
			'!=': NotEqualsCondition,
			'>': GreaterThanCondition,
			'<': LessThanCondition,
			'>=': GreaterThanOrEqualCondition,
			'<=': LessThanOrEqualCondition,
            '~': RegexMatchCondition
		}
		if operator not in d:
			raise Exception("Unknown operator '%s'" % operator)
		return d[operator]

