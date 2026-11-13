# Replace Magic Literal

Fowler (2018), web edition only (not in the print book); summary at https://refactoring.com/catalog/replaceMagicLiteral.html. Formerly / aka: Replace Magic Number with Symbolic Constant. Inverse: —.

## When to use
A literal value sits in an expression and its meaning has to be guessed: a tax rate, a time unit, a physical constant, a status string, a size limit. The same value repeated in several places is worse, because a change means finding every copy and telling apart the ones that mean the same thing from the ones that only look alike.

Do not extract every literal. `0`, `1`, `""` or `-1` in an obvious role (a loop start, an empty check, "not found") are usually clearer as they are. When the literal is really a set of related alternatives, an `enum` or a type is a better home than a loose constant.

## Mechanics
1. Declare a constant with a name that says what the value means, not what it is (`StandardGravity`, not `NineEightOne`).
2. Find the occurrences of the literal. For each one, decide whether it has the same meaning as the constant; equal values with different meanings get their own constants or stay as they are.
3. Replace one occurrence with the constant. Compile and test.
4. Repeat for the remaining occurrences of that meaning, testing as you go.
5. To check the result, change the constant's value temporarily and see whether the tests notice everywhere they should. It is not always possible, but it is a cheap check when it is.

## Example
Before:

```csharp
public class TemperatureConverter
{
    public double ToKelvin(double celsius)
    {
        return celsius + 273.15;
    }

    public double ToCelsius(double kelvin)
    {
        return kelvin - 273.15;
    }
}
```

After:

```csharp
public class TemperatureConverter
{
    private const double KelvinOffset = 273.15;

    public double ToKelvin(double celsius)
    {
        return celsius + KelvinOffset;
    }

    public double ToCelsius(double kelvin)
    {
        return kelvin - KelvinOffset;
    }
}
```

Behavior is unchanged, and the relation between the two methods is now visible.

## C# notes
- `const` is limited to primitives, `string` and `null`. Use it for compile-time values, `static readonly` for the rest (computed at startup, or of a type that cannot be `const`).
- A `const` from another assembly is inlined at compile time, so changing its value requires recompiling the consumers; prefer `static readonly` for public values that may change.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Search the code for the old literal to confirm no occurrence of that meaning remains, and that occurrences of the same value with a different meaning were left alone.
