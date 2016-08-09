from phylter.conditions import Condition

class RegexMatchCondition(Condition):

	def __str__(self):  # pragma: nocover
		return "%s ~ %s" % (self.left, self.right)

