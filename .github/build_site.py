"""Prepare _docs for mkdocs: copy the tracked files, make SKILL.md the home page, and README the about page.
Usage: python .github/build_site.py  (run from the repository root)"""
import pathlib, shutil, subprocess

root = pathlib.Path.cwd()
docs = root / "_docs"
shutil.rmtree(docs, ignore_errors=True)
skip = (".github/", "mkdocs.yml", ".gitignore")
for name in subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines():
    if not name.startswith(skip):
        (docs / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, docs / name)

skill_dir = docs / "skills/refactoring"
skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
(skill_dir / "SKILL.md").unlink()
(docs / "README.md").rename(docs / "about.md")
(docs / "index.md").write_text(skill.replace("](references/", "](skills/refactoring/references/"), encoding="utf-8")

