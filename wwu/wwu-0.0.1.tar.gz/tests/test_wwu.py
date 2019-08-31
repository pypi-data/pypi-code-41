import pytest


class TestWwu:
    def test_wwu(self, box):
        assert box.wwu(10, 10, 20) == 0
        assert box.wwu(20, 10, 10) == 4

    def test_with_non_fitting_box(self, box):
        with pytest.raises(ZeroDivisionError):
            box.wwu(10, 10, 10)
