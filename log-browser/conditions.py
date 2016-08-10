from phylter.conditions import Condition

class NotEqualsCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s != %s" % (self.left, self.right)

class RegexMatchCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s ~ %s" % (self.left, self.right)

