from multidict import MultiDict, MultiDictProxy
from urllib.parse import urlsplit, urlunsplit, parse_qsl, SplitResult


__version__ = '0.0.1'

# Why not furl?
# Because I pretty sure URL class should be immutable
# but furl is a mutable class.


DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
    'ws': 80,
    'wss': 443,
}


class URL:
    # don't derive from str
    # follow pathlib.Path design
    # probably URL will not suffer from pathlib problems:
    # it's intended for libraries like aiohttp,
    # not to be passed into standard library functions like os.open etc.

    __slots__ = ('_val', '_query', '_hash')

    def __init__(self, val):
        if isinstance(val, str):
            self._val = urlsplit(val)
        elif isinstance(val, SplitResult):
            self._val = val
        else:
            raise TypeError("Constructor parameter should be "
                            "either URL or str")
        self._query = None
        self._hash = None

    def __str__(self):
        return urlunsplit(self._val)

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, str(self))

    def __eq__(self, other):
        if not isinstance(other, URL):
            return NotImplemented
        return self._val == other._val

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self._val)
        return self._hash

    @property
    def host(self):
        # Use host instead of hostname for sake of shortness
        # May add .hostname prop later
        return self._val.hostname

    @property
    def port(self):
        return self._val.port or DEFAULT_PORTS.get(self._val.scheme)

    @property
    def scheme(self):
        return self._val.scheme

    @property
    def path(self):
        return self._val.path or '/'

    @property
    def user(self):
        # not .username
        return self._val.username

    @property
    def password(self):
        return self._val.password

    @property
    def query(self):
        if self._query is None:
            self._query = MultiDict(parse_qsl(self._val.query))
        return MultiDictProxy(self._query)

    @property
    def fragment(self):
        return self._val.fragment

    @property
    def parent(self):
        path = self.path
        if path == '/':
            return self
        parts = path.split('/')
        val = self._val._replace(path='/'.join(parts[:-1]))
        return URL(val)
