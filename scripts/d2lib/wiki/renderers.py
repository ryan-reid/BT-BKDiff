from __future__ import annotations
import os
import shutil
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: TEMPLATE_DIR and ASSET_SOURCE_DIR are relative to the original wiki.py location
# We need to adjust them to be relative to the repo root or the d2lib package.
D2LIB_DIR = os.path.dirname(MODULE_DIR)
TEMPLATE_DIR = os.path.join(D2LIB_DIR, "wiki_templates")
ASSET_SOURCE_DIR = os.path.join(D2LIB_DIR, "wiki_assets")

class WikiRenderer:
    def __init__(self, template_dir: str = TEMPLATE_DIR):
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **context: Any) -> str:
        return self.environment.get_template(template_name).render(**context)


class WikiOutputWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generated_paths: set[str] = set()

    def write_text(self, relative_path: str, content: str) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        self.generated_paths.add(normalized)

    def write_bytes(self, relative_path: str, content: bytes) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
        self.generated_paths.add(normalized)

    def copy_asset(self, source_path: str, relative_path: str) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        shutil.copyfile(source_path, full_path)
        self.generated_paths.add(normalized)

    def remove_stale_files(self) -> None:
        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.output_dir).replace("\\", "/")
                if rel_path in self.generated_paths:
                    continue
                try:
                    os.remove(full_path)
                except OSError:
                    pass

            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass