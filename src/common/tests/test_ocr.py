"""Test ocr utils work as expected."""
from django.test import SimpleTestCase

from common.tests import factories
from common.utils import ocr


class TestCase(SimpleTestCase):
    """Test ocr works as expected."""

    def test_image_to_int(self):
        """Images containing only ints can be converted to integers."""
        expected_int = 3
        for expected_int in range(10):
            with self.subTest(expected_int=expected_int):
                self.assertEqual(
                    ocr.b64_image_to_int(factories.base64_images[str(expected_int)]),
                    expected_int,
                )

    def test_image_to_int_with_text(self):
        """Images containing non int characters results in a ValueError."""
        with self.assertRaises(ValueError):
            ocr.b64_image_to_int(
                factories.base64_images["image_with_text"], single_char=False
            )

    def test_image_to_text(self):
        """Images can be converted to text."""
        text = ocr.b64_image_to_text(
            factories.base64_images["image_with_text"], single_char=False, strip=False
        )
        self.assertIn("with Text", text)
        self.assertIn("1", text)
