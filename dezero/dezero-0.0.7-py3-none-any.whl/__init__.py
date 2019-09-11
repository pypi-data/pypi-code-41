
# step30まではversion 1、それ以降はversion 2
core_version = 2  #1 or 2


if core_version == 1:
    from dezero.core_simple import Variable
    from dezero.core_simple import Function
    from dezero.core_simple import using_config
    from dezero.core_simple import no_grad
    from dezero.core_simple import as_variable
    from dezero.core_simple import setup_variable

elif core_version == 2:
    from dezero.core import Variable
    from dezero.core import Function
    from dezero.core import using_config
    from dezero.core import no_grad
    from dezero.core import as_variable
    from dezero.core import setup_variable
    from dezero.links import Link
    from dezero.links import Chain

    import dezero.datasets
    import dezero.dataset
    import dezero.optimizers
    import dezero.iterators
    import dezero.functions
    import dezero.links

setup_variable()


__version__ = '0.0.7'