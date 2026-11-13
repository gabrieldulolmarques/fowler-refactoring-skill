# Parameterize Function

Fowler (2018), ch. 11, p. 310. Formerly / aka: Parameterize Method. Inverse: —.

## When to use
Two or more functions have the same shape and differ only in literal values. Folding them into one function with parameters removes the duplication, and
the single function can then be reused with values nobody wrote a variant for.

Not a fit when the functions differ in structure rather than in values: forcing them into one
function leads to a pile of parameters and branches. If a parameter would only select which
logic runs, that is a flag argument, not a value (see [remove-flag-argument.md](remove-flag-argument.md)).

## Mechanics
1. Pick one of the similar functions as the base. For range-like families, the middle case is
   often a good choice, since it tends to use every literal that the others use.
2. Add a parameter for each literal that varies, using [change-function-declaration.md](../first-set/change-function-declaration.md)
   (rename the function too if the old name no longer fits). Compile.
3. Update every caller of that function to pass the literal it used to rely on. Test.
4. In the body, replace each literal with its parameter, one at a time. Test after each one.
5. For each similar function, replace its callers with a call to the parameterized function,
   passing that function's values. Test after each one. Then delete the old function.
6. If the parameterized function cannot express a variant, adjust it for that variant
   (a sentinel such as an open-ended limit often works) before moving on to the next one.

## Example
Before:

```csharp
public class MessagePreview
{
    public string SmsPreview(string body)
    {
        return body.Length <= 160 ? body : body.Substring(0, 157) + "...";
    }

    public string PushPreview(string body)
    {
        return body.Length <= 40 ? body : body.Substring(0, 37) + "...";
    }
}
```

After:

```csharp
public class MessagePreview
{
    public string Preview(string body, int maxLength)
    {
        return body.Length <= maxLength ? body : body.Substring(0, maxLength - 3) + "...";
    }
}

// callers
// preview.Preview(body, 160);  // was SmsPreview
// preview.Preview(body, 40);   // was PushPreview
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
