import base64
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO

from wordpress import WordPressError, publish_content


class FakeResponse:
    def __init__(self, value):
        self.value = json.dumps(value).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.value


class PublishContentTests(unittest.TestCase):
    def test_posts_are_published_with_application_password_auth(self):
        result = {"id": 42, "title": {"rendered": "A post"}}
        with patch("wordpress.urlopen", return_value=FakeResponse(result)) as open_url:
            published = publish_content(
                "https://example.com/", " editor ", " ab cd ", "posts", " A post ", "Body"
            )

        self.assertEqual(published, result)
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.com/wp-json/wp/v2/posts")
        self.assertEqual(
            request.get_header("Authorization"),
            "Basic " + base64.b64encode(b"editor:abcd").decode("ascii"),
        )
        self.assertEqual(
            json.loads(request.data),
            {"title": "A post", "content": "Body", "status": "publish"},
        )
        self.assertEqual(open_url.call_args.kwargs["timeout"], 20)

    def test_pages_use_pages_endpoint(self):
        with patch("wordpress.urlopen", return_value=FakeResponse({"id": 9})) as open_url:
            publish_content(
                "https://example.com", "editor", "password", "pages", "A page", "Body"
            )

        self.assertTrue(open_url.call_args.args[0].full_url.endswith("/wp/v2/pages"))

    def test_required_fields_and_content_type_are_validated(self):
        for values in (
            ("", "user", "password", "posts", "title", "body"),
            ("https://example.com", "user", "password", "posts", " ", "body"),
            ("https://example.com", "user", "password", "comments", "title", "body"),
        ):
            with self.subTest(values=values), self.assertRaises(WordPressError):
                publish_content(*values)

    def test_invalid_site_urls_are_rejected(self):
        for url in ("example.com", "ftp://example.com", "https://user@example.com", "https://example.com/?x=1"):
            with self.subTest(url=url), self.assertRaises(WordPressError):
                publish_content(url, "user", "password", "posts", "title", "body")

    def test_wordpress_error_message_is_reported(self):
        error = HTTPError(
            "https://example.com/wp-json/wp/v2/posts",
            401,
            "Unauthorized",
            {},
            BytesIO(b'{"message":"Authentication failed."}'),
        )
        with patch("wordpress.urlopen", side_effect=error):
            with self.assertRaisesRegex(WordPressError, "Authentication failed"):
                publish_content(
                    "https://example.com", "user", "password", "posts", "title", "body"
                )


if __name__ == "__main__":
    unittest.main()
