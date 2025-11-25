"""Parsers for different bookmark file formats."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from bookmark_checker.core.models import Bookmark, BookmarkCollection


def parse_many(paths: List[str]) -> BookmarkCollection:
    """
    Parse multiple bookmark files and merge into a single collection.

    Args:
        paths: List of file paths to parse

    Returns:
        BookmarkCollection with all parsed bookmarks
    """
    collection = BookmarkCollection()

    for path in paths:
        path_obj = Path(path)
        if not path_obj.exists():
            continue

        try:
            if path_obj.suffix.lower() == ".json":
                parsed = parse_chrome_json(str(path_obj))
            else:
                parsed = parse_netscape_html(str(path_obj))

            collection.extend(parsed.bookmarks)
        except Exception:
            # Continue processing other files on error
            continue

    return collection


def parse_netscape_html(path: str) -> BookmarkCollection:
    """
    Parse Netscape HTML bookmark file.

    Args:
        path: Path to HTML file

    Returns:
        BookmarkCollection with parsed bookmarks
    """
    collection = BookmarkCollection()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    def get_folder_path_for_element(element: Any) -> str:
        """Get folder path by finding all parent DLs and their associated H3 folders."""
        path_parts = []
        current_dl = element.find_parent("dl")
        
        # Walk up the tree through all parent DLs
        visited_dls = set()
        while current_dl:
            if current_dl in visited_dls:
                break
            visited_dls.add(current_dl)
            
            # Find the H3 that is associated with this DL
            # The H3 can be:
            # 1. A direct previous sibling of the DL
            # 2. Inside a DT that is a previous sibling of the DL
            # 3. Inside a DT that is a child of the parent DL
            
            folder_name = None
            
            # Method 1: Check if H3 is a direct previous sibling
            for prev_sib in current_dl.previous_siblings:
                if not hasattr(prev_sib, "name"):
                    continue
                if prev_sib.name == "h3" and hasattr(prev_sib, "get_text"):
                    folder_name = prev_sib.get_text(strip=True)
                    break
                # Method 2: Check if DT with H3 is a previous sibling
                if prev_sib.name == "dt":
                    h3 = prev_sib.find("h3")
                    if h3 and hasattr(h3, "get_text"):
                        folder_name = h3.get_text(strip=True)
                        break
            
            # Method 3: Check parent DL's children for DT with H3 before this DL
            if not folder_name and current_dl.parent:
                parent = current_dl.parent
                found_current = False
                for child in parent.children:
                    if child == current_dl:
                        found_current = True
                        continue
                    if found_current and hasattr(child, "name") and child.name == "dt":
                        h3 = child.find("h3")
                        if h3 and hasattr(h3, "get_text"):
                            folder_name = h3.get_text(strip=True)
                            break
                    # Also check before current_dl
                    if not found_current and hasattr(child, "name") and child.name == "dt":
                        h3 = child.find("h3")
                        if h3 and hasattr(h3, "get_text"):
                            # This might be the folder for a sibling DL, not this one
                            # Check if there's a DL after this DT
                            for next_child in parent.children:
                                if next_child == child:
                                    continue
                                if hasattr(next_child, "name") and next_child.name == "dl":
                                    # This DT is for this DL
                                    folder_name = h3.get_text(strip=True)
                                    break
                            if folder_name:
                                break
            
            if folder_name:
                path_parts.insert(0, folder_name)
            
            # Move to parent DL
            current_dl = current_dl.find_parent("dl")
        
        return "/".join(path_parts)

    # Find all bookmark links (A tags)
    all_links = soup.find_all("a", href=True)
    
    for link in all_links:
        url = link.get("href", "").strip()
        if not url or url.startswith("data:"):
            continue
        
        title = link.get_text(strip=True) or url
        
        # Parse ADD_DATE if present
        added = None
        add_date = link.get("add_date")
        if add_date:
            try:
                timestamp = int(add_date)
                added = datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                pass
        
        # Get folder path
        folder_path = get_folder_path_for_element(link)
        
        bookmark = Bookmark(
            url=url,
            title=title,
            added=added,
            folder_path=folder_path,
            source_file=path,
        )
        collection.add(bookmark)

    return collection


def parse_chrome_json(path: str) -> BookmarkCollection:
    """
    Parse Chrome/Chromium JSON bookmark file.

    Args:
        path: Path to JSON file

    Returns:
        BookmarkCollection with parsed bookmarks
    """
    collection = BookmarkCollection()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)

    def parse_node(node: Dict[str, Any], folder_path: str = "") -> None:
        """Recursively parse bookmark tree nodes."""
        node_type = node.get("type", "")

        if node_type == "url":
            # Bookmark
            url = node.get("url", "").strip()
            name = node.get("name", "").strip() or url

            # Parse date_added (Chrome uses microseconds since 1601-01-01)
            added = None
            date_added = node.get("date_added")
            if date_added:
                try:
                    # Chrome timestamp is microseconds since 1601-01-01
                    # Convert to Unix timestamp
                    chrome_epoch = 11644473600000000  # microseconds
                    unix_timestamp = (int(date_added) - chrome_epoch) / 1000000
                    added = datetime.fromtimestamp(unix_timestamp)
                except (ValueError, OSError):
                    pass

            if url:
                bookmark = Bookmark(
                    url=url,
                    title=name,
                    added=added,
                    folder_path=folder_path,
                    source_file=path,
                )
                collection.add(bookmark)
        elif node_type == "folder":
            # Folder
            name = node.get("name", "").strip()
            new_path = f"{folder_path}/{name}" if folder_path else name

            # Process children
            children = node.get("children", [])
            for child in children:
                parse_node(child, new_path)

    # Process roots
    roots = data.get("roots", {})
    for root_key in ["bookmark_bar", "other", "synced", "mobile"]:
        if root_key in roots:
            parse_node(roots[root_key], root_key.replace("_", " ").title())

    return collection

