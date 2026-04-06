"""Shared citation utilities — programmatic (Author, Year) → [N] injection."""

import re
import logging

logger = logging.getLogger(__name__)

# Regex patterns matching (Author, Year) in two citation styles.
# Both support:  et al.  |  & Co-Author  |  and Co-Author  |  , Co-Author
_CO_AUTHOR_GROUP = r'(?:\s+et\s+al\.?|(?:\s*(?:[,&]|\band\b)\s*[A-Z][a-zA-Z\-\']+)+)?'

# Parenthetical — (Smith et al., 2023)  /  (Black and Wiliam, 2009)
_P1 = re.compile(
    r'\((?P<surname>[A-Z][a-zA-Z\-\']+)' + _CO_AUTHOR_GROUP +
    r',?\s+(?P<year>(?:19|20)\d{2})\)'
)

# Narrative — Smith et al. (2023)  /  Black and Wiliam (2009)
_P2 = re.compile(
    r'(?P<surname>[A-Z][a-zA-Z\-\']+)' + _CO_AUTHOR_GROUP +
    r'\s+\((?P<year>(?:19|20)\d{2})\)'
)


def inject_citations(text: str, index_map: dict[int, dict]) -> str:
    """Replace (Author, Year) references with [N] from index_map.

    Handles three citation styles:
    - Multi-citation blocks: (Smith, 2020; Jones et al., 2021; Black and Wiliam, 2009)
    - Single parenthetical: (Smith et al., 2023) / (Black and Wiliam, 2009)
    - Narrative: Smith et al. (2023) / Black and Wiliam (2009)

    Replaces with [N] on a successful match; leaves unchanged otherwise.
    """
    # Build year → list of (N, profile) lookup
    by_year: dict[int, list[tuple[int, dict]]] = {}
    for n, profile in index_map.items():
        try:
            y = int(profile.get("year") or 0)
            if y:
                by_year.setdefault(y, []).append((n, profile))
        except (TypeError, ValueError):
            pass

    def _find_n(surname: str, year: int) -> int | None:
        surname_lower = surname.strip().lower()
        candidates = by_year.get(year, [])

        # Pass 1: whole-word match in authors (e.g. "anders" won't match "andersson")
        word_re = re.compile(r'\b' + re.escape(surname_lower) + r'\b')
        for n, profile in candidates:
            authors = (profile.get("authors") or "").lower()
            if word_re.search(authors):
                return n

        # Pass 2: whole-word match in title
        for n, profile in candidates:
            title = (profile.get("title") or "").lower()
            if word_re.search(title):
                return n

        # Pass 3: substring fallback (original behaviour — catches hyphenated names etc.)
        for n, profile in candidates:
            title = (profile.get("title") or "").lower()
            authors = (profile.get("authors") or "").lower()
            if surname_lower in title or surname_lower in authors:
                return n

        return None

    def _replace(m: re.Match) -> str:
        surname = m.group("surname").strip().rstrip(",.")
        try:
            year = int(m.group("year"))
        except ValueError:
            return m.group(0)
        n = _find_n(surname, year)
        if n is not None:
            logger.debug(f"[cite_inject] ({surname}, {year}) → [{n}]")
            return f"[{n}]"
        return m.group(0)

    # Phase 0: Multi-citation blocks — (Smith, 2020; Jones et al., 2021; ...)
    # Matches any (...) block containing at least one semicolon AND two years
    _multi_cite_re = re.compile(
        r'\([^()]*(?:19|20)\d{2}[^()]*;[^()]*(?:19|20)\d{2}[^()]*\)'
    )

    def _replace_multi(m: re.Match) -> str:
        content = m.group(0)[1:-1]  # Strip outer parens
        parts = [p.strip() for p in content.split(';')]
        results = []
        for part in parts:
            yr_m = re.search(r'((?:19|20)\d{2})', part)
            sn_m = re.search(r'[A-Z][a-zA-Z\-\']+', part)
            if yr_m and sn_m:
                n = _find_n(sn_m.group(0), int(yr_m.group(1)))
                if n is not None:
                    logger.debug(f"[cite_inject] (multi) {sn_m.group(0)}, {yr_m.group(1)} → [{n}]")
                    results.append(f"[{n}]")
                    continue
            # Keep unmatched part as a standalone parenthetical so P1 can retry it
            results.append(f"({part})")
        return "".join(results)

    text = _multi_cite_re.sub(_replace_multi, text)

    # Phase 1: Single parenthetical — (Smith et al., 2023) / (Black and Wiliam, 2009)
    text = _P1.sub(_replace, text)

    # Phase 2: Narrative — Smith et al. (2023) / Black and Wiliam (2009)
    text = _P2.sub(_replace, text)

    return text


