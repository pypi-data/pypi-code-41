import unittest

from schemazer.base import SchemazerResponseField


class TestResponseFields(unittest.TestCase):
    def test_response_field_structure(self):
        class TestResponseField(SchemazerResponseField):
            description = 'description'
            name = 'name'
            type = int

        float_field = TestResponseField()

        self.assertEqual(
            float_field.to_dict(),
            {
                TestResponseField.name:
                    {
                        'type': int.__name__,
                        'description': TestResponseField.description,
                    }
            }
        )


if __name__ == '__main__':
    unittest.main()
