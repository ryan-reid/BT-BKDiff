from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from d2lib.wiki.presentation import sanitize_display_text


class WikiPageDTO(TypedDict):
    kind: str
    title: str
    output_path: str
    template_name: str
    category: str
    source_files: List[str]
    payload: Dict[str, Any]


class WikiAssetDTO(TypedDict, total=False):
    relative_path: str
    source_path: str
    content_bytes: bytes


class WikiDataFileDTO(TypedDict):
    relative_path: str
    content: str


class WikiManifestEntryDTO(TypedDict):
    title: str
    path: str
    category: str
    sources: List[str]


class WikiSiteDTO(TypedDict):
    old_label: str
    new_label: str
    pages: List[WikiPageDTO]
    assets: List[WikiAssetDTO]
    data_files: List[WikiDataFileDTO]
    manifest: List[WikiManifestEntryDTO]


def empty_wiki_site(old_label: str, new_label: str) -> WikiSiteDTO:
    return {
        "old_label": old_label,
        "new_label": new_label,
        "pages": [],
        "assets": [],
        "data_files": [],
        "manifest": [],
    }


class WikiSiteRecordingWriter:
    """Collect generated non-page files while the content builder runs."""

    def __init__(self, site: WikiSiteDTO):
        self.site = site
        self.generated_paths: set[str] = set()

    def write_text(self, relative_path: str, content: str) -> None:
        normalized = relative_path.replace("\\", "/")
        self.site["data_files"].append({"relative_path": normalized, "content": sanitize_display_text(content)})
        self.generated_paths.add(normalized)

    def write_bytes(self, relative_path: str, content: bytes) -> None:
        normalized = relative_path.replace("\\", "/")
        self.site["assets"].append({"relative_path": normalized, "content_bytes": content})
        self.generated_paths.add(normalized)

    def copy_asset(self, source_path: str, relative_path: str) -> None:
        normalized = relative_path.replace("\\", "/")
        self.site["assets"].append({"relative_path": normalized, "source_path": source_path})
        self.generated_paths.add(normalized)

    def remove_stale_files(self) -> None:
        # Stale removal belongs to the publisher, where the final output root is known.
        return None
