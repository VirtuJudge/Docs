import tempfile
import unittest
from pathlib import Path

from scripts.validate_docs import validate_document


class DocumentationValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.document = self.root / "example.md"

    def validate(self, text):
        self.document.write_text(text, encoding="utf-8")
        return validate_document(self.document, self.root)

    def test_valid_links_and_examples(self):
        (self.root / "target.md").touch()
        self.assertEqual(
            self.validate(
                "[local](target.md#heading)\n[root](/target.md)\n"
                "[web](https://example.com/missing)\n[anchor](#heading)\n"
                '[reference]: target.md "Title"\n'
                '```json\n{"valid": true}\n```\n'
                "```mermaid\nflowchart LR\n A --> B\n```\n"
            ),
            [],
        )

    def test_missing_local_and_reference_links(self):
        self.assertEqual(
            len(self.validate("[missing](absent.md)\n[ref]: absent.md\n")), 2
        )

    def test_out_of_repository_link(self):
        self.assertIn("out-of-repository", self.validate("[escape](../outside.md)")[0])

    def test_invalid_json(self):
        self.assertIn("invalid JSON", self.validate("```json\n{not json}\n```\n")[0])

    def test_unclosed_fence(self):
        self.assertIn(
            "unclosed code fence", self.validate("```mermaid\nflowchart LR\n")[0]
        )

    def test_links_inside_code_are_not_validated(self):
        self.assertEqual(self.validate("```text\n[example](absent.md)\n```\n"), [])

    def test_nested_shorter_fence_does_not_close_outer_fence(self):
        self.assertEqual(
            self.validate("````text\n```\n[example](absent.md)\n````\n"), []
        )

    def test_conflict_markers(self):
        self.assertEqual(
            len(self.validate("<<<<<<< ours\n=======\n>>>>>>> theirs\n")), 3
        )

    def test_missing_document(self):
        self.assertIn("cannot read", validate_document(self.document, self.root)[0])


if __name__ == "__main__":
    unittest.main()
