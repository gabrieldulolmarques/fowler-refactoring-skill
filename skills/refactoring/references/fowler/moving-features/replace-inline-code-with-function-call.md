# Replace Inline Code with Function Call

Fowler (2018), ch. 8, p. 222. Formerly / aka: —. Inverse: —.

## When to use
- Inline code does the same job as a function that already exists in the codebase or in the
  standard library (a manual loop that searches, sums, joins or tests membership).
- The same logic is copied in several places and one copy already lives in a named function.
- Duplication is the usual symptom (see Duplicated Code in [smells.md](../../smells.md)).

Before replacing, read the function name in place of the inline code. If the name reads
naturally there, replace it. If it does not, either the name is poor (fix it with
[change-function-declaration.md](../first-set/change-function-declaration.md)) or the function has a different purpose and the
similarity is a coincidence. In that case, leave the code alone: if you would change the
function body without wanting this code to change, they are not the same thing.

## Mechanics
1. Confirm the existing function does exactly what the inline code does, including edge
   cases (empty input, null, ordering, case sensitivity, side effects).
2. Replace the inline code with a call to the function.
3. Compile and run the tests.
4. Repeat for the other copies, one at a time, testing after each.

## Example
Before:

```csharp
public class ShippingPolicy
{
    private static readonly string[] RestrictedCountries = { "KP", "IR", "SY" };

    public bool IsRestricted(string countryCode)
    {
        bool restricted = false;
        foreach (var code in RestrictedCountries)
        {
            if (code == countryCode)
            {
                restricted = true;
            }
        }
        return restricted;
    }
}
```

After:

```csharp
public class ShippingPolicy
{
    private static readonly string[] RestrictedCountries = { "KP", "IR", "SY" };

    public bool IsRestricted(string countryCode)
    {
        return RestrictedCountries.Contains(countryCode);
    }
}
```

(`Contains` on an array comes from `System.Linq`; add `using System.Linq;` where needed.)
Behavior is unchanged: both return true when the code is in the list.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
