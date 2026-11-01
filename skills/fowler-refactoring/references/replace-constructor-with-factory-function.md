# Replace Constructor with Factory Function

Fowler (2018), ch. 11, p. 334. Formerly / aka: formerly Replace Constructor with Factory Method. Inverse: —.

## When to use
- Constructors have limits: they cannot be renamed per use, so `new Account(id, 'S')` says little about what is created. A named factory (`Account.CreateSavings(id)`) says it.
- Callers pass a literal type code or flag only to pick a variant. That is a smell in itself, and the factory can hide the code behind a descriptive name.
- Creation may need to return a subclass, a shared or cached instance, or a special-case object. A constructor always returns a new instance of exactly its own class.
- Do not bother when the constructor is already clear and has a single obvious way to be called.

## Mechanics
1. Create a factory function whose body only calls the constructor with the same arguments.
2. Replace one call to the constructor with a call to the factory. Compile and test.
3. Repeat step 2 for every caller, one at a time.
4. Where a caller passes a literal code, add a more specific factory that embeds that choice in its name, and switch the caller to it.
5. Reduce the constructor's visibility as far as possible (`private` or `protected`), so new code cannot bypass the factory. Compile and test.

## Example
Before:

```csharp
using System;

public class Invoice
{
    public string Customer { get; }
    public string KindCode { get; }

    public Invoice(string customer, string kindCode)
    {
        Customer = customer;
        KindCode = kindCode;
    }

    public string Kind => KindCode switch
    {
        "R" => "Recurring",
        "O" => "OneOff",
        _ => throw new ArgumentException("Unknown kind")
    };
}

// callers
var a = new Invoice(row.Customer, row.KindCode);
var b = new Invoice("Acme", "R");
```

After:

```csharp
using System;

public class Invoice
{
    public string Customer { get; }
    public string KindCode { get; }

    private Invoice(string customer, string kindCode)
    {
        Customer = customer;
        KindCode = kindCode;
    }

    public static Invoice Create(string customer, string kindCode) =>
        new Invoice(customer, kindCode);

    public static Invoice CreateRecurring(string customer) =>
        new Invoice(customer, "R");

    public string Kind => KindCode switch
    {
        "R" => "Recurring",
        "O" => "OneOff",
        _ => throw new ArgumentException("Unknown kind")
    };
}

// callers
var a = Invoice.Create(row.Customer, row.KindCode);
var b = Invoice.CreateRecurring("Acme");
```

Behavior is the same; the literal code no longer appears in `b`'s call site.

## C# notes
- The factory is a static factory method. Make the constructor `private` (or `protected` if subclasses must call it) once every caller has moved.
- If the factory must return a subclass, a `private` base constructor stops outside subclasses from deriving. Either nest the subclasses in the base class, or make the base constructor `protected` or `private protected`. Keep the subclass constructors `internal` or `private` so only the factory reaches them.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
