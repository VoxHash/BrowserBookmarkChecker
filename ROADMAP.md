# Roadmap — Browser-Bookmark Checker

Realistic priorities based on the shipped 1.1.0 baseline (GUI + CLI merge/dedupe, Netscape HTML & Chrome JSON, offline PyInstaller release builds).

## Near term (Q4 2026 – Q1 2027)

### Formats
- [ ] Firefox bookmark export support beyond Netscape HTML (native JSON where practical)
- [ ] Safari bookmark import path (read-only export → HTML/JSON bridge)

### UX & CLI
- [ ] Progress output for large CLI merges
- [ ] Clearer CLI errors for missing/unreadable input files
- [ ] Keyboard shortcuts for primary GUI actions (import, merge, export)

### Quality
- [ ] Raise line coverage toward 90% on `core/` parsers and exporters
- [ ] Smoke-test packaged executables in CI before attaching to releases

## Next (2027 H1)

### Features
- [ ] Additional export formats (JSON bookmark dump alongside HTML/CSV)
- [ ] Optional folder-aware merge strategies (keep first path vs. flatten)
- [ ] Similarity presets for “strict URL only” vs. “aggressive fuzzy”

### Performance
- [ ] Faster fuzzy matching path for 50k+ bookmark sets
- [ ] Memory-friendly streaming parse for very large HTML exports

## Later (backlog)

- Plugin-style custom parsers (only if a second external format lands)
- Browser extension that exports into this tool’s formats (separate project)
- Cloud sync — **out of scope** while the product stays privacy-first / offline

## Explicitly not planned

- Telemetry or automated online link checking
- Renaming the project: **BrowserBookmarkChecker** stays. The name is descriptive for search (“browser bookmark” + duplicate checking), already published as `v1.0.0`/`v1.1.0` with matching PyPI-style package id and GitHub URL. A marketing rename would break links without a clear discoverability gain over better topics and description.

---

**Legend:** unchecked = planned · checked = done in a released version
