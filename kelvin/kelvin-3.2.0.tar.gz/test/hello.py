
print('hello', __name__)

def test_includes():
    """
    Loads the 'dynload' module in a way that Kelvin cannot detect.  Tests the "includes"
    option.
    """
    m = __import__('dynload')
    m.test()


def test_extension():
    import ssl


def test_subpackage():
    """
    Ensure subpackages are automatically added by importing a module from sub1 then dynamically importing a module from
    sub1.sub2.  The sub1 import should cause Kelvin to include everything from sub1 down.
    """
    from sub1 import sub1mod
    sub1mod.f()

    pkg = 'sub1.sub2.sub2mod'
    m = __import__(pkg)
    # Python returns the top level.
    for attr in pkg.split('.')[1:]:
        m = getattr(m, attr)

    m.f()


if __name__ == '__main__':
    print('hello is main!')

    test_includes()
    test_extension()
    test_subpackage()
    
