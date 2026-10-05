#!/usr/bin/env python3
"""test_home_patch.py - regression gate for scripts/patch_layer.py.

Run by selfcheck section [6]. Locks the lesson of 2026-09-18: a patch file is NOT
a violation just because it exists - the judged fact is "does this file carry OUR
row id", and a cleanup must never touch the rest of a file that other frameworks
and machine-local settings share.

Every case also asserts that stderr stays empty: Windows PowerShell 5.1 promotes
a native command's stderr output to a terminating error under
$ErrorActionPreference = 'Stop', which would abort install.ps1.
"""
import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PRIMITIVE = os.path.join(HERE, os.pardir, "scripts", "patch_layer.py")
ROW = "re-framework-tools-global"
FOREIGN = "anchorlaw-tools-global"
BOM = b"\xef\xbb\xbf"
BACKUP_SUFFIX = ".bak-ref-install"


def run(*args):
    proc = subprocess.run(
        [sys.executable, PRIMITIVE] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout.decode("utf-8").strip(), proc.stderr.decode("utf-8")


class PatchLayerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "cordis.patch.yml")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data):
        with open(self.path, "wb") as handle:
            handle.write(data)

    def read(self):
        with open(self.path, "rb") as handle:
            return handle.read()

    def assert_no_stderr(self, stderr):
        self.assertEqual(stderr, "", "stderr must stay empty for PowerShell 5.1")

    # ---------------------------------------------------------------- judgement
    def test_our_row_is_detected(self):
        self.write(b"- insert:\n  - id: " + ROW.encode() + b"\n    name: ./x.js\n")
        code, out, err = run("--has-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "present"))

    def test_foreign_row_is_not_our_row(self):
        self.write(b"- insert:\n  - id: " + FOREIGN.encode() + b"\n    name: ./y.js\n")
        code, out, err = run("--has-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (1, "absent"), "a foreign framework row is legal")

    def test_comment_mention_is_not_a_row(self):
        self.write(b"# migrated away from " + ROW.encode() + b"\n- id: agent-instructions\n")
        code, out, err = run("--has-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (1, "absent"), "prose must not trip the gate")

    def test_missing_file_counts_as_absent(self):
        code, out, err = run("--has-row", os.path.join(self.tmp.name, "nope.yml"), "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (1, "absent"))

    # ------------------------------------------------------------------ cleanup
    def test_removal_keeps_every_other_byte(self):
        source = (
            BOM
            + b"# machine-local prefs (keep me)\r\n"
            + b"- id: agent-instructions\r\n"
            + b"  config:\r\n"
            + b"    maxBytes: 262144\r\n"
            + b"\r\n"
            + b"- insert:\r\n"
            + b"  - id: " + ROW.encode() + b"\r\n"
            + b"    name: ./plugins/re-framework/re-framework-tools.js\r\n"
            + b"    config: {}\r\n"
        )
        expected = (
            BOM
            + b"# machine-local prefs (keep me)\r\n"
            + b"- id: agent-instructions\r\n"
            + b"  config:\r\n"
            + b"    maxBytes: 262144\r\n"
            + b"\r\n"
        )
        self.write(source)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        self.assertEqual(self.read(), expected, "comment, foreign row, BOM and CRLF must survive")

    def test_no_write_when_absent(self):
        source = b"- insert:\n  - id: " + FOREIGN.encode() + b"\n    name: ./y.js\n"
        self.write(source)
        before = os.path.getmtime(self.path)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW, "--backup")
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "absent"))
        self.assertEqual(self.read(), source, "absent row must leave the file untouched")
        self.assertEqual(os.path.getmtime(self.path), before, "no write at all")
        self.assertFalse(os.path.exists(self.path + BACKUP_SUFFIX), "no backup for a no-op")

    def test_removal_keeps_the_layer_loadable(self):
        self.write(b"# only our withdrawn row here\r\n- insert:\r\n  - id: " + ROW.encode() + b"\r\n    name: ./x.js\r\n")
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        result = self.read()
        self.assertTrue(result.startswith(b"# only our withdrawn row here\r\n"))
        self.assertIn(b"[]", result, "comments-only patch files make DSH fail to boot")

    def test_inline_style_row_is_detected_and_removed(self):
        self.write(b"[]\n- insert:\n  - {id: " + ROW.encode() + b", name: ./x.js}\n")
        code, _, err = run("--has-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual(code, 0)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        self.assertNotIn(ROW.encode(), self.read())

    def test_sibling_entry_in_the_same_insert_row_survives(self):
        # one 'insert:' row may carry another framework's entry right next to ours
        source = (
            b"- insert:\r\n"
            b"  - id: anchorlaw-tools-global\r\n"
            b"    name: ./plugins/anchorlaw/anchorlaw-tools.js\r\n"
            b"    config: {}\r\n"
            b"  - id: " + ROW.encode() + b"\r\n"
            b"    name: ./plugins/re-framework/x.js\r\n"
            b"    config: {}\r\n"
        )
        expected = (
            b"- insert:\r\n"
            b"  - id: anchorlaw-tools-global\r\n"
            b"    name: ./plugins/anchorlaw/anchorlaw-tools.js\r\n"
            b"    config: {}\r\n"
        )
        self.write(source)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        self.assertEqual(self.read(), expected, "the sibling entry must survive")

    def test_blank_separator_line_survives(self):
        source = (
            b"- insert:\r\n"
            b"  - id: anchorlaw-tools-global\r\n"
            b"    name: ./plugins/anchorlaw/anchorlaw-tools.js\r\n"
            b"    config: {}\r\n"
            b"  - id: " + ROW.encode() + b"\r\n"
            b"    name: ./plugins/re-framework/x.js\r\n"
            b"    config: {}\r\n"
            b"\r\n"
            b"- id: agent-instructions\r\n"
        )
        expected = (
            b"- insert:\r\n"
            b"  - id: anchorlaw-tools-global\r\n"
            b"    name: ./plugins/anchorlaw/anchorlaw-tools.js\r\n"
            b"    config: {}\r\n"
            b"\r\n"
            b"- id: agent-instructions\r\n"
        )
        self.write(source)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        self.assertEqual(self.read(), expected, "the blank separator line must survive")

    def test_nested_list_inside_our_entry_is_not_a_second_entry(self):
        self.write(
            b"- insert:\n  - id: " + ROW.encode() + b"\n    name: ./x.js\n"
            b"    config:\n      tools:\n        - status\n"
        )
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        self.assertEqual(self.read(), b"[]\n", "the whole emptied item goes, nested lines included")

    def test_two_own_entries_in_one_row_are_both_removed(self):
        self.write(
            b"- insert:\n  - id: " + ROW.encode() + b"\n    name: ./a.js\n"
            b"  - id: " + ROW.encode() + b"\n    name: ./b.js\n"
        )
        code, _, err = run("--has-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual(code, 0)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW)
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        self.assertNotIn(ROW.encode(), self.read())
        self.assertEqual(self.read(), b"[]\n")

    def test_backup_holds_the_original_bytes(self):
        source = b"- insert:\n  - id: " + ROW.encode() + b"\n    name: ./x.js\n"
        self.write(source)
        code, out, err = run("--remove-row", self.path, "--row-id", ROW, "--backup")
        self.assert_no_stderr(err)
        self.assertEqual((code, out), (0, "removed"))
        with open(self.path + BACKUP_SUFFIX, "rb") as handle:
            self.assertEqual(handle.read(), source)
        self.assertNotIn(ROW.encode(), self.read())


if __name__ == "__main__":
    # unittest's own chatter goes to a buffer: selfcheck section [6] wants ONE
    # readable line on success, and stderr must stay empty (PowerShell 5.1 turns a
    # native command's stderr into a terminating error under -ErrorAction Stop).
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PatchLayerTest)
    buffer = io.StringIO()
    result = unittest.TextTestRunner(verbosity=0, stream=buffer).run(suite)
    if result.wasSuccessful():
        print("{0} patch-layer cases passed".format(result.testsRun))
        raise SystemExit(0)
    sys.stdout.write(buffer.getvalue())
    raise SystemExit(1)
