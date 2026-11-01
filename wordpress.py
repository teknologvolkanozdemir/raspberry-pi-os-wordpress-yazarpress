"""Small client for publishing content through the WordPress REST API."""

import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit


class WordPressError(Exception):
    """Raised when a WordPress publishing request cannot be completed."""


def publish_content(site_url, username, app_password, content_type, title, content):
    """Publish a post or page and return the created WordPress object."""
    site_url = site_url.strip().rstrip("/")
    username = username.strip()
    app_password = "".join(app_password.split())
    title = title.strip()

    if not site_url or not username or not app_password or not title or not content.strip():
        raise WordPressError("Yayınlamadan önce tüm alanları doldurun.")
    if content_type not in ("posts", "pages"):
        raise WordPressError("Yazı veya sayfa türünü seçin.")

    try:
        parsed_url = urlsplit(site_url)
        valid_url = (
            parsed_url.scheme in ("http", "https")
            and parsed_url.netloc
            and parsed_url.hostname
            and not parsed_url.username
            and not parsed_url.password
            and not parsed_url.query
            and not parsed_url.fragment
        )
        if not valid_url:
            raise ValueError
        parsed_url.port
    except ValueError:
        raise WordPressError(
            "http:// veya https:// ile başlayan geçerli bir web sitesi adresi girin."
        ) from None

    endpoint = f"{site_url}/wp-json/wp/v2/{content_type}"
    credentials = base64.b64encode(f"{username}:{app_password}".encode("utf-8")).decode("ascii")
    payload = json.dumps(
        {"title": title, "content": content, "status": "publish"}
    ).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "YazarPress/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            details = json.loads(error.read().decode("utf-8"))
            message = details.get("message", "WordPress sunucusu isteği reddetti.")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            message = "WordPress sunucusu isteği reddetti."
        raise WordPressError(str(message)) from None
    except (URLError, TimeoutError, OSError):
        raise WordPressError(
            "WordPress'e bağlanılamadı. Web sitesi adresini ve ağ bağlantınızı kontrol edin."
        ) from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise WordPressError("WordPress geçersiz bir yanıt verdi.") from None

    if not isinstance(result, dict):
        raise WordPressError("WordPress geçersiz bir yanıt verdi.")
    return result
