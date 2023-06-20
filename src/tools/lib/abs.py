def reprify(cls):
	__str__ = getattr(cls, "__str__")
	setattr(cls, "__repr__", __str__)
	return cls

def stringify(cls):
	def __str__(self):
		return self.__class__.__name__ + str(self.__dict__)
	setattr(cls, "__str__", __str__)
	return cls
