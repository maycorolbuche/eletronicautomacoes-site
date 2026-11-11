"""Confere se os recursos locais referenciados pelo HTML estão no site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest


ROOT = Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name not in {"src", "href"} or not value:
                continue
            url = urlsplit(value.strip())
            if url.scheme or url.netloc or not url.path:
                continue
            self.local.append((self.getpos()[0], value, unquote(url.path)))


class SiteFiles(unittest.TestCase):
    def test_homepage_references_existing_local_files(self):
        parser = References()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        parser.close()
        self.assertTrue(parser.local, "index.html não referencia recursos locais")

        for line, reference, path in parser.local:
            with self.subTest(line=line, reference=reference):
                target = (ROOT / path.lstrip("/")).resolve()
                self.assertTrue(target.is_relative_to(ROOT), "Referência fora do site")
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), f"index.html:{line}: ausente {reference}")


if __name__ == "__main__":
    unittest.main()
