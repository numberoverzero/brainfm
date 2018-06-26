import functools


def defer(func):
    """
    def create_database_connection():
        db = Db()
        print("Creating connection")
        conn = db.connect('foo', 'bar')
        conn.expensive_sanity_check()
        return conn

    >>> conn = defer(create_database_connection)
    >>> conn.username
    "Creating connection"
    'foo'
    """
    class Deferred():
        def __init__(self):
            pass

        def __getattribute__(self, key):
            print('d.ga')
            obj = func()
            # the following lines will replace this instance (self)
            # with the dict and class of the actual object created by func()
            # which means future __getattribute__ calls won't go through
            # this function, but through the deferred object's class's
            # version of the same function.
            self.__dict__ = obj.__dict__
            self.__class__ = obj.__class__
            return obj.__getattribute__(key)
    return Deferred()


def deferred(func):
    """
    @deferred
    def make_thing(x, y):
        thing = Thing(x, y)
        thing.expensive_startup_call()
        return thing

    thing = make_thing(x, y)
    thing.do_work()  # <-- thing is instantiated here
    """
    # Wrap the initial function
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # using a lambda since defer requires a no-arg function
        return defer(lambda: func(*args, **kwargs))
    return wrapper
