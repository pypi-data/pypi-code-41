from pyecs import datatypes as dt


def test_vector2D():
    a = dt.Vector2D(1.0, 0.0)
    b = dt.Vector2D(1.0, 1.0)

    assert 2 * b == dt.Vector2D(2.0, 2.0)
    assert 2 * b == b * 2

    assert a + b == dt.Vector2D(2.0, 1.0)
    assert b + a == a + b

    assert b - a == dt.Vector2D(0.0, 1.0)
    assert a - b != b - a

    b += a
    assert b == dt.Vector2D(2.0, 1.0)

    b -= a
    assert b == dt.Vector2D(1.0, 1.0)

    a *= 2
    assert a == dt.Vector2D(2.0, 0.0)
