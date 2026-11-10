# fowler-refactoring-skill

Martin Fowler's refactoring catalog (*Refactoring*, 2nd ed., 2018) packaged as
[Agent Skills](https://agentskills.io) for coding agents: one skill, `fowler-refactoring`,
that maps the 24 code smells to the refactorings that fix them, with one reference file per
refactoring (mechanics, a C# example and verification steps).

**Status:** all 66 reference files written and reviewed.

## Layout

```
.claude-plugin/plugin.json # makes the package a Claude Code plugin
LICENSE # CC BY 4.0
NOTICE # credit to Fowler and Addison-Wesley; what the license covers
CATALOG.md # the spec: 66 refactorings, 24 smells, file format
agents/
├── fowler-skill-writer.md # writes or fixes one file of the skill per call
└── fowler-skill-reviewer.md # read-only review, returns findings and a verdict
skills/fowler-refactoring/
├── SKILL.md # flow smell → refactoring → file, smell index, table of the 66
└── references/ # smells.md, discipline.md and one <slug>.md per refactoring, in a folder per chapter
```

Only the skill's description stays in the agent's context. The body loads when the skill is
used, and each refactoring's file only when the agent opens it.

## Building the skill

From a session that has both agents:

1. Call `fowler-skill-writer` with the package path and the part to write (a refactoring,
   `smells.md`, `discipline.md` or `SKILL.md`).
2. Call `fowler-skill-reviewer` on the result, in a separate context.
3. If the verdict is not "approved", send the report back to the writer. After two rounds,
   stop and decide by hand.
4. Check the `check against the book` marks with the book before committing.

Both agents can read the book if the call gives the path to its PDF (or a text extraction
of it). They find each section by its title; the Page column of `CATALOG.md` is the printed
page, and a PDF's physical pages are usually offset from it. Reading PDF pages in
Claude Code needs `pdftoppm` (poppler) on the PATH. The book is not part of this package:
bring your own copy.

## Using it

- **Any Agent Skills client** (Claude Code, Codex, OpenCode): link the
  `skills/fowler-refactoring` folder into the project's skills folder (on Windows, a junction:
  `New-Item -ItemType Junction`).
- **Claude Code plugin**: `claude --plugin-dir <path-to-this-repo>`. The skill and agents are
  then namespaced as `fowler-refactoring:<name>`.

Use one route per project, or Claude Code sees the skill twice.

## License and credit

[CC BY 4.0](LICENSE): free to share and adapt for any purpose, as long as you credit this
package **and** the book it is based on:

> Martin Fowler. *Refactoring: Improving the Design of Existing Code*. 2nd ed. Boston:
> Addison-Wesley (Pearson Education), 2018. ISBN 978-0-13-475759-9.

The license covers only this package's own content, not the book (see [NOTICE](NOTICE)).
The motivation and mechanics in the skill are paraphrased, with chapter and page cited;
nothing is copied from the book, refactoring.com, Refactoring.Guru's *Dive Into
Refactoring*, or the replication package of Chen Kuang Piao et al. Refactoring names, former
names and inverses come from the book's section headers, and from the public catalog at
[refactoring.com/catalog](https://refactoring.com/catalog/) for the five web-only
refactorings. The C# examples are original.
