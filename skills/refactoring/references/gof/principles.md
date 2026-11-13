# Design principles and how to use a pattern

Gamma et al. (1995), ch. 1 and ch. 6, §6.1. Paraphrased. The catalog of patterns is in
[catalog.md](catalog.md).

## What a pattern is (§1.1, §1.3)

A design pattern names a recurring design problem and the core of a solution that can be reused
without ever being implemented the same way twice. Each pattern has four essential parts:

- a **name**, which becomes part of the team's vocabulary;
- the **problem**, which says when to apply it;
- the **solution**, which describes the elements, their responsibilities and collaborations, as a
  template rather than a concrete design;
- the **consequences**, the benefits and costs of applying it, which decide whether it is worth it.

The pattern files in this folder follow that order: intent, when it pays off, participants, example,
variations, risks.

## Principles of reusable object-oriented design (§1.6)

- **Program to an interface, not an implementation** (pp. 16-18). Declare variables, parameters and
  fields with interfaces or abstract types. Clients then do not depend on concrete classes, only on
  the operations they use, and any object that implements the interface can take part. The
  creational patterns exist largely so that concrete classes are named in as few places as possible.
- **Favor object composition over class inheritance** (pp. 18-20). Inheritance is reuse decided at
  compile time, and it exposes the parent's internals to the subclass, so a change in the parent can
  break subclasses. Composition is decided at run time, through interfaces, keeps each class
  encapsulated and focused, and lets you change behavior by plugging in another object. Use
  inheritance where it is the simplest fit, but do not reach for it first.
- **Delegation** (pp. 20-21). An object hands part of a request to another object it holds, instead
  of inheriting the behavior. It makes composition as powerful as inheritance (State, Strategy and
  Visitor rely on it), at the cost of designs that are more dynamic and harder to follow.
- **Inheritance versus parameterized types** (pp. 21-22). Generics are a third way to vary behavior,
  by the types an operation works with, fixed at compile time.
- **Run-time structure is not the code structure** (pp. 22-23). The classes show what objects may
  hold or know (aggregation, acquaintance); the actual network of objects at run time is only
  visible when the program runs. Many patterns, such as Observer, Composite and Chain of
  Responsibility, are easier to understand from the run-time structure.
- **Design for change** (p. 24). Most redesign has a few known causes: naming concrete classes,
  hard-coding requests, platform dependence, exposing representations, algorithm dependence, tight
  coupling, extending only by subclassing, and classes that cannot be changed. Each pattern lets one
  aspect vary on its own; [catalog.md](catalog.md) maps each cause to the patterns that prevent it.
- **Applications, toolkits and frameworks** (pp. 25-27). Application code values internal reuse and
  easy change; libraries and toolkits must avoid assumptions about their users; frameworks fix the
  architecture and call your code, so their patterns must be chosen with the most care.

## How to select a pattern (§1.7, p. 28)

The book gives six alternative approaches to finding the pattern for a problem. They are not steps;
use whichever suits the situation, or combine them.

- **How patterns solve design problems.** §1.6 of the book covers finding objects, object
  granularity, specifying interfaces and the other points of that section. The list above
  summarizes only the principles that matter most for the code here, so go to the book for the rest.
- **Scan the intents.** Read the intents in [catalog.md](catalog.md) and narrow the list by purpose
  and scope (Table 1.1, p. 10).
- **Study how the patterns relate.** Figure 1.1 (p. 12) of the book draws the relationships between
  patterns; it is not reproduced here.
- **Study patterns of like purpose.** The comparison that closes each category in
  [catalog.md](catalog.md) shows what separates similar patterns.
- **Examine a cause of redesign.** Check whether the problem matches one of the causes, and look at
  the patterns that prevent it ([catalog.md](catalog.md), p. 24).
- **Consider what should be variable.** The reverse of the previous approach: decide what you want
  to be able to change without redesign, and pick the pattern that lets that aspect vary.
  Isolating whatever varies is the idea behind many of the patterns.

## How to use a pattern (§1.8, p. 29)

1. Read the whole pattern once, paying most attention to when it pays off and its consequences.
2. Study the participants and how they collaborate.
3. Look at the example to see the pattern in code.
4. Name the participants after the application, keeping a hint of the role when it helps
   (`ShippingStrategy`, `OrderBuilder`).
5. Declare the types: interfaces, inheritance, fields and references. Identify the existing classes
   the pattern touches and change them.
6. Name the operations after their responsibilities, consistently (for example, always `Create...`
   for factory methods).
7. Implement the operations, using the variations as a guide.

**When not to use a pattern** (§1.8). Patterns buy flexibility with extra indirection, which can
make a design more complicated and slower. Apply a pattern only when the flexibility it gives is
actually needed; its consequences say what it costs.

## What to expect from patterns (§6.1, pp. 351-354)

- **A common vocabulary** (p. 352): "use an Observer here" says in three words what would take a
  paragraph, and makes designs easier to discuss and review.
- **Documentation and learning:** naming the patterns a system uses makes it much easier to
  understand.
- **A complement to design methods:** patterns show how to use objects, inheritance and
  polymorphism well, and help move from a model of the problem to working code.
- **A target for refactoring** (p. 353): software grows in phases, from prototyping to expanding
  to consolidating. In the consolidating phase it is reorganized, and many patterns are the
  structures that this reorganization arrives at. Knowing them helps you see where to take a design,
  even when the pattern only becomes visible after the system is built.

## Verification checklist (same for every pattern)

- The problem the pattern solves is present in the code, not expected some day.
- The participants have names from the domain, and clients depend on interfaces, not on the
  concrete classes the pattern introduced.
- The design is simpler to change in the way the pattern promises, and the extra indirection is
  worth it.
- Compiles and the tests pass; behavior is unchanged where the pattern was introduced by
  refactoring.
