import ast
import re
import sys
import unittest
from importlib.metadata import version
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PRIMARY_DOCS = (
    Path("README.md"),
    Path("START_HERE.md"),
    Path("docs/CHAPTERS.md"),
    Path("docs/WORKFLOW_LOG.md"),
    Path("docs/CH4_AUDIT_CANDIDATE.md"),
    Path("docs/CH4_PRODUCTION_PLAN.md"),
    Path("docs/CH4_SCRIPT_CANDIDATE.md"),
    Path("docs/PRODUCTION_REQUIREMENTS.md"),
)


def requirement_versions() -> dict[str, str]:
    result = {}
    for raw in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, pinned = line.partition("==")
        if not separator or not name or not pinned:
            raise AssertionError(f"dependency must be exactly pinned: {line}")
        result[name.lower()] = pinned
    return result


def imported_roots() -> set[str]:
    modules = set()
    python_files = list(ROOT.glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module.split(".")[0])
    return modules


class DocumentationAndRequirementsTests(unittest.TestCase):
    def test_dependency_manifest_matches_imports_and_tested_environment(self):
        expected = {
            "fonttools": "4.68.0",
            "numpy": "2.4.6",
            "pillow": "13.0.0",
        }
        self.assertEqual(requirement_versions(), expected)
        for distribution, pinned in expected.items():
            with self.subTest(distribution=distribution):
                self.assertEqual(version(distribution), pinned)

        local_modules = {path.stem for path in ROOT.glob("*.py")}
        third_party = imported_roots() - set(sys.stdlib_module_names) - local_modules - {"tests"}
        self.assertEqual(third_party, {"PIL", "fontTools", "numpy"})

    def test_required_documents_builders_and_review_artifacts_exist(self):
        required = {
            *PRIMARY_DOCS,
            Path("requirements.txt"),
            Path("build_ch4_v2_scroll.py"),
            Path("CH4_V2_REVIEW_SCROLL_full.jpg"),
            Path("CH4_V2_REVIEW_SHEET.jpg"),
        }
        for relative in sorted(required):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_current_chapter_four_status_is_consistent_across_primary_docs(self):
        current_docs = PRIMARY_DOCS[:-1]
        for relative in current_docs:
            text = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(document=relative):
                self.assertIn("CH4_V2_REVIEW_SCROLL_full.jpg", text)
                self.assertIn("800×32018", text)
                self.assertNotIn("review-лента ещё не создавалась", text)
                self.assertNotIn("полная review-лента ещё не создавалась", text)
        combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in current_docs)
        self.assertIn("CH4_V2_REVIEW_SHEET.jpg", combined)
        self.assertIn("1908×3048", combined)
        self.assertIn("НЕ УТВЕРЖДЕНО", combined)
        self.assertIn("буквального `утверждаю`", combined)
        self.assertIn("**`1 / 5`**", (ROOT / "docs/WORKFLOW_LOG.md").read_text(encoding="utf-8"))
        self.assertIn("`1/5`", (ROOT / "docs/CHAPTERS.md").read_text(encoding="utf-8"))
        self.assertIn("50 тестов", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_all_markdown_links_resolve(self):
        markdown_files = sorted(ROOT.glob("*.md")) + sorted((ROOT / "docs").glob("*.md"))
        link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
        for document in markdown_files:
            text = document.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                if "://" in target or target.startswith("#"):
                    continue
                local = target.split("#", 1)[0]
                with self.subTest(document=document.relative_to(ROOT), target=target):
                    self.assertTrue((document.parent / local).resolve().exists())

    def test_archived_handoff_has_an_unambiguous_obsolescence_warning(self):
        opening = (ROOT / "HANDOFF.md").read_text(encoding="utf-8")[:2500]
        for exact in (
            "АРХИВНЫЙ HANDOFF",
            "не является текущей спецификацией",
            "Главы 4",
            "docs/PRODUCTION_REQUIREMENTS.md",
            "игровых номеров",
        ):
            with self.subTest(exact=exact):
                self.assertIn(exact, opening)

    def test_production_requirements_cover_mandatory_gates_and_qc(self):
        requirements = (ROOT / "docs/PRODUCTION_REQUIREMENTS.md").read_text(encoding="utf-8")
        for exact in (
            "## 2 · Среда и зависимости",
            "requirements.txt",
            "## 4 · Граница утверждения",
            "буквальное **`утверждаю`**",
            "не больше **10 кадров**",
            "## 8 · Текущий контракт Главы 4",
            "## 9 · Обязательный QC перед фиксацией",
            "unittest discover -s tests -v",
            "git diff --check",
            "## 11 · Определение готовности",
        ):
            with self.subTest(exact=exact):
                self.assertIn(exact, requirements)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("pip install -r requirements.txt", readme)


if __name__ == "__main__":
    unittest.main()
