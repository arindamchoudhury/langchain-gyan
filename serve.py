import glob as _glob
import os
from livereload import Server

import zensical.config as _zc


def _make_wikilink_resolver(docs_dir):
    def build_url(label, base, end):
        slug = label.strip().replace(" ", "-").lower()
        matches = _glob.glob(
            os.path.join(docs_dir, "**", f"{slug}.md"), recursive=True
        )
        if matches:
            rel = os.path.relpath(matches[0], docs_dir).replace("\\", "/")
            return "/" + rel[:-3] + "/"
        return f"/sources/{slug}/"
    return build_url


_docs_dir = os.path.join(os.path.dirname(os.path.abspath("zensical.toml")), "docs")

import markdown.extensions.wikilinks as _wikilinks_ext
_wikilinks_ext.build_url = _make_wikilink_resolver(_docs_dir)

_zc.DEFAULT_MARKDOWN_EXTENSIONS["wikilinks"] = {
    "base_url": "/sources/",
    "end_url": "/",
}

from zensical import build as _zensical_build

_CONFIG_FILE = os.path.abspath("zensical.toml")


def build():
    _zensical_build(_CONFIG_FILE, {"clean": False, "strict": False})


build()

server = Server()
server.watch("docs/", build)
server.watch("zensical.toml", build)
server.serve(root="site", port=8000, host="0.0.0.0")
