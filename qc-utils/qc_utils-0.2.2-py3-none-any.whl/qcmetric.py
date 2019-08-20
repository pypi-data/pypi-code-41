from bisect import insort
from collections import OrderedDict


class QCMetric(object):
    """Container that holds the qc metric as OrderedDict (sorted by keys of
    the input dict) and the "master" key (name) of the said qc metric. Can be
    instantiated from a regular dict.
    """

    def __init__(self, qc_metric_name, qc_metric_content, parser=None):
        if parser is not None:
            qc_metric_dict = parser(qc_metric_content)
        else:
            qc_metric_dict = qc_metric_content
        if not isinstance(qc_metric_dict, dict):
            raise TypeError("QCMetric data must be a dict.")
        self._name = qc_metric_name
        self._content = OrderedDict(sorted(qc_metric_dict.items(), key=lambda x: x[0]))

    @property
    def content(self):
        return self._content

    @property
    def name(self):
        return self._name

    def __len__(self):
        return len(self._content)

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "QCMetric(%r, %r)" % (self.name, self.content)


class QCMetricRecord(object):
    """Container that holds QCMetrics in sorted order.

    Attributes:
        metrics: list of metrics, kept sorted by the name of metrics
    """

    def __init__(self, metrics=None):
        if metrics is None:
            self._metrics = []
        else:
            # names must be unique
            names = [metric.name for metric in metrics]
            assert len(names) == len(set(names)), "Names of metrics have to be unique"
            self._metrics = metrics[:]
            self._metrics.sort()

    @property
    def metrics(self):
        return self._metrics

    def add(self, qc_metric):
        """Adds qc metric to the metrics, keeping it sorted by name.

        Args:
            qc_metric: QCMetric

        Returns: None

        Raises: AssertionError if a metric with same name is already in record
        """

        assert (
            qc_metric not in self._metrics
        ), "Metric with name {} already in record".format(qc_metric.name)
        insort(self._metrics, qc_metric)

    def add_all(self, qc_metric_container):
        """Adds all metrics from qc_metric_container preserving uniquness of names and order.
        If the names in the qc_metric_container are not unique, raises AssertionError and leaves
        the QCMetricRecord unmodified.
        Args:
            qc_metric_container: container of QCMetrics
        Returns: None

        Raises: AssertionError if adding would break the uniqueness of names in self.
        """
        for metric in qc_metric_container:
            assert (
                metric not in self._metrics
            ), "Metric with name {} already in record. Nothing from the container added".format(
                metric.name
            )
        for metric in qc_metric_container:
            self.add(metric)

    def to_ordered_dict(self):
        """Returns an OrderedDict with the contents.

        Returns: Ordered dict with structure as follows:
            - Ordered as the metrics is
            - Contents, assuming metrics = [qc1, qc2, qc3]:
            {
                qc1.name : qc1.content,
                qc2.name : qc2.content,
                qc3.name : qc3.content
            }
        """
        result = OrderedDict()
        for metric in self._metrics:
            result.update({metric.name: metric.content})
        return result

    def __len__(self):
        """
        Delegated to metrics.
        """
        return len(self._metrics)

    def __iter__(self):
        """
        Iterating QCMetricRecord is iterating over metrics.
        """
        return iter(self._metrics)

    def __repr__(self):
        """
        Like __iter__, __repr__ is delegated to metrics.
        """
        return "QCMetricRecord(%s)" % self._metrics.__repr__()
