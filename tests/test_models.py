"""Tests for bookmark data models."""

from bookmark_checker.core.models import Bookmark, BookmarkCollection


class TestBookmark:
    """Tests for Bookmark equality and hashing."""

    def test_hash_uses_canonical_or_url(self) -> None:
        """Hash is stable for equal bookmarks."""
        a = Bookmark(url="https://a.example", title="A", canonical_url="https://a.example")
        b = Bookmark(url="https://a.example", title="A", canonical_url="https://a.example")
        assert hash(a) == hash(b)
        assert {a, b} == {a}

    def test_eq_compares_canonical_and_title(self) -> None:
        """Equality uses canonical URL (or url) and title."""
        a = Bookmark(url="https://x", title="T", canonical_url="https://canonical")
        b = Bookmark(url="https://y", title="T", canonical_url="https://canonical")
        c = Bookmark(url="https://x", title="Other", canonical_url="https://canonical")
        assert a == b
        assert a != c
        assert a != "not-a-bookmark"


class TestBookmarkCollection:
    """Tests for BookmarkCollection helpers."""

    def test_len_and_iter(self) -> None:
        """Collection supports len() and iteration."""
        collection = BookmarkCollection()
        collection.add(Bookmark(url="https://example.com", title="Example"))
        assert len(collection) == 1
        assert [b.title for b in collection] == ["Example"]
