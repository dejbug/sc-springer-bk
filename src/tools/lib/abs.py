def stringify(cls):
	def __str__(self):
		return self.__class__.__name__ + str(self.__dict__)
	setattr(cls, "__str__", __str__)
	return cls
