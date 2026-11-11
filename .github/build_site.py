"""Prepare _docs for mkdocs: copy the tracked files, make SKILL.md the home page, README the about page,
and add one index page per chapter folder built from the chapter tables in SKILL.md.
Usage: python .github/build_site.py  (run from the repository root)"""
import pathlib, re, shutil, subprocess

root = pathlib.Path.cwd()
docs = root / "_docs"
shutil.rmtree(docs, ignore_errors=True)
skip = (".github/", "mkdocs.yml", ".gitignore")
for name in subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines():
    if not name.startswith(skip):
        (docs / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, docs / name)

skill_dir = docs / "skills/fowler-refactoring"
skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
(skill_dir / "SKILL.md").unlink()
(docs / "README.md").rename(docs / "about.md")
(docs / "index.md").write_text(skill.replace("](references/", "](skills/fowler-refactoring/references/"), encoding="utf-8")

for section in re.split(r"\n(?=### )", skill)[1:]:
    heading, _, rest = section.partition("\n")
    table = "\n".join(l for l in rest.splitlines() if l.startswith("|"))
    folder = re.search(r"references/([a-z-]+)/", table).group(1)
    table = re.sub(r"\]\(references/([a-z-]+)/", lambda m: "](" if m.group(1) == folder else f"](../{m.group(1)}/", table)
    (skill_dir / "references" / folder / "index.md").write_text(f"# {heading[4:]}\n\n{table}\n", encoding="utf-8")
