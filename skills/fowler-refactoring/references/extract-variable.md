# Extract Variable

Fowler (2018), ch. 6, p. 119. Formerly / aka: Introduce Explaining Variable. Inverse: Inline
Variable ([inline-variable.md](inline-variable.md)).

## When to use
- An expression mixes several ideas and the reader has to decode it, or a comment exists only
  to say what a piece of it means. A well-named variable makes the comment unnecessary.
- The same sub-expression appears more than once and deserves one name.
- You want a place to put a breakpoint or a log call on an intermediate value.

Scope the name before extracting it. If it only makes sense inside this function, a local
variable is right. If it describes something about the whole object (or is useful to other
callers), make it a method or property instead, with Extract Function
([extract-function.md](extract-function.md)) or later with Replace Temp with Query ([replace-temp-with-query.md](replace-temp-with-query.md)).
Prefer the wider scope when it is cheap, because the name then becomes available everywhere.

Do not use it when the name would add nothing the expression does not already say (that is the
case for Inline Variable).

## Mechanics
1. Make sure the expression has no side effects, and that evaluating it once instead of
   several times changes nothing.
2. Declare an immutable local variable (`var` or an explicit type, never reassigned) and
   initialize it with a copy of the expression.
3. Replace the original expression with the variable.
4. Compile and run the tests.
5. If the same expression shows up elsewhere in the scope, swap those spots for the variable
   too, one spot per step, and run the tests between swaps.
6. Delete any comment that now only repeats what the variable name says.

## Example
Before:

```csharp
public bool CanApproveCredit(Customer customer, Account account)
{
    // adult, using over half the limit, and not frozen
    return customer.Age >= 18
        && account.Balance > account.Limit * 0.5m
        && !account.IsFrozen;
}
```

After extracting each condition, one at a time with the tests run after each step (this is the
end state):

```csharp
public bool CanApproveCredit(Customer customer, Account account)
{
    var isAdult = customer.Age >= 18;
    var usesOverHalfOfLimit = account.Balance > account.Limit * 0.5m;
    var isActive = !account.IsFrozen;
    return isAdult && usesOverHalfOfLimit && isActive;
}
```

If a name such as `isActive` is also meaningful to other members of `Account`, make it a
read-only property of the class instead of a local.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
