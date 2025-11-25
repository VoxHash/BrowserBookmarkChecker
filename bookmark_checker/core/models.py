"""Data models for bookmarks."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Bookmark:
    """Represents a single bookmark."""

    url: str
    title: str
    added: datetime | None = None
    folder_path: str = ""
    source_file: str = ""
    canonical_url: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Hash based on canonical URL and title."""
        return hash((self.canonical_url or self.url, self.title))

    def __eq__(self, other: object) -> bool:
        """Equality based on canonical URL and title."""
        if not isinstance(other, Bookmark):
            return False
        return (
            (self.canonical_url or self.url) == (other.canonical_url or other.url)
            and self.title == other.title
        )


class BookmarkCollection:
    """Collection of bookmarks with metadata."""

    def __init__(self) -> None:
        """Initialize an empty collection."""
        self.bookmarks: list[Bookmark] = []
        self.source_files: list[str] = []

    def add(self, bookmark: Bookmark) -> None:
        """Add a bookmark to the collection."""
        self.bookmarks.append(bookmark)
        if bookmark.source_file and bookmark.source_file not in self.source_files:
            self.source_files.append(bookmark.source_file)

    def extend(self, bookmarks: list[Bookmark]) -> None:
        """Add multiple bookmarks."""
        for bookmark in bookmarks:
            self.add(bookmark)

    def __len__(self) -> int:
        """Return the number of bookmarks."""
        return len(self.bookmarks)

    def __iter__(self):
        """Iterate over bookmarks."""
        return iter(self.bookmarks)

