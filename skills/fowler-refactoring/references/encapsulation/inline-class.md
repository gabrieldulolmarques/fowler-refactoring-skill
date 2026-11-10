# Inline Class

Fowler (2018), ch. 7, p. 186. Formerly / aka: —. Inverse: Extract Class
([extract-class.md](extract-class.md)).

## When to use
Smells: Lazy Element, Speculative Generality, Shotgun Surgery.

- A class has so little left (often after other refactorings moved its members out) that it
  adds a name and an indirection but no meaning. Fold it into the class that uses it most.
- Two classes split their responsibilities badly. It can be easier to merge them first and
  then apply Extract Class ([extract-class.md](extract-class.md)) along the right line than to shuffle
  members one by one.
- Do not use it when the class has several unrelated clients that would each need the same
  members copied or re-exposed, or when it carries a real responsibility that just happens to
  be small.

## Mechanics
1. Pick the target: the class that uses the source class most.
2. In the target, add a delegating member for every public member of the source that clients
   use. Each one just forwards to the source object.
3. Compile and test.
4. Redirect clients one at a time so they call the target's delegators instead of reaching
   through to the source. Compile and test after each change.
5. Inline any source method that only makes sense as a whole (see [inline-function.md](../first-set/inline-function.md))
   so its body lives in the target.
6. Move the source's fields and methods into the target one at a time, replacing each
   delegator with the real member. Compile and test after each move.
7. Move any construction or initialization of the source's data into the target's
   constructor.
8. When the source class is empty and nothing references it, delete it. Compile and test.

## Example
Before: `PaymentTerms` holds little and is only used by `Invoice`.

```csharp
public class PaymentTerms
{
    public int NetDays { get; set; }
    public string Label { get; set; } = "";

    public string Describe() => $"{Label} (net {NetDays} days)";
}

public class Invoice
{
    public PaymentTerms Terms { get; } = new PaymentTerms();
    public DateTime IssuedOn { get; init; }

    public DateTime DueDate => IssuedOn.AddDays(Terms.NetDays);
    public string TermsSummary => Terms.Describe();
}

// client
invoice.Terms.NetDays = 30;
invoice.Terms.Label = "Standard";
```

Step 2 and 4: add delegators to `Invoice`, then change clients to use them.

```csharp
public int NetDays
{
    get => Terms.NetDays;
    set => Terms.NetDays = value;
}

public string TermsLabel
{
    get => Terms.Label;
    set => Terms.Label = value;
}

// client
invoice.NetDays = 30;
invoice.TermsLabel = "Standard";
```

Steps 5 to 8: move the data and the behavior, then delete `PaymentTerms`.

```csharp
public class Invoice
{
    public DateTime IssuedOn { get; init; }
    public int NetDays { get; set; }
    public string TermsLabel { get; set; } = "";

    public DateTime DueDate => IssuedOn.AddDays(NetDays);
    public string TermsSummary => $"{TermsLabel} (net {NetDays} days)";
}
```

Behavior is unchanged. Only the client code that reached through `Terms` changed shape, and
that happened before the class disappeared.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
