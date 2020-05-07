from functools import wraps
save = []


def foo(size = 1):
    # @wraps(func)
    def inner(func):

        def wrapper(*args, **kwargs):
            print(f"here it is{args} and {size}")
            print(func.__name__)
            global save
            out = func(*args, **kwargs)
            print(args)
            save.append(out)
            return out

        return wrapper
    return inner


@foo(5)
def bar(a, b):
    return a + b


print(bar("a", "b"), save)
