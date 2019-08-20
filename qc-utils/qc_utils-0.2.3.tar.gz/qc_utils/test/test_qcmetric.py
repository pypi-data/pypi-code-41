from collections import OrderedDict

import pytest

from qc_utils import QCMetric, QCMetricRecord


@pytest.fixture
def ordered():
    return OrderedDict([(2, "a"), (1, "b")])


@pytest.fixture
def obj_a1():
    return QCMetric("a", {1: 2})


@pytest.fixture
def obj_a2():
    return QCMetric("a", {2: 3})


@pytest.fixture
def obj_b():
    return QCMetric("b", {3: 4})


@pytest.fixture
def obj_c():
    return QCMetric("c", {1: 2, 3: 4, 5: 6})


@pytest.fixture
def obj_d():
    return QCMetric("d", {"a": "b"})


@pytest.fixture
def qc_record():
    return QCMetricRecord()


# Test QCMetric


def test_type_check():
    with pytest.raises(TypeError):
        QCMetric("name", 1)


def test_get_name():
    qc_obj = QCMetric("a", {})
    assert qc_obj.name == "a"


def test_get_content():
    qc_obj = QCMetric("_", {2: "a", 1: "b"})
    assert qc_obj.content == OrderedDict([(1, "b"), (2, "a")])


def test_len_0():
    assert len(QCMetric("a", {})) == 0


def test_len_1(obj_a1):
    assert len(obj_a1) == 1


def test_less_than():
    smaller_obj = QCMetric(1, {})
    bigger_obj = QCMetric(2, {})
    assert smaller_obj < bigger_obj


def test_equals():
    first_obj = QCMetric("a", {})
    second_obj = QCMetric("a", {"x": "y"})
    assert first_obj == second_obj


def test_QCMetric_repr():
    obj = QCMetric("a", {1: "x"})
    assert obj.__repr__() == "QCMetric('a', OrderedDict([(1, 'x')]))"


# Test QCMetricRecord


def test_init_from_list_not_unique(obj_a1, obj_a2):
    metrics = [obj_a1, obj_a2]
    with pytest.raises(AssertionError):
        QCMetricRecord(metrics)


def test_init_from_list_success(obj_a1, obj_b):
    metrics = [obj_a1, obj_b]
    record = QCMetricRecord(metrics)
    assert record.metrics[0] is obj_a1
    assert record.metrics[1] is obj_b


def test_add(qc_record, obj_a1):
    assert len(qc_record) == 0
    qc_record.add(obj_a1)
    assert len(qc_record) == 1


def test_add_all_to_empty(qc_record, obj_a1, obj_b):
    metrics = [obj_a1, obj_b]
    qc_record.add_all(metrics)
    assert len(qc_record) == 2


def test_add_all_to_nonempty_success(qc_record, obj_a1, obj_b, obj_c, obj_d):
    metrics = [obj_a1, obj_b]
    record = QCMetricRecord(metrics)
    record.add_all([obj_c, obj_d])
    assert len(record) == 4


def test_add_all_failure_because_not_unique(obj_a1, obj_a2, obj_b):
    record = QCMetricRecord([obj_a1])
    with pytest.raises(AssertionError):
        record.add_all([obj_b, obj_a2])
    assert len(record) == 1


def test_add_raises_error_when_add_same_twice(qc_record, obj_a1):
    qc_record.add(obj_a1)
    with pytest.raises(AssertionError):
        qc_record.add(obj_a1)


def test_add_raises_error_when_add_with_same_name(qc_record, obj_a1, obj_a2):
    qc_record.add(obj_a1)
    with pytest.raises(AssertionError):
        qc_record.add(obj_a2)


def test_to_ordered_dict(qc_record, obj_a1, obj_b):
    qc_record.add(obj_a1)
    qc_record.add(obj_b)
    qc_dict = qc_record.to_ordered_dict()
    assert qc_dict == OrderedDict([("a", {1: 2}), ("b", {3: 4})])


def test_QCMetricRecord_repr(obj_a1, obj_b):
    metrics = [obj_a1, obj_b]
    record = QCMetricRecord(metrics)
    assert (
        record.__repr__()
        == "QCMetricRecord([QCMetric('a', OrderedDict([(1, 2)])), QCMetric('b', OrderedDict([(3, 4)]))])"
    )
