# Discipline for refactoring to patterns

Kerievsky (2004), ch. 1-3. Paraphrased.

## The goal is a better design, not a pattern

Refactoring to a pattern has the same motivations as any refactoring: remove duplication, simplify
what is complicated, and make the code say what it means (ch. 1). A pattern is a destination that
can serve those goals, never a goal of its own. After refactoring to or towards a pattern, check
that the design really improved; if it did not, back out or go another way (ch. 3, pp. 29-31).

## Over-engineering and under-engineering

- **Over-engineering** (ch. 1, pp. 1-2): code more flexible or sophisticated than today's needs, built
  for a future that may not come. It is rarely removed, makes the code base bigger than it needs to
  be, and costs everyone time to learn.
- **Under-engineering** (ch. 1, pp. 3-4): poorly designed code written in a hurry, with no time to
  refactor. Each release gets slower than the last, until a rewrite looks like the only way out.
- Avoid both by evolving the design: add a pattern when the code asks for it, through refactoring,
  not up front "just in case" (ch. 1, p. 8).

## Patterns happy

Being *patterns happy* means using patterns because you like them, not because the code needs them
(ch. 3, p. 24). The result is pattern-dense code that is harder to read than a simple conditional
or a plain class. Before applying a refactoring to a pattern, ask whether a simpler change removes
the smell. When a pattern no longer pays for itself, refactor away from it.

## Test-driven development and continuous refactoring

Write a failing test, make it pass in the simplest way, then refactor (red, green, refactor; ch. 1,
pp. 4-6). Refactor continuously, a little at a time, instead of saving it for later (ch. 1, p. 5).
Patterns then appear when duplication or complexity calls for them.

## Small steps

Combining several refactorings into one big step feels faster but is slower: the tests stay red for
a long time and the fixes pile up (ch. 2, pp. 14-15). If the tests have been failing for more than a
few minutes, the step is too big: go back to the last green state and take a smaller one.

## Composite and test-driven refactorings

- Almost every refactoring to a pattern is **composite**: a sequence of low-level refactorings
  (mostly Fowler's), with the tests run between each one (ch. 2, pp. 17-20). The book's mechanics
  give an order that works; you can certainly apply the steps in another order if you see fit.
- A **test-driven refactoring** writes the replacement with test-driven development and then swaps
  it in for the old code, keeping and rerunning the old code's tests (ch. 2, pp. 17-19). Use it when
  the new design is too far from the current one to reach by moving code around, as when
  substituting an algorithm or introducing a Builder.

## To, towards and away

- Some refactorings only help if you go all the way **to** the pattern: half a Template Method
  removes no duplication.
- Others already improve the design partway: going **towards** a Decorator or a Command may be
  enough, and you can stop as soon as the smell is gone.
- Refactoring **away** from a pattern is just as legitimate: remove a Singleton or an Iterator when
  the design is better without it.

Each reference file states its direction (ch. 3, pp. 29-31).

## Many ways to implement a pattern

A pattern's usual class diagram is one example, not a specification (ch. 3, p. 26). Implement only
what the code needs, with your own names; a minimal pattern is the normal result of evolving a
design.

## Do patterns make code more complex?

Code with a pattern looks more complex to someone who does not know the pattern (ch. 3). Prefer
teaching the pattern to the team over avoiding it, but if an implementation really is more complex
than the problem, simplify it or refactor away from it.

## Design up front with patterns only rarely

Designing with patterns before writing code is sometimes justified, for example when a detailed
design must be presented before the work starts and the requirements are small and fixed (ch. 3,
pp. 33-35). Otherwise evolve the system and refactor to, towards or away from patterns as needed.

## Design debt

Design debt builds up whenever duplication is not removed, code is not simplified, or intent is not
made clear (ch. 2, pp. 15-16). Like financial debt, it grows if it is not paid down; paying it a
little at a time, through continuous refactoring, keeps the code easy to change.

## Verification checklist (same for every refactoring to a pattern)

- Compiles and the tests pass after every low-level step; one commit per refactoring.
- The smell that motivated the refactoring is gone.
- The design is simpler than before for someone who knows the pattern; if not, back out or go
  another way.
