#!/bin/bash
# Example CLI usage

python -m bookmark_checker \
    --input examples/sample_chrome_export.html examples/sample_chrome_bookmarks.json \
    --out merged_bookmarks.html \
    --similarity 85