# ---------------------------------------------------------------------------
# Notes-index builder — parses researcher notes for supplementary references
# ---------------------------------------------------------------------------

_REF_LINE_RE = re.compile(r'^\[\d+\]\s+(.+)', re.MULTILINE)
_YEAR_RE = re.compile(r'\b((?:19|20)\d{2})\b')
_URL_RE = re.compile(r'(?:URL:\s*)(https?://\S+)', re.IGNORECASE)
_STAR_RE = re.compile(r'\*+')


def _extract_first_surname(author_str: str) -> str | None:
    """Extract the first author's surname from an author string.

    Handles:
        "Karaman, Pınar"          → "Karaman"
        "Pınar Karaman"           → "Karaman"
        "Rashid & Jaidin"         → "Rashid"
        "Black and Wiliam"        → "Black"
        "Wenzel, Hovey, & Ittner" → "Wenzel"
        "Andrew Sortwell, ..."    → "Sortwell"
    """
    s = author_str.strip().rstrip('.,; ')
    if not s:
        return None

    # Split on & / and / ; to isolate the first author chunk
    first_chunk = re.split(r'\s*(?:[&;]|\band\b)\s*', s)[0].strip().rstrip(',. ')

    # Split on comma — in "Last, First" the first part is the surname
    comma_parts = first_chunk.split(',')
    name_part = comma_parts[0].strip()

    words = name_part.split()
    if not words:
        return None

    # "Pınar Karaman" → last word is surname; "Rashid" → only word is surname
    # Using last word handles "First Last" format; single-word works naturally.
    return words[-1].strip('.,;&')


def build_notes_index(
    notes: list[str],
    exec_summaries: list[str],
    existing_map: dict[int, dict],
) -> dict[int, dict]:
    """Parse research notes + exec summaries for reference lines; build supplementary index.

    Returns a dict {N: profile_dict} with entries NOT already covered by existing_map,
    starting N from max(existing_map)+1.
    """
    # Pre-build a set of (surname_lower, year) already in existing_map so we skip duplicates
    existing_keys: set[tuple[str, int]] = set()
    for profile in existing_map.values():
        try:
            y = int(profile.get("year") or 0)
        except (TypeError, ValueError):
            y = 0
        authors = (profile.get("authors") or "").lower()
        title = (profile.get("title") or "").lower()
        # Add the first surname from the profile's authors field
        first_name = _extract_first_surname(profile.get("authors") or "")
        if first_name and y:
            existing_keys.add((first_name.lower(), y))
        # Also add first word of title as backup
        title_words = title.split()
        if title_words and y:
            existing_keys.add((title_words[0].lower(), y))

    # Scan all text for reference lines
    all_text = "\n".join(notes + exec_summaries)

    # seen: (surname_lower, year) → entry dict  (deduplication)
    seen: dict[tuple[str, int], dict] = {}

    for m in _REF_LINE_RE.finditer(all_text):
        line = m.group(1).strip()

        # Skip lines that look like OpenAI web search summaries or non-citations
        if line.lower().startswith("openai web search"):
            continue

        # Find year
        year_matches = _YEAR_RE.findall(line)
        if not year_matches:
            continue
        year = int(year_matches[0])

        # Extract URL (take the first one found)
        url = ""
        url_m = _URL_RE.search(line)
        if url_m:
            url = url_m.group(1).rstrip('.,)')

        # Determine boundary between authors and title
        # Strategy: find year position, authors are before it, title after
        year_pos = line.find(str(year))
        if year_pos < 0:
            continue

        authors_raw = line[:year_pos].rstrip('.,; *').strip()
        after_year = line[year_pos + 4:].lstrip('.,;: *').strip()

        # Title: everything up to next period, URL:, or end-of-usable-text
        title_raw = _STAR_RE.sub("", after_year.split(".")[0]).strip()
        if not title_raw:
            # fall back to a slightly longer slice
            title_raw = _STAR_RE.sub("", after_year[:200]).strip()

        if not authors_raw:
            continue

        surname = _extract_first_surname(authors_raw)
        if not surname or len(surname) < 2:
            continue

        key = (surname.lower(), year)
        if key in existing_keys or key in seen:
            continue

        seen[key] = {
            "title": title_raw[:200] or f"[{surname} {year}]",
            "authors": authors_raw[:150],
            "year": year,
            "url": url,
            "study_design": "not_reported",
            "quality": "n/a",
            "impact": "n/a",
        }

    # Assign [N] numbers continuing from existing_map
    start_n = (max(existing_map.keys()) + 1) if existing_map else 1
    result: dict[int, dict] = {}
    for i, entry in enumerate(seen.values(), start=start_n):
        result[i] = entry

    logger.info(f"[notes_index] Built {len(result)} supplementary index entries from notes/summaries")
    return result
