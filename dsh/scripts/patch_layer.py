#!/usr/bin/env python3
"""patch_layer.py - shared patch-layer primitive for the RE-Framework DSH tools.

Why this exists (2026-09-18 incident): the framework used to judge the home-level
patch file by "the file exists" and deleted the WHOLE file whenever it contained
this framework's withdrawn row. That file is legal DSH state (the home-level user
patch layer, applied after every profile layer), and in practice it carries other
frameworks' rows and machine-local settings.

One primitive, used by BOTH scripts/install.ps1 and scripts/selfcheck.ps1, for
BOTH the home layer and every profile layer:

  --has-row PATH --row-id ID
      read-only. exit 0 = present, 1 = absent (a missing file counts as absent),
      2 = error.
  --remove-row PATH --row-id ID [--backup]
      removes ONLY the entries carrying id: <ID> and keeps every other byte
      (comments, sibling entries, other rows, BOM, line endings). No write at all
      when the row is absent. exit 0 = removed|absent, 2 = error (nothing written).

Granularity is the ENTRY, not the top-level row: one 'insert' row may legally
carry several entries (another framework's entry next to ours), so a removal must
leave the sibling entries alive. Only when an item is left without any entry does
the whole item go (an 'insert:' with no entries would be a malformed patch row).

Text-level on purpose, never a YAML round-trip: yaml.safe_dump drops every comment
and normalises line endings, which is an unacceptable side effect on a config file
shared with other frameworks and with machine-local settings.

All diagnostics go to STDOUT: Windows PowerShell 5.1 promotes a native command's
stderr output to a terminating error when $ErrorActionPreference is Stop.
"""
import argparse
import os
import re
import sys

BOM = b"\xef\xbb\xbf"


def fail(message):
    sys.stdout.write("error: {0}\n".format(message))
    raise SystemExit(2)


def read_source(path):
    """Return (text, had_bom, raw) or None when the file does not exist."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except FileNotFoundError:
        return None
    except OSError as exc:
        fail("cannot read {0}: {1}".format(path, exc))
    had_bom = raw.startswith(BOM)
    try:
        text = (raw[len(BOM):] if had_bom else raw).decode("utf-8")
    except UnicodeDecodeError as exc:
        fail("not valid utf-8: {0} ({1})".format(path, exc))
    return text, had_bom, raw


def row_pattern(row_id):
    return re.compile(
        r"(?:^|[\s{,])id\s*:\s*['\"]?" + re.escape(row_id) + r"['\"]?(?=[\s,}\]]|$)"
    )


def indent_of(line):
    return len(line) - len(line.lstrip(" "))


def is_sequence_line(line):
    return line.lstrip(" ").startswith("-")


def item_spans(lines):
    """Top-level sequence items: a column-0 '-' starts one (YAML block scalars are
    indented, so their content can never be mistaken for an item boundary)."""
    starts = [i for i, line in enumerate(lines) if re.match(r"-(?:\s|$)", line)]
    spans = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        spans.append((start, end))
    return spans


def find_entries(text, row_id):
    """Locate every entry carrying row_id.

    Returns (lines, items, matches); each match is the entry's own line block,
    determined by indentation so nested sequences (e.g. a 'tools:' list inside the
    entry's config) are never mistaken for a second entry.
    """
    lines = text.splitlines(keepends=True)
    items = item_spans(lines)
    pattern = row_pattern(row_id)
    matches = []
    for item_index, (start, end) in enumerate(items):
        cursor = start
        while cursor < end:
            line = lines[cursor]
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and pattern.search(line):
                indent = indent_of(line)
                entry_end = end
                for probe in range(cursor + 1, end):
                    if indent_of(lines[probe]) == indent and is_sequence_line(lines[probe]):
                        entry_end = probe
                        break
                # blank lines after the entry belong to the separator between
                # entries/items, not to the entry: keep them byte-identical.
                while entry_end - 1 > cursor and lines[entry_end - 1].strip() == "":
                    entry_end -= 1
                matches.append(
                    {
                        "item": item_index,
                        "start": cursor,
                        "end": entry_end,
                        "indent": indent,
                    }
                )
                cursor = entry_end
            else:
                cursor += 1
    return lines, items, matches


def has_row(text, row_id):
    return bool(find_entries(text, row_id)[2])


def remove_row(text, row_id):
    """Return the new text, or None when there is nothing to remove."""
    lines, items, matches = find_entries(text, row_id)
    if not matches:
        return None
    dropped = set()
    per_item = {}
    for match in matches:
        dropped.update(range(match["start"], match["end"]))
        per_item.setdefault(match["item"], []).append(match)

    for item_index, item_matches in per_item.items():
        start, end = items[item_index]
        indent = item_matches[0]["indent"]
        survivors = [
            i
            for i in range(start, end)
            if i not in dropped
            and indent_of(lines[i]) == indent
            and is_sequence_line(lines[i])
            and not lines[i].strip().startswith("#")
        ]
        if not survivors:
            # an 'insert:' with no entries left would be a malformed patch row
            dropped.update(range(start, end))

    kept = [line for index, line in enumerate(lines) if index not in dropped]
    still_loadable = any(
        is_sequence_line(line) or line.strip() == "[]" for line in kept
    )
    if not still_loadable:
        # a comments-only patch file makes DSH fail to boot; the documented way to
        # disable a layer is an explicit empty list.
        if kept and not kept[-1].endswith(("\n", "\r")):
            kept[-1] = kept[-1] + "\n"
        kept.append("[]\n")
    return "".join(kept)


def write_atomic(path, text, had_bom):
    payload = text.encode("utf-8")
    if had_bom:
        payload = BOM + payload
    temp = path + ".tmp-patch-layer"
    try:
        with open(temp, "wb") as handle:
            handle.write(payload)
        os.replace(temp, path)
    except OSError:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="entry-level patch-layer primitive")
    parser.add_argument("--has-row", metavar="PATH")
    parser.add_argument("--remove-row", metavar="PATH")
    parser.add_argument("--row-id", required=True)
    parser.add_argument("--backup", action="store_true")
    args = parser.parse_args(argv)

    if bool(args.has_row) == bool(args.remove_row):
        fail("exactly one of --has-row or --remove-row is required")
    path = args.has_row or args.remove_row
    source = read_source(path)
    if source is None:
        sys.stdout.write("absent\n")
        return 1 if args.has_row else 0
    text, had_bom, raw = source

    if args.has_row:
        if has_row(text, args.row_id):
            sys.stdout.write("present\n")
            return 0
        sys.stdout.write("absent\n")
        return 1

    updated = remove_row(text, args.row_id)
    if updated is None:
        sys.stdout.write("absent\n")
        return 0
    if args.backup:
        try:
            with open(path + ".bak-ref-install", "wb") as handle:
                handle.write(raw)
        except OSError as exc:
            fail("cannot write backup for {0}: {1}".format(path, exc))
    try:
        write_atomic(path, updated, had_bom)
    except OSError as exc:
        fail("cannot write {0}: {1}".format(path, exc))
    sys.stdout.write("removed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
