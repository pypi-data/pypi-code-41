# system modules
import logging
import threading
import copy
import functools
import datetime
import collections
import itertools

# internal modules

# external modules

logger = logging.getLogger(__name__)


class StorageQueue(collections.deque):
    @property
    def lock(self):
        try:
            return self._lock
        except AttributeError:
            self._lock = threading.Lock()
        return self._lock

    @property
    def bundle_interval(self):
        return getattr(self, "_bundle_interval", 0)

    @bundle_interval.setter
    def bundle_interval(self, interval):
        self._bundle_interval = float(interval)

    def locked(decorated_function):
        """
        Decorator for methods that should be locked with UploadQueue.lock
        """

        @functools.wraps(decorated_function)
        def wrapper(self, *args, **kwargs):
            with self.lock:
                return decorated_function(self, *args, **kwargs)

        return wrapper

    def log_queue_len(self):
        logger.debug("Now {n} datasets are queued".format(n=len(self)))

    @property
    @locked
    def bundleable_datasets(self):
        """
        Generator yielding datasets from the queue that still lie within the
        :any:`bundle_interval`.
        """
        for n, (queued_time, queued_dataset) in enumerate(self):
            now = datetime.datetime.utcnow().replace(
                tzinfo=datetime.timezone.utc
            )
            seconds_queued = (now - queued_time).total_seconds()
            if seconds_queued < self.bundle_interval:
                # logger.debug(
                #     "Queued dataset Nr. {n} ({dataset}) "
                #     "has been queued for "
                #     "{seconds:.2f} seconds, which is within "
                #     "the bundle inverval of {interval} seconds".format(
                #         n=n,
                #         seconds=seconds_queued,
                #         dataset=queued_dataset,
                #         interval=self.bundle_interval,
                #     )
                # )
                yield (queued_time, queued_dataset)

    def matching_bundleable_dataset(self, table, column_data):
        """
        Generator yielding :any:`bundleable_datasets` which can be used to
        merge a new given dataset in

        Args:
            table (str): the table name
            column_data (dict): the new dataset to merge. Dict structured like
                ``column_data["column1"] = value`` with an arbitrary
                number and columns
        """
        for column_combination in map(
            set,
            itertools.chain.from_iterable(
                map(
                    functools.partial(itertools.combinations, column_data),
                    range(len(column_data), 0, -1),
                )
            ),
        ):
            for n, (queued_time, queued_dataset) in enumerate(
                self.bundleable_datasets
            ):
                queued_table = queued_dataset.get(table, {})
                new_columns = column_combination - set(queued_table)
                if not new_columns:
                    continue
                intersecting_columns = column_combination.intersection(
                    queued_table
                )
                if not all(queued_table[k] == k for k in intersecting_columns):
                    continue
                logger.debug(
                    "Table {table} of "
                    "bundleable queued "
                    "dataset Nr. {n} ({dataset}) "
                    "has columns matching {column_data} so "
                    "it can be filled with {new_column_data}".format(
                        n=n,
                        dataset=queued_dataset,
                        column_data={
                            k: column_data[k] for k in intersecting_columns
                        },
                        table=repr(table),
                        new_column_data={
                            k: column_data[k] for k in new_columns
                        },
                    )
                )
                yield (queued_time, queued_dataset)

    @property
    @locked
    def old_datasets(self):
        """
        Generator yielding datasets from the queue that don't lie within the
        :any:`bundle_interval` anymore.
        """
        try:
            skipped = list()
            while self:
                ds = self.popleft()
                if (
                    datetime.datetime.utcnow().replace(
                        tzinfo=datetime.timezone.utc
                    )
                    - ds[0]
                ).total_seconds() > self.bundle_interval:
                    logger.debug(
                        "Dataset {dataset} doesn't lie "
                        "within the bundle interval of {interval:.2f} "
                        "seconds anymore".format(
                            dataset=ds, interval=self.bundle_interval
                        )
                    )
                    yield ds
                else:
                    logger.debug(
                        "Dataset {dataset} still lies "
                        "within the bundle interval of {interval:.2f} "
                        "seconds. Remembering it for re-queueing.".format(
                            dataset=ds, interval=self.bundle_interval
                        )
                    )
                    skipped.append(ds)
        finally:
            for ds in skipped:
                logger.debug(
                    "Re-queueing previously remembered dataset "
                    "{} which lied within the bundle interval".format(ds)
                )
                self.appendleft(ds)

    @property
    @locked
    def dataset(self):
        """
        Generator yielding the next queued dataset and removing it from the
        queue
        """
        while self:
            logger.debug("Retrieving a queued dataset")
            ds = self.popleft()
            self.log_queue_len()
            yield ds

    def add(self, dataset, dataset_time=None, prioritized=False):
        """
        Queue another dataset as tuple ``(now, dataset)``, where ``now`` is the
        current :any:`datetime.datetime.utcnow` with the timezone set to
        :any:`datetime.timezone.utc`.

        Args:
            dataset (dict): the dataset to queue. Dict structured like
                ``dataset["table1"]["column1"] = value`` with an arbitrary
                number of tables and columns
            dataset_time (datetime.datetime, optional): the time of the dataset
            prioritized (bool, optional): if ``True``, insert at the
                prioritized side of the queue.
        """
        if not dataset_time:
            dataset_time = datetime.datetime.utcnow().replace(
                tzinfo=datetime.timezone.utc
            )
        if self.bundle_interval <= 0:
            (self.appendleft if prioritized else self.append)(
                (dataset_time, dataset)
            )
            return

        dataset = copy.deepcopy(dataset)
        for table, column_data in copy.deepcopy(dataset).items():
            logger.debug("table: {}".format(table))
            logger.debug("new_column_data: {}".format(column_data))
            try:
                queued_time, queued_dataset = next(
                    self.matching_bundleable_dataset(table, column_data)
                )
            except StopIteration:
                continue
            queued_dataset.setdefault(table, {})
            queued_table = queued_dataset[table]
            queued_table.update(column_data)
            dataset.pop(table)
        if dataset:
            logger.warning(
                "Couldn't sort this remaining data into "
                "bundleable queued datasets, "
                "adding to the queue: {dataset}".format(dataset=dataset)
            )
            (self.appendleft if prioritized else self.append)(
                (dataset_time, dataset)
            )
        self.log_queue_len()
