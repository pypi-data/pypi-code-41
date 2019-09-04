from django.test import SimpleTestCase

from mbq.api_tools import exceptions
from mbq.api_tools.pagination import paginate_queryset
from mbq.api_tools.schema import Pagination


class PaginationTests(SimpleTestCase):
    def test_pagination_structure(self):
        data = [{"id": idx} for idx in range(100)]
        url = "/test-pagination"
        paginator = Pagination(page=2, page_size=25)

        data, pagination_data = paginate_queryset(data, url, paginator)

        self.assertEqual(pagination_data["page"], 2)
        self.assertEqual(pagination_data["page_size"], 25)
        self.assertEqual(pagination_data["total_objects"], 100)
        self.assertEqual(pagination_data["num_pages"], 4)
        self.assertEqual(pagination_data["next_page"], "/test-pagination?page=3")
        self.assertEqual(pagination_data["previous_page"], "/test-pagination?page=1")
        self.assertEqual(len(data), 25)
        self.assertEqual(data[0]["id"], 25)

    def test_error_handling(self):
        data = [{"id": idx} for idx in range(10)]
        url = "/test-pagination"
        paginator = Pagination(page=3, page_size=25)

        with self.assertRaises(exceptions.ImmediateResponseError):
            paginate_queryset(data, url, paginator)

    def test_empty_results(self):
        url = "/test-pagination"
        paginator = Pagination(page=1, page_size=25)

        data, pagination_data = paginate_queryset([], url, paginator)

        self.assertEqual(pagination_data["page"], 1)
        self.assertEqual(pagination_data["page_size"], 25)
        self.assertEqual(pagination_data["total_objects"], 0)
        self.assertEqual(pagination_data["num_pages"], 1)
        self.assertEqual(pagination_data["next_page"], None)
        self.assertEqual(pagination_data["previous_page"], None)
        self.assertEqual(len(data), 0)
