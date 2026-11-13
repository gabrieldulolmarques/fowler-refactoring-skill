# Catalog spec

The spec the skill was written from and is checked against: one skill,
`refactoring`, with one reference file per refactoring, the smells and the discipline,
and the file format. Sections 1–4 cover Fowler's catalog; section 5 covers Kerievsky's
refactorings to patterns, added in 0.4.0.

Sources: Fowler, *Refactoring*, 2nd ed. (2018), chapters 2–4 and 6–12, and the online catalog
([refactoring.com/catalog](https://refactoring.com/catalog/), checked on 2026-10-31), which
lists **66 refactorings**: the **61 from the book** plus **5 that only exist in the web
edition** (marked "web" in the Page column).

The skill is generic: it teaches the refactorings, not any project's process. The examples
are plain C# with a neutral domain (orders, customers, invoices, accounts), and nothing refers
to a specific project, framework, engine or team workflow.

---

## 1. The skill

One skill, `refactoring`. Only its `description` stays in the agent's context; the
`SKILL.md` body loads when the skill is used, and each reference file only when the agent
opens it. The agent starts from a problem (a smell), not from a refactoring's name, so one
entry point that routes smell → refactoring → file works better than 66 competing
descriptions.

| File | Source | Content |
|---|---|---|
| `SKILL.md` | this spec | the flow smell → refactoring → file, a smell quick index and a table of the 66 refactorings (name, when, file), grouped by chapter (section 4.1) |
| `references/smells.md` | ch. 3; Kerievsky ch. 4 | the 29 smells, symptoms and suggested refactorings (sections 3 and 5.2) |
| `references/discipline.md` | ch. 2 and 4 | tests first, small steps, commit after each green refactoring |
| `references/fowler/<chapter>/<slug>.md` (66 files) | ch. 6–12, or the web edition for the web-only ones | one refactoring each: when to use, mechanics, C# example, verification (section 4.2) |
| `references/kerievsky/<chapter>/<slug>.md` (27 files) | Kerievsky ch. 6–11 | one refactoring to a pattern each, same format plus pattern and direction (section 5) |

The slug is the refactoring's name in kebab-case. Example: Extract Function →
`references/fowler/first-set/extract-function.md`. The files are grouped by book (`fowler/`, `kerievsky/`) and then in one folder per chapter. Fowler's:
`first-set` (ch. 6), `encapsulation` (7), `moving-features` (8), `organizing-data` (9),
`conditional-logic` (10), `refactoring-apis` (11) and `inheritance` (12); a web-only refactoring goes
in the chapter section 2 lists it under. The refactoring.com page uses the name in camelCase
instead: `https://refactoring.com/catalog/extractFunction.html`.

```
skills/
└── refactoring/
    ├── SKILL.md
    └── references/
        ├── smells.md
        ├── discipline.md
        ├── fowler/ # 7 chapter folders, 66 files
        │   ├── first-set/
        │   │   ├── extract-function.md
        │   │   └── ...
        │   └── ...
        └── kerievsky/ # 6 chapter folders, 27 files
            ├── creation/
            └── ...
```

---

## 2. The 66 refactorings

Checked against the book on 2026-10-31, mechanically from the PDF's text: each of the 61 book
refactorings starts on the **Page** shown (printed edition), the **Formerly / aka** and
**Inverse** columns are the book's own section header (`formerly:`, `aka:`, `subsumes:`,
`inverse of:`), and all 575 "Name (page)" cross-references in ch. 3–12 agree with the Page
column. For the 5 web-only refactorings, names, aliases and mechanics come from the book's web edition (checked on 2026-11-11).

**C# note** is what the reference file must add because the book's examples are JavaScript:
only generic C# points. Where it says "—", the file has no C# notes section.

### Chapter 6: A First Set of Refactorings

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 1 | Extract Function | 106 | formerly Extract Method | Inline Function | in C#, local functions are an option for helpers used in one place |
| 2 | Inline Function | 115 | formerly Inline Method | Extract Function | do not inline a `virtual`/`override` method or an interface implementation without checking the other implementations |
| 3 | Extract Variable | 119 | formerly Introduce Explaining Variable | Inline Variable | — |
| 4 | Inline Variable | 123 | formerly Inline Temp | Extract Variable | — |
| 5 | Change Function Declaration | 124 | aka Rename Function, Change Signature; formerly Rename Method, Add Parameter, Remove Parameter | — | the compiler finds direct callers, not reflection, string-based lookups or serialized names; on a public API, keep the old signature as an `[Obsolete]` forwarder during migration |
| 6 | Encapsulate Variable | 132 | formerly Encapsulate Field, Self-Encapsulate Field | — | public field → private field + property; a static field → static property |
| 7 | Rename Variable | 137 | — | — | — |
| 8 | Introduce Parameter Object | 140 | — | — | a class, `record` or `record struct` |
| 9 | Combine Functions into Class | 144 | — | — | — |
| 10 | Combine Functions into Transform | 149 | — | — | idiomatic in JavaScript; in C# it is usually a function that returns a new enriched `record` (`with` expressions), or it becomes Combine Functions into Class |
| 11 | Split Phase | 154 | — | — | the intermediate data structure is usually a `record` |

### Chapter 7: Encapsulation

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 12 | Encapsulate Record | 162 | formerly Replace Record with Data Class | — | dictionary, tuple, anonymous or `dynamic` data → a class or `record` with properties |
| 13 | Encapsulate Collection | 170 | — | — | expose `IReadOnlyList<T>` / `IReadOnlyCollection<T>`, with `Add`/`Remove` methods; a read-only interface does not stop a caller from casting back, so return a copy where that matters |
| 14 | Replace Primitive with Object | 174 | formerly Replace Data Value with Object, Replace Type Code with Class | — | meaningful `string`/`int` → own type (`record`, `readonly record struct`) or `enum` |
| 15 | Replace Temp with Query | 178 | — | — | a read-only property or a method; keep expensive queries as methods |
| 16 | Extract Class | 182 | — | Inline Class | — |
| 17 | Inline Class | 186 | — | Extract Class | — |
| 18 | Hide Delegate | 189 | — | Remove Middle Man | — |
| 19 | Remove Middle Man | 192 | — | Hide Delegate | — |
| 20 | Substitute Algorithm | 195 | — | — | — |

### Chapter 8: Moving Features

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 21 | Move Function | 198 | formerly Move Method | — | the target may be another class, a static class, or an extension method |
| 22 | Move Field | 207 | — | — | a field that is persisted or serialized keeps its stored name only if the mapping is updated too |
| 23 | Move Statements into Function | 213 | — | Move Statements to Callers | — |
| 24 | Move Statements to Callers | 217 | — | Move Statements into Function | — |
| 25 | Replace Inline Code with Function Call | 222 | — | — | — |
| 26 | Slide Statements | 223 | formerly Consolidate Duplicate Conditional Fragments | — | — |
| 27 | Split Loop | 227 | — | — | — |
| 28 | Replace Loop with Pipeline | 231 | — | — | LINQ; mind deferred execution (enumerate once) and allocation on hot paths |
| 29 | Remove Dead Code | 237 | — | — | code with no static callers may still be reached by reflection, dependency injection or serialization |

### Chapter 9: Organizing Data

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 30 | Split Variable | 240 | formerly Remove Assignments to Parameters, Split Temp | — | no immutable locals (`const` only fits compile-time constants), so keep each new variable assigned once; renaming a parameter breaks callers that use named arguments |
| 31 | Rename Field | 244 | — | — | a serialized or persisted field keeps its wire name only with a mapping attribute (e.g. `[JsonPropertyName("oldName")]`) or a migration |
| 32 | Replace Derived Variable with Query | 248 | — | — | a computed read-only property |
| 33 | Change Reference to Value | 252 | — | Change Value to Reference | `record`, `readonly record struct` or an immutable class with value equality (`Equals`/`GetHashCode`) |
| 34 | Change Value to Reference | 256 | — | Change Reference to Value | a repository or registry that hands out the shared instance |
| 35 | Replace Magic Literal | web | Replace Magic Number with Symbolic Constant | — | `const` for compile-time values, `static readonly` for the rest |

### Chapter 10: Simplifying Conditional Logic

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 36 | Decompose Conditional | 260 | — | — | — |
| 37 | Consolidate Conditional Expression | 263 | — | — | — |
| 38 | Replace Nested Conditional with Guard Clauses | 266 | — | — | — |
| 39 | Replace Conditional with Polymorphism | 272 | — | — | a `switch` on a type code → `abstract`/`virtual` members or an interface |
| 40 | Introduce Special Case | 289 | formerly Introduce Null Object | — | with nullable reference types enabled, the special case removes `?`/null checks at the call sites |
| 41 | Introduce Assertion | 302 | — | — | `Debug.Assert` (removed from Release builds) |
| 42 | Replace Control Flag with Break | web | Remove Control Flag | — | — |

### Chapter 11: Refactoring APIs

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 43 | Separate Query from Modifier | 306 | — | — | — |
| 44 | Parameterize Function | 310 | formerly Parameterize Method | — | — |
| 45 | Remove Flag Argument | 314 | formerly Replace Parameter with Explicit Methods | — | — |
| 46 | Preserve Whole Object | 319 | — | — | — |
| 47 | Replace Parameter with Query | 324 | formerly Replace Parameter with Method | Replace Query with Parameter | — |
| 48 | Replace Query with Parameter | 327 | — | Replace Parameter with Query | useful to remove a dependency on a static or singleton and make the code testable |
| 49 | Remove Setting Method | 331 | — | — | `{ get; }` or `{ get; init; }` |
| 50 | Replace Constructor with Factory Function | 334 | formerly Replace Constructor with Factory Method | — | a static factory method; make the constructor `private` or `protected` |
| 51 | Replace Function with Command | 337 | formerly Replace Method with Method Object | Replace Command with Function | — |
| 52 | Replace Command with Function | 344 | — | Replace Function with Command | — |
| 53 | Return Modified Value | web | — | — | — |
| 54 | Replace Error Code with Exception | web | — | — | do not use exceptions for expected control flow |
| 55 | Replace Exception with Precheck | web | Replace Exception with Test | — | the `TryParse`/`TryGetValue` pattern |

### Chapter 12: Dealing with Inheritance

| # | Refactoring | Page | Formerly / aka | Inverse | C# note |
|---|---|---|---|---|---|
| 56 | Pull Up Method | 350 | — | Push Down Method | — |
| 57 | Pull Up Field | 353 | — | Push Down Field | — |
| 58 | Pull Up Constructor Body | 355 | — | — | `: base(...)` constructor chaining |
| 59 | Push Down Method | 359 | — | Pull Up Method | — |
| 60 | Push Down Field | 361 | — | Pull Up Field | — |
| 61 | Replace Type Code with Subclasses | 362 | subsumes Replace Type Code with State/Strategy, Extract Subclass | Remove Subclass | — |
| 62 | Remove Subclass | 369 | formerly Replace Subclass with Fields | Replace Type Code with Subclasses | — |
| 63 | Extract Superclass | 375 | — | — | an `abstract` base class, or an interface if only the signatures are shared |
| 64 | Collapse Hierarchy | 380 | — | — | — |
| 65 | Replace Subclass with Delegate | 381 | — | — | — |
| 66 | Replace Superclass with Delegate | 399 | formerly Replace Inheritance with Delegation | — | — |

---

## 3. `references/smells.md`: the 24 smells and where they lead

Summary of ch. 3: the index the agent checks before picking a refactoring. Each refactoring
named here is the file `references/fowler/<chapter>/<slug>.md`.

| Smell | Page | Suggested refactorings |
|---|---|---|
| Mysterious Name | 72 | Change Function Declaration, Rename Variable, Rename Field |
| Duplicated Code | 72 | Extract Function, Slide Statements, Pull Up Method |
| Long Function | 73 | Extract Function, Replace Temp with Query, Introduce Parameter Object, Preserve Whole Object, Replace Function with Command, Decompose Conditional, Replace Conditional with Polymorphism, Split Loop |
| Long Parameter List | 74 | Replace Parameter with Query, Preserve Whole Object, Introduce Parameter Object, Remove Flag Argument, Combine Functions into Class |
| Global Data | 74 | Encapsulate Variable |
| Mutable Data | 75 | Encapsulate Variable, Split Variable, Slide Statements, Extract Function, Separate Query from Modifier, Remove Setting Method, Replace Derived Variable with Query, Combine Functions into Class, Combine Functions into Transform, Change Reference to Value |
| Divergent Change | 76 | Split Phase, Move Function, Extract Function, Extract Class |
| Shotgun Surgery | 76 | Move Function, Move Field, Combine Functions into Class, Combine Functions into Transform, Split Phase, Inline Function, Inline Class |
| Feature Envy | 77 | Move Function, Extract Function |
| Data Clumps | 78 | Extract Class, Introduce Parameter Object, Preserve Whole Object |
| Primitive Obsession | 78 | Replace Primitive with Object, Replace Type Code with Subclasses, Replace Conditional with Polymorphism, Extract Class, Introduce Parameter Object |
| Repeated Switches | 79 | Replace Conditional with Polymorphism |
| Loops | 79 | Replace Loop with Pipeline |
| Lazy Element | 80 | Inline Function, Inline Class, Collapse Hierarchy |
| Speculative Generality | 80 | Collapse Hierarchy, Inline Function, Inline Class, Change Function Declaration, Remove Dead Code |
| Temporary Field | 80 | Extract Class, Move Function, Introduce Special Case |
| Message Chains | 81 | Hide Delegate, Extract Function, Move Function |
| Middle Man | 81 | Remove Middle Man, Inline Function, Replace Superclass with Delegate, Replace Subclass with Delegate |
| Insider Trading | 82 | Move Function, Move Field, Hide Delegate, Replace Subclass with Delegate, Replace Superclass with Delegate |
| Large Class | 82 | Extract Class, Extract Superclass, Replace Type Code with Subclasses |
| Alternative Classes with Different Interfaces | 83 | Change Function Declaration, Move Function, Extract Superclass |
| Data Class | 83 | Encapsulate Record, Remove Setting Method, Move Function, Extract Function |
| Refused Bequest | 83 | Push Down Method, Push Down Field, Replace Subclass with Delegate, Replace Superclass with Delegate |
| Comments | 84 | Extract Function, Change Function Declaration, Introduce Assertion |

Checked against ch. 3 on 2026-10-31: every refactoring the chapter cites as "Name (page)" under
each smell is in its row. Data Class does not list Split Phase: the book mentions it only as the
example of an exception (an immutable result record), not as a fix.

---

## 4. How each piece becomes a file

### 4.1 `SKILL.md`

Frontmatter `name: refactoring` and a `description` (at most 1024 characters) that names
the catalog, the common symptoms and the most used refactorings, so the agent finds the skill
both by problem ("this class does too much") and by name ("do an Extract Class"). The body has
the flow (smell → refactoring → file, with the discipline before the first step), the smell
quick index, and one table per chapter with every refactoring, a one-line "when" and a link to
its file. It ends with the Source line:

```markdown
Source: Martin Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed.,
Addison-Wesley (Pearson Education), 2018, and the online catalog at
https://refactoring.com/catalog/. Paraphrased; see the package NOTICE.
```

When a reference file is added, renamed or removed, its row in the `SKILL.md` table changes
with it.

### 4.2 A refactoring's reference file

```markdown
# Extract Class

Fowler (2018), ch. 7, p. 182. Formerly / aka: —. Inverse: Inline Class
([inline-class.md](inline-class.md)).

## When to use
Smells: Large Class, Divergent Change, Data Clumps. (paraphrase, 2 to 5 lines, plus when
not to use it if the book says so)

## Mechanics
1. ... (paraphrase of the book's steps, numbered, one testable step per item)

## Example
Before / after in C#, written for this package (not copied from the book).

## C# notes
- Only when section 2 has a C# note.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
```

No frontmatter and no Source line: the credit is in `SKILL.md` and the NOTICE. A link to
another refactoring is relative: `[inline-class.md](inline-class.md)` in the same chapter folder,
`[move-function.md](../moving-features/move-function.md)` in another. For a web-only
refactoring, the citation line says "web edition only" and links the refactoring.com summary instead of chapter and page.

### 4.3 What goes in each part

| Part | Comes from | Note |
|---|---|---|
| Name, formerly / aka, inverse | the book's section header (section 2); the web edition for the web-only ones | short: may be literal |
| When to use, mechanics | the book (its web edition for the web-only ones) | **paraphrase**, with chapter and page; nothing copied |
| Example | written for this package in C# | neutral domain (orders, customers, invoices, accounts); not the book's example or domain |
| C# notes | section 2, "C# note" column | only where there is something to say |
| Verification | ch. 4 + `references/discipline.md` | the same in every file |
| Source line | this spec (4.1) | once, at the end of `SKILL.md`; credits the author and the publisher |

Nothing in the skill names a specific project, framework, engine or team process.

Not used as a source: the replication package by Chen Kuang Piao et al.
(`Fowler_catalog.json`). It has no license and contains text from the book.

---

## 5. Kerievsky's refactorings to patterns

Source: Joshua Kerievsky, *Refactoring to Patterns*, Addison-Wesley (Pearson Education), 2004,
chapters 4 and 6–11. Each refactoring is a sequence of smaller refactorings, mostly Fowler's,
that ends at a pattern (*to*), moves partway (*towards*) or removes one (*away*). The online
catalog at https://www.industriallogic.com/refactoring-to-patterns/catalog/ has only a summary
and a diagram for each; the mechanics come from the book.

### 5.1 The 27 refactorings

**Page** is the printed page from the book's own list of refactorings (inside front cover).
**Direction** comes from the book's "Refactoring Directions" table. **GoF** is the printed page of
the target pattern in Gamma et al., *Design Patterns* (1995), from that book's inside front
cover; "—" when the pattern is not in GoF. The book's mechanics name Fowler's refactorings by
their 1st-edition names; the reference files use the 2nd-edition names (section 2) and link
their files.

| # | Refactoring | Folder | Page | Pattern | Direction | GoF |
|---|---|---|---|---|---|---|
| 1 | Replace Constructors with Creation Methods | `creation` (ch. 6) | 57 | Creation Method | to | — |
| 2 | Move Creation Knowledge to Factory | `creation` | 68 | Factory | to | — |
| 3 | Encapsulate Classes with Factory | `creation` | 80 | Factory | to | — |
| 4 | Introduce Polymorphic Creation with Factory Method | `creation` | 88 | Factory Method | to | 107 |
| 5 | Encapsulate Composite with Builder | `creation` | 96 | Builder (Composite: away) | to | 97 |
| 6 | Inline Singleton | `creation` | 114 | Singleton | away | 127 |
| 7 | Compose Method | `simplification` (ch. 7) | 123 | Composed Method | to | — |
| 8 | Replace Conditional Logic with Strategy | `simplification` | 129 | Strategy | to, towards | 315 |
| 9 | Move Embellishment to Decorator | `simplification` | 144 | Decorator | to, towards | 175 |
| 10 | Replace State-Altering Conditionals with State | `simplification` | 166 | State | to, towards | 305 |
| 11 | Replace Implicit Tree with Composite | `simplification` | 178 | Composite | to | 163 |
| 12 | Replace Conditional Dispatcher with Command | `simplification` | 191 | Command | to, towards | 233 |
| 13 | Form Template Method | `generalization` (ch. 8) | 205 | Template Method | to | 325 |
| 14 | Extract Composite | `generalization` | 214 | Composite | to | 163 |
| 15 | Replace One/Many Distinctions with Composite | `generalization` | 224 | Composite | to | 163 |
| 16 | Replace Hard-Coded Notifications with Observer | `generalization` | 236 | Observer | to, towards | 293 |
| 17 | Unify Interfaces with Adapter | `generalization` | 247 | Adapter | to, towards | 139 |
| 18 | Extract Adapter | `generalization` | 258 | Adapter | to | 139 |
| 19 | Replace Implicit Language with Interpreter | `generalization` | 269 | Interpreter | to | 243 |
| 20 | Replace Type Code with Class | `protection` (ch. 9) | 286 | — | — | — |
| 21 | Limit Instantiation with Singleton | `protection` | 296 | Singleton | to | 127 |
| 22 | Introduce Null Object | `protection` | 301 | Null Object | to | — |
| 23 | Move Accumulation to Collecting Parameter | `accumulation` (ch. 10) | 313 | Collecting Parameter | to | — |
| 24 | Move Accumulation to Visitor | `accumulation` | 320 | Visitor (Iterator: away) | to, towards | 331 |
| 25 | Chain Constructors | `utilities` (ch. 11) | 340 | — | — | — |
| 26 | Unify Interfaces | `utilities` | 343 | — | — | — |
| 27 | Extract Parameter | `utilities` | 346 | — | — | — |

Overlaps with Fowler's 2nd edition, kept short and pointing to the Fowler file: Compose Method
(Extract Function, Slide Statements), Replace Type Code with Class (Replace Primitive with
Object, which subsumes it) and Introduce Null Object (Introduce Special Case, its new name).

### 5.2 The 12 smells

From ch. 4 and the inside back cover. Seven match a Fowler smell and are listed under it in
`smells.md`; five are new and listed at the end.

| Smell | Page | Fowler's smell | Refactorings |
|---|---|---|---|
| Duplicated Code | 39 | Duplicated Code | Form Template Method, Introduce Polymorphic Creation with Factory Method, Chain Constructors, Replace One/Many Distinctions with Composite, Extract Composite, Unify Interfaces with Adapter, Introduce Null Object |
| Long Method | 40 | Long Function | Compose Method, Move Accumulation to Collecting Parameter, Replace Conditional Dispatcher with Command, Move Accumulation to Visitor, Replace Conditional Logic with Strategy |
| Conditional Complexity | 41 | new | Replace Conditional Logic with Strategy, Move Embellishment to Decorator, Replace State-Altering Conditionals with State, Introduce Null Object |
| Primitive Obsession | 41 | Primitive Obsession | Replace Type Code with Class, Replace State-Altering Conditionals with State, Replace Conditional Logic with Strategy, Replace Implicit Tree with Composite, Replace Implicit Language with Interpreter, Move Embellishment to Decorator, Encapsulate Composite with Builder |
| Indecent Exposure | 42 | new | Encapsulate Classes with Factory |
| Solution Sprawl | 43 | new (the book calls it the twin of Shotgun Surgery) | Move Creation Knowledge to Factory |
| Alternative Classes with Different Interfaces | 43 | same | Unify Interfaces with Adapter |
| Lazy Class | 43 | Lazy Element | Inline Singleton |
| Large Class | 44 | Large Class | Replace Conditional Dispatcher with Command, Replace State-Altering Conditionals with State, Replace Implicit Language with Interpreter |
| Switch Statements | 44 | Repeated Switches | Replace Conditional Dispatcher with Command, Move Accumulation to Visitor |
| Combinatorial Explosion | 45 | new | Replace Implicit Language with Interpreter |
| Oddball Solution | 45 | new | Substitute Algorithm, Unify Interfaces with Adapter |

### 5.3 File format

Same as section 4.2, with a different citation line:

```markdown
# Replace State-Altering Conditionals with State

Kerievsky (2004), ch. 7, p. 166. Direction: to, towards. Pattern: State (GoF, p. 305).
```

A mechanics step that is a Fowler refactoring names it by its 2nd-edition name and links its
file; a refactoring with no 2nd-edition counterpart (such as Extract Interface) is described in
plain words and marked "(1st ed. only)". "When to use" includes the book's liabilities, so the
agent knows when the pattern is not worth it. Examples are original C#, as in section 4.3.
