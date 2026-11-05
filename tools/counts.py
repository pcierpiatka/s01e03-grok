#!/usr/bin/env python3
"""The only source of ticket counts. Exits non-zero when a count is not the rendered kb view."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDS = ROOT / "analysis" / "ids"
DESK = ROOT / "rendered" / "desk-4471.html"
COUNTS = ROOT / "src" / "lib" / "data" / "problem-counts.json"
ISSUES = ROOT / "analysis" / "issues"
SNAPSHOT = ROOT / "analysis" / "snapshot-ids.txt"

TITLES = {
    "parser": "parser: shared date parser reads day-first tenants month first",
    "hint": "hint: booking-v3 tells day-first tenants to type month first",
}
FOOTNOTE = "one-day"


def rendered_view(html: str) -> dict[str, int]:
    def cell(cause: str) -> int:
        match = re.search(
            rf"<code>{cause}</code></td><td[^>]*>\s*(\d+)\s*</td>",
            html,
        )
        if not match:
            sys.exit(f"rendered table has no {cause} count")
        return int(match.group(1))

    note = re.search(r"(\d+) reports read as a one-day move", html)
    if not note:
        sys.exit("rendered page has no one-day footnote")
    return {"parser": cell("parser"), "hint": cell("hint"), "one-day": int(note.group(1))}


def load_ids(name: str) -> list[str]:
    lines = (IDS / f"{name}.txt").read_text().split()
    if len(lines) != len(set(lines)):
        sys.exit(f"{name} has a duplicate id")
    return lines


def main() -> None:
    view = rendered_view(DESK.read_text())
    lists = {name: load_ids(name) for name in (*TITLES, FOOTNOTE)}
    known = set(SNAPSHOT.read_text().split())
    for name, ids in lists.items():
        missing = [i for i in ids if i not in known]
        if missing:
            sys.exit(f"{name} has ids missing from the snapshot: {missing[:5]}")
        if len(ids) != view[name]:
            sys.exit(f"{name} list is {len(ids)}; the rendered kb view shows {view[name]}")
    parser, hint, one_day = set(lists["parser"]), set(lists["hint"]), set(lists[FOOTNOTE])
    if parser & hint:
        sys.exit("parser and hint overlap")
    if parser | hint != known:
        sys.exit("parser plus hint is not every unique report")
    if not one_day <= parser:
        sys.exit("one-day ids are not all filed under parser")

    problems = []
    where = {
        "parser": "the rendered #4471 cause table, row parser, column reports",
        "hint": "the rendered #4471 cause table, row hint, column reports",
        "one-day": "the footnote under the rendered #4471 cause table",
    }
    notes = {
        "parser": "This row is the cause the table files as #4471. The one-day footnote is the same problem, counted inside this row.",
        "hint": "This row says: not this ticket — no ticket of its own.",
    }
    ISSUES.mkdir(parents=True, exist_ok=True)
    for name, ids in ((name, lists[name]) for name in TITLES):
        n = len(ids)
        title = f"{TITLES[name]} ({n} reports)"
        body = "\n".join([
            f"The desk's own view shows {n} for this, here: {where[name]}.",
            notes[name],
            f"Id list: analysis/ids/{name}.txt ({n} ids).",
        ])
        (ISSUES / f"{name}.md").write_text(f"# {title}\n\n{body}\n")
        problems.append({
            "id": name,
            "title": title,
            "reports": n,
            "where": where[name],
            "note": notes[name],
            "ids": f"analysis/ids/{name}.txt",
        })
    COUNTS.parent.mkdir(parents=True, exist_ok=True)
    COUNTS.write_text(json.dumps({"problems": problems}, indent=2) + "\n")
    print("ok", {name: len(ids) for name, ids in lists.items()})


if __name__ == "__main__":
    main()
