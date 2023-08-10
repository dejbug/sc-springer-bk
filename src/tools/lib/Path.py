import collections, re, os

Path = collections.namedtuple("Path", "text root type year month extra_")
Path.re = re.compile(r"(.*?/)(blitz|schnell|gp|meister)-(\d+)(?:-(\d+))?(-.*?)?\.csv")
Path.gg = classmethod(lambda cls, path: cls.re.match(path).groups())
Path.tt = [os.path.normpath, str, int, lambda x: int(x) if x else 0, lambda x: x]
Path.aa = classmethod(lambda cls, path: (t(g) for t,g in zip(cls.tt, cls.gg(path))))
Path.parse = classmethod(lambda cls, path: cls(path, *cls.aa(path)))
Path.__lt__ = lambda p, other: p.month < other.month
Path.extra = property(lambda p: p.extra_ if p.extra_ is not None else "")
Path.name = property(lambda p: "{0.type}-{0.year:02d}-{0.month:02d}{0.extra}".format(p))
Path.path = property(lambda p: os.path.join(p.root, p.name))
