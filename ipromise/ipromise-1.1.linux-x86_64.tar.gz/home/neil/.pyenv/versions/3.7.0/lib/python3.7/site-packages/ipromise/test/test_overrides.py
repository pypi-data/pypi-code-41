from abc import abstractmethod

import pytest
from ipromise import AbstractBaseClass, implements, overrides, must_agument


class HasAbstractMethod(AbstractBaseClass):

    @abstractmethod
    def f(self):
        raise NotImplementedError


class ImplementsAbstractMethod(HasAbstractMethod):

    @implements(HasAbstractMethod)
    def f(self):
        return 0


class HasRegularMethod(AbstractBaseClass):

    def f(self):
        return 1


class OverridesImplementedAbstractMethod(ImplementsAbstractMethod):

    @overrides(ImplementsAbstractMethod)
    def f(self):
        return 1


class EmptyClass:
    pass


# TODO: seems bad
class C(ImplementsAbstractMethod):

    @abstractmethod
    def f(self):
        raise NotImplementedError


# Tests from ipromise.py.
# -----------------------------------------------------------------------------
def test_not_a_base_class():
    with pytest.raises(TypeError):
        class X(HasAbstractMethod):
            @overrides(ImplementsAbstractMethod)
            def f(self):
                return 1

def test_somehow_abstract():
    # Somehow abstract in base class.
    class X(C):
        @overrides(ImplementsAbstractMethod)
        def f(self):
            return 1

def test_already_implemented():
    with pytest.raises(TypeError):
        # Already implemented in base class that does not inherit from ImplementsAbstractMethod.
        class X(ImplementsAbstractMethod, HasRegularMethod):
            @overrides(ImplementsAbstractMethod)
            def f(self):
                return 1

# Tests from overrides.py.
# -----------------------------------------------------------------------------
def test_decorated_twice():
    with pytest.raises(TypeError):
        # Not found in interface class.
        class X(HasAbstractMethod):
            @overrides(HasRegularMethod)
            @must_agument
            def f(self):
                return 1

def test_not_found():
    with pytest.raises(TypeError):
        # Not found in interface class.
        class X(ImplementsAbstractMethod):
            @overrides(ImplementsAbstractMethod)
            def g(self):
                return 1

def test_is_abstract():
    # Is abstract in interface class.
    class X(ImplementsAbstractMethod):
        @overrides(ImplementsAbstractMethod)
        def f(self):
            return 1

def test_override_an_override():
    with pytest.raises(TypeError):
        # Overrides an override.
        class X(OverridesImplementedAbstractMethod):
            @overrides(OverridesImplementedAbstractMethod)
            def f(self):
                return 1

def test_overrides_and_implemented():

    with pytest.raises(TypeError):
        class X(ImplementsAbstractMethod):
            @overrides(HasAbstractMethod)
            def f(self):
                return 1

def test_overrides_from_other_class():

    with pytest.raises(TypeError):
        class X(EmptyClass):
            @overrides(HasRegularMethod)
            def f():
                pass
