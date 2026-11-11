# Replace Exception with Precheck

Fowler (2018), web edition only (not in the print book); summary at https://refactoring.com/catalog/replaceExceptionWithPrecheck.html. Formerly / aka: Replace Exception with Test. Inverse: —.

## When to use
A `try`/`catch` exists to handle a condition that is not exceptional: the caller can know in advance that it may happen, and the catch block just supplies a default or takes the alternative path. Exceptions are for unexpected failures; using them as a branch hides the normal flow, costs more at run time and can swallow real errors of the same type.

Replace the handler with a conditional that tests the condition first, then runs the operation only when it is safe.

Do not use it when the condition cannot be tested reliably before the call (for example another thread may change it in between, or the only way to know is to attempt the operation, as with many file or network operations, or the precheck would repeat an expensive operation). Then keep the exception, or use a `Try...` method that does check and act in one step. Also keep it when the exception signals a real fault that should not be silently replaced by a default.

## Mechanics
1. Identify the exact condition that makes the operation throw, and the value or path the catch block uses in response.
2. Add the check as a conditional before the operation, with the catch block's behavior in its branch, while leaving the `try`/`catch` in place. Compile and test.
3. Add an assertion or a temporary log inside the catch block, run the tests, and confirm it is never reached. If it is, the precheck does not cover every case; fix the condition first.
4. Remove the `try`/`catch`, leaving the operation in the safe branch. Compile and test.
5. Remove the temporary assertion or log, and tidy the remaining conditional (for example with a guard clause).

## Example
Before (`_quantities` is an `int[]` field of an `Order`, one entry per line):

```csharp
public int GetLineQuantity(int lineIndex)
{
    try
    {
        return _quantities[lineIndex];
    }
    catch (IndexOutOfRangeException)
    {
        return 0;
    }
}
```

After:

```csharp
public int GetLineQuantity(int lineIndex)
{
    if (lineIndex < 0 || lineIndex >= _quantities.Length)
        return 0;

    return _quantities[lineIndex];
}
```

## C# notes
- Prefer the framework's `TryParse` / `TryGetValue` pattern where it exists: it performs the check and the operation together, so there is no gap between test and use. Example: `if (_prices.TryGetValue(sku, out var price)) return price; return 0m;` instead of catching `KeyNotFoundException`.
- A narrow `catch` makes the condition easy to identify. A broad `catch (Exception)` calls for first finding which cause is intended, since it often hides more than one.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged for every input, including the boundary values (first, last and just outside the valid range) that used to trigger the exception.
