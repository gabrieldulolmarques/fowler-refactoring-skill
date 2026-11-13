# Introduce Assertion

Fowler (2018), ch. 10, p. 302. Formerly / aka: —. Inverse: —.

## When to use
Smell: Comments. A comment that says "this must be positive" or "x is never null here" is
an assumption written for humans only. An assertion states the same thing in code, so
the reader sees it and the runtime can check it.

An assertion marks a programmer error: a condition that must hold if the rest of the
system is correct. Reserve assertions for invariants the design depends on. Skip the
merely plausible ones, because every assertion is one more condition to maintain.

Input from outside the program (files, network, users, other systems) can legitimately be
wrong, so it needs real validation and error handling, not an assertion. An assertion
failure means a bug. Nothing should handle it as a normal outcome.

## Mechanics
1. Find a condition the code assumes to be true at this point.
2. When needed: if the code shape does not allow a statement there (for example a ternary
   expression), first reshape it into plain `if` statements. Test.
3. Add the assertion at that point. Behavior is unchanged as long as the assertion has no
   side effects and the program would work the same with all assertions removed. It is only
   evaluated in Debug builds, so test in Debug. Test.
4. When needed: ask where the bad value would first enter. Often the better place is the setter,
   constructor or factory that produces it, so a failure points at the source and not at
   the code that later uses it. Move or add the assertion there. Test.
5. When needed: if the same condition appears in several assertions, extract it into a named function
   ([extract-function.md](../first-set/extract-function.md)) so it is changed in one place.
6. Remove the comment the assertion replaces.

## Example
Before:

```csharp
public class Promotion
{
    public string? Code { get; }
    public string? SeasonName { get; }

    public Promotion(string? code, string? seasonName)
    {
        Code = code;
        SeasonName = seasonName;
    }

    public string Label()
    {
        // a promotion always has a coupon code or a season name
        return string.IsNullOrEmpty(Code) ? SeasonName! : Code;
    }
}
```

After (the check lives in the constructor, where a bad pair would first enter):

```csharp
using System.Diagnostics;

public class Promotion
{
    public string? Code { get; }
    public string? SeasonName { get; }

    public Promotion(string? code, string? seasonName)
    {
        Debug.Assert(
            !string.IsNullOrEmpty(code) || !string.IsNullOrEmpty(seasonName),
            "a promotion needs a coupon code or a season name");
        Code = code;
        SeasonName = seasonName;
    }

    public string Label()
    {
        return string.IsNullOrEmpty(Code) ? SeasonName! : Code;
    }
}
```

## C# notes
- `Debug.Assert` (`System.Diagnostics`) is removed from Release builds, which fits the rule
  that the program must behave the same without assertions. Do not put side effects in the
  asserted expression.
- `Debug.Assert` does not change nullable flow analysis, so the `!` in `Label`
  stays and still hides a possible null when `Code` is empty. The assertion documents the
  invariant; it does not prove it to the compiler.
- If a check must also run in production, it is not an assertion: use real validation
  (for example throwing `ArgumentException`).

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Run the tests in a Debug build so the new assertion is actually evaluated.
