"""Tests for utility functions."""

from bookmark_checker.core.utils import canonicalize_url, domain_from_url, normalize_whitespace


class TestCanonicalizeURL:
    """Tests for URL canonicalization."""

    def test_strips_tracking_params(self) -> None:
        """Test that tracking parameters are removed."""
        url = "https://example.com/page?utm_source=test&utm_medium=email&id=123"
        result = canonicalize_url(url)
        assert "utm_source" not in result
        assert "utm_medium" not in result
        assert "id=123" in result

    def test_removes_fragments(self) -> None:
        """Test that URL fragments are removed."""
        url = "https://example.com/page#section"
        result = canonicalize_url(url)
        assert "#" not in result
        assert result == "https://example.com/page"

    def test_lowercases_host(self) -> None:
        """Test that host is lowercased."""
        url = "https://EXAMPLE.COM/Page"
        result = canonicalize_url(url)
        assert "example.com" in result.lower()

    def test_strips_default_ports(self) -> None:
        """Test that default ports are stripped."""
        assert canonicalize_url("http://example.com:80/page") == "http://example.com/page"
        assert canonicalize_url("https://example.com:443/page") == "https://example.com/page"

    def test_preserves_non_tracking_params(self) -> None:
        """Test that non-tracking parameters are preserved."""
        url = "https://example.com/page?id=123&name=test"
        result = canonicalize_url(url)
        assert "id=123" in result
        assert "name=test" in result

    def test_removes_trailing_slash(self) -> None:
        """Test that trailing slashes are removed on non-root paths."""
        assert canonicalize_url("https://example.com/page/") == "https://example.com/page"
        assert canonicalize_url("https://example.com/") == "https://example.com/"

    def test_handles_empty_url(self) -> None:
        """Test handling of empty URLs."""
        assert canonicalize_url("") == ""
        assert canonicalize_url("   ") == "   "

    def test_all_tracking_params(self) -> None:
        """Test all known tracking parameters."""
        params = [
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "gclid",
            "fbclid",
            "mc_cid",
            "mc_eid",
            "igshid",
            "yclid",
            "_hsenc",
            "_hsmi",
            "mkt_tok",
            "ref",
            "cmp",
            "spm",
            "ved",
            "si",
            "s",
            "trk",
            "scid",
            "ck_subscriber_id",
        ]
        for param in params:
            url = f"https://example.com/page?{param}=value&keep=me"
            result = canonicalize_url(url)
            assert param not in result.lower()
            assert "keep=me" in result


class TestNormalizeWhitespace:
    """Tests for whitespace normalization."""

    def test_collapses_spaces(self) -> None:
        """Test that multiple spaces are collapsed."""
        assert normalize_whitespace("hello    world") == "hello world"

    def test_collapses_tabs(self) -> None:
        """Test that tabs are collapsed."""
        assert normalize_whitespace("hello\t\tworld") == "hello world"

    def test_collapses_newlines(self) -> None:
        """Test that newlines are collapsed."""
        assert normalize_whitespace("hello\n\nworld") == "hello world"

    def test_strips_whitespace(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        assert normalize_whitespace("  hello world  ") == "hello world"

    def test_handles_empty_string(self) -> None:
        """Test handling of empty strings."""
        assert normalize_whitespace("") == ""
        assert normalize_whitespace("   ") == ""


class TestDomainFromURL:
    """Tests for domain extraction."""

    def test_extracts_domain(self) -> None:
        """Test that domain is extracted correctly."""
        assert domain_from_url("https://example.com/page") == "example.com"
        assert domain_from_url("http://subdomain.example.com/path") == "subdomain.example.com"

    def test_removes_port(self) -> None:
        """Test that port is removed."""
        assert domain_from_url("https://example.com:8080/page") == "example.com"

    def test_lowercases_domain(self) -> None:
        """Test that domain is lowercased."""
        assert domain_from_url("https://EXAMPLE.COM/page") == "example.com"

    def test_handles_invalid_url(self) -> None:
        """Test handling of invalid URLs."""
        assert domain_from_url("") == ""
        assert domain_from_url("not a url") == ""
