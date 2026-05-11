import tempfile
import unittest
from pathlib import Path

from generate_homepage import generate_homepages


class GenerateHomepageTests(unittest.TestCase):
    def test_generates_single_terminal_homepage_with_filterable_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ai_dir = root / "AI应用"
            app_dir = root / "软件应用"
            hidden_dir = root / ".github"
            ai_dir.mkdir()
            app_dir.mkdir()
            hidden_dir.mkdir()

            (ai_dir / "mcp.html").write_text(
                "<!doctype html><html><head><title>MCP 指南</title></head><body></body></html>",
                encoding="utf-8",
            )
            (app_dir / "proxy.html").write_text(
                "<html><body><h1>Proxy Setup</h1></body></html>",
                encoding="utf-8",
            )
            (hidden_dir / "ignored.html").write_text("<title>Ignored</title>", encoding="utf-8")

            generated = generate_homepages(root)

            self.assertEqual(generated, [root / "index.html"])
            root_index = (root / "index.html").read_text(encoding="utf-8")

            self.assertFalse((ai_dir / "index.html").exists())
            self.assertFalse((app_dir / "index.html").exists())
            self.assertIn("Open a report, guide, or tool.", root_index)
            self.assertIn('class="cat"', root_index)
            self.assertIn('data-section="AI应用"', root_index)
            self.assertIn("AI应用", root_index)
            self.assertIn("软件应用", root_index)
            self.assertIn('href="AI应用/mcp.html"', root_index)
            self.assertNotIn("ignored.html", root_index)
            self.assertIn("MCP 指南", root_index)
            self.assertIn("Proxy Setup", root_index)
            self.assertIn(".result.is-hidden", root_index)
            self.assertIn('item.classList.toggle("is-hidden"', root_index)
            self.assertNotIn("item.hidden", root_index)
            self.assertNotIn("AI应用/index.html", root_index)


if __name__ == "__main__":
    unittest.main()
