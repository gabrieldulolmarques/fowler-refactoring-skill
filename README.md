# refactoring-skill

Two refactoring catalogs packaged as [Agent Skills](https://agentskills.io) for coding
agents: Martin Fowler's *Refactoring* (2nd ed., 2018) and Joshua Kerievsky's *Refactoring to
Patterns* (2004). One skill, `refactoring`, maps 29 code smells to the 66 refactorings and 27
refactorings to patterns that fix them, with one reference file per refactoring (mechanics, a
C# example and verification steps).

**Site:** <https://gabrieldulolmarques.github.io/refactoring-skill/> (English and Portuguese).

## Layout

```
.claude-plugin/plugin.json # makes the package a Claude Code plugin
LICENSE # CC BY 4.0
NOTICE # credit to Fowler, Kerievsky and Addison-Wesley; what the license covers
CATALOG.md # the spec: 66 + 27 refactorings, 29 smells, file format
agents/
├── refactoring-analyst.md # read-only: finds smells and returns a short plan
└── refactoring-implementer.md # applies one refactoring, testing after each step
skills/refactoring/
├── SKILL.md # flow smell → refactoring → file, smell index, tables of the 66 + 27
└── references/ # smells.md, discipline.md and one <slug>.md per refactoring, in a folder per chapter
```

Only the skill's description stays in the agent's context. The body loads when the skill is
used, and each refactoring's file only when the agent opens it.

## Agents

Two subagents that use the skill:

- `refactoring-analyst` reads the code it is pointed at, names the smells and returns a short
  plan: where, which smell, which refactoring, whether tests cover it, and the risk. It never
  edits.
- `refactoring-implementer` applies one item of that plan (or a named refactoring), following
  the mechanics with a build and a test run after each step.

Review the plan before handing an item to the implementer. The build and test commands come
from the call or from the project's own instructions, not from this package.

## Using it

- **Any Agent Skills client** (Claude Code, Codex, OpenCode): link the
  `skills/refactoring` folder into the project's skills folder (on Windows, a junction:
  `New-Item -ItemType Junction`).
- **Claude Code plugin**: `claude --plugin-dir <path-to-this-repo>`. The skill and agents are
  then namespaced as `refactoring:<name>`.

Use one route per project, or Claude Code sees the skill twice.

## License and credit

[CC BY 4.0](LICENSE): free to share and adapt for any purpose, as long as you credit this
package **and** the books it is based on:

> Martin Fowler. *Refactoring: Improving the Design of Existing Code*. 2nd ed. Boston:
> Addison-Wesley (Pearson Education), 2018. ISBN 978-0-13-475759-9.
>
> Joshua Kerievsky. *Refactoring to Patterns*. Boston: Addison-Wesley (Pearson Education),
> 2004. ISBN 978-0-321-21335-8.

The license covers only this package's own content, not the books (see [NOTICE](NOTICE)).
The motivation and mechanics in the skill are paraphrased, with chapter and page cited;
nothing is copied from the books, refactoring.com, industriallogic.com, Refactoring.Guru's *Dive Into
Refactoring*, or the replication package of Chen Kuang Piao et al. Refactoring names, former
names and inverses come from the book's section headers, and from the book's web edition for the five web-only
refactorings. The C# examples are original.
