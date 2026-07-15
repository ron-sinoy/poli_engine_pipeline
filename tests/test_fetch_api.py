import unittest
from types import SimpleNamespace
from unittest.mock import patch

from modules.fetch_api import fetch_api, post_api


def _response(payload):
    return SimpleNamespace(raise_for_status=lambda: None, json=lambda: payload)


class TestFetchApi(unittest.TestCase):
    def test_fetch_api_returns_the_parsed_body(self) -> None:
        with patch("modules.fetch_api.httpx.get", return_value=_response([{"id": 1}])):
            self.assertEqual(fetch_api("https://example.com/rows"), [{"id": 1}])

    def test_a_200_carrying_an_error_body_raises(self) -> None:
        # The backend reports Supabase failures in the body with a 200. Passing
        # that dict on as data silently degraded to "nothing matched".
        error_body = {
            "error": "Failed to load waiting list incident vectors from Supabase",
            "details": {"code": "57014", "message": "canceling statement due to statement timeout"},
        }

        with patch("modules.fetch_api.httpx.get", return_value=_response(error_body)):
            with self.assertRaises(RuntimeError) as raised:
                fetch_api("https://example.com/rows")

        self.assertIn("57014", str(raised.exception))

    def test_post_api_returns_the_parsed_body(self) -> None:
        with patch("modules.fetch_api.httpx.post", return_value=_response({"ok": True})) as post:
            result = post_api("https://example.com/match", {"vectors": [0.1]})

        self.assertEqual(result, {"ok": True})
        post.assert_called_once_with(
            "https://example.com/match",
            json={"vectors": [0.1]},
            follow_redirects=True,
            timeout=90,
        )

    def test_post_api_raises_on_an_error_body(self) -> None:
        with patch("modules.fetch_api.httpx.post", return_value=_response({"error": "boom"})):
            with self.assertRaises(RuntimeError):
                post_api("https://example.com/match", {"vectors": [0.1]})


if __name__ == "__main__":
    unittest.main()
