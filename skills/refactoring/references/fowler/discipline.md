# Refactoring discipline

Fowler (2018), ch. 2, pp. 45-70, and ch. 4, pp. 85-100. Paraphrased.

## What counts as refactoring

A change to internal structure that makes code easier to understand and cheaper to change **without changing observable behavior** (ch. 2, p. 45). It is a chain of small steps, each one leaving the code working. If the code is broken for days, it is not refactoring. Nothing a user cares about may change; a bug you find stays a bug until you finish and fix it separately.

Performance tuning is different: it accepts harder-to-read code in exchange for speed. Refactoring may speed things up or slow them down, because its goal is clarity.

## Two hats

Wear one at a time (ch. 2, p. 46):

- **Feature hat:** add behavior and tests; do not restructure.
- **Refactoring hat:** restructure; add no behavior and no tests (except for a case you missed). Change tests only when an interface changed.

Swap often, but know which one you are wearing.

## When to refactor

Mostly opportunistically, as part of other work (ch. 2, pp. 50-53):

- **Rule of three:** tolerate duplication twice, refactor on the third.
- **Preparatory:** just before adding a feature or fixing a bug, reshape the code so the change becomes easy.
- **Comprehension:** when you had to puzzle over code, put what you learned back into the code (names, structure).
- **Litter pickup:** small cleanups on the way; note larger ones and come back.
- **Planned/long-term:** rare; spread large efforts across everyday changes instead of one block of time.

## The loop

1. **Green baseline.** Run the tests. Do not begin or carry on while any test fails. If a failure shows up mid-way, go back to the last passing version.
2. **One small step** from the refactoring's mechanics.
3. **Compile and run the tests.** Compiling alone is not enough: references by name, reflection and serialized data are invisible to the compiler.
4. **Commit** after each refactoring that is done and green. Commit more often if a step is risky. Keeping refactoring commits apart from feature commits is a default, not a law: the book (p. 53) leaves it to the team. The default has a practical payoff, since each refactoring commit becomes a safe point to revert to.
5. **Repeat** with the next smell.

Small steps feel slower but are faster in total: you almost never debug, because the last change is the only suspect.

## Tests first (ch. 4)

Refactoring needs self-checking tests: they run on their own and report pass/fail. They are the detector for the mistakes you will make.

- No tests around the code you want to change? Write them first, then refactor.
- Write the test for new behavior before the code when you can; it forces you to think about the interface.
- Test what could break (risk-driven), not every getter and setter. A few tests on the riskiest logic beat a plan for complete coverage that never gets written.
- **See each new test fail once.** Temporarily break the code (for example, flip a comparison or return a constant) and confirm the test goes red, then undo. A test that cannot fail protects nothing.
- Probe boundaries: empty collections, zero, negative or out-of-range values, and the error paths, where bugs tend to cluster.
- Keep tests independent: build fresh objects per test instead of sharing a mutable fixture, so one test cannot break another.
- Use `Introduce Assertion` ([introduce-assertion.md](conditional-logic/introduce-assertion.md)) to state a rule the code assumes, so a violation fails loudly.
- Run the tests that cover the code you touch every few minutes, and the whole suite at least daily.

## When not to refactor

- Code you do not need to change: ugly but stable code can stay as it is.
- Code that is easier to rewrite than to reshape: start over instead of a long chain of steps (ch. 2, p. 55).
- Renaming or changing a published interface (used by code you cannot edit, such as a package or other teams) needs a transition: keep the old one forwarding to the new one for a while (ch. 2, p. 57).

## Beyond the book: legacy code without tests

Not from Fowler's ch. 2-4.

A **characterization test** pins down what code does today (assert the current output), even if that output looks odd. Use it before restructuring code that has no tests.

General practice, also outside the book: anything referenced by name from outside the code (configuration, reflection, serialized data, scripts) needs a search before it is renamed, moved or removed, because the compiler will not catch a broken reference.

## Commit message

One line, in whatever format the project uses for commits, describing a single refactoring.

## Verification checklist (same for every refactoring)

- Compiles with no new warnings.
- The tests pass (the new tests failed once before they passed).
- Committed on green, behavior unchanged.
