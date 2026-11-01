# Extract Class

Fowler (2018), ch. 7, p. 182. Formerly / aka: —. Inverse: Inline Class
([inline-class.md](inline-class.md)).

## When to use
Smells: Large Class, Divergent Change, Data Clumps, Primitive Obsession, Temporary Field.

- A class has grown into many fields and methods, and part of it can be understood on its own.
- A subset of the fields and methods belongs together: the fields change together or depend on each other.
- Test: remove one field or method in your head. If other members become meaningless, they belong in the same extracted class.
- Subtyping or variation affects only some of the class's features, or different features vary in different ways.

Do not use it when the pieces are tightly entangled with the rest and there is no clear
responsibility to name. Also skip it for a class that is small and cohesive.

## Mechanics
1. Decide which responsibility to split off and name it.
2. Create the new, empty class. If the original's name no longer describes what is left, rename it.
3. Give the original an instance of the new class, created in its constructor, and keep it in a private field.
4. Move the fields one at a time ([move-field.md](move-field.md)). The original's members now delegate to the new class. Compile and test after each field.
5. Move the methods one at a time ([move-function.md](move-function.md)), starting with the lowest-level ones (those that are called rather than those that call). Compile and test after each method.
6. Review both public interfaces: remove methods that are no longer needed and rename members to fit their new context (the new class does not need the old prefixes or qualifiers).
7. Decide whether to expose the new object to clients. If so, consider making it a value object ([change-reference-to-value.md](change-reference-to-value.md)) first.

## Example
Before: an invoice class that also holds the billing address data.

```csharp
public class Invoice
{
    private decimal _amount;
    private string _billingStreet;
    private string _billingCity;
    private string _billingZip;

    public Invoice(decimal amount, string street, string city, string zip)
    {
        _amount = amount;
        _billingStreet = street;
        _billingCity = city;
        _billingZip = zip;
    }

    public decimal Amount => _amount;
    public string BillingStreet => _billingStreet;
    public string BillingCity => _billingCity;
    public string BillingZip => _billingZip;

    public string BillingLabel => $"{_billingStreet}, {_billingCity} {_billingZip}";
}
```

After: the address data and behavior live in `Address`; `Invoice` keeps its public members
as delegates, so callers do not change.

```csharp
public class Address
{
    public Address(string street, string city, string zip)
    {
        Street = street;
        City = city;
        Zip = zip;
    }

    public string Street { get; }
    public string City { get; }
    public string Zip { get; }

    public override string ToString() => $"{Street}, {City} {Zip}";
}

public class Invoice
{
    private readonly decimal _amount;
    private readonly Address _billingAddress;

    public Invoice(decimal amount, string street, string city, string zip)
    {
        _amount = amount;
        _billingAddress = new Address(street, city, zip);
    }

    public decimal Amount => _amount;
    public string BillingStreet => _billingAddress.Street;
    public string BillingCity => _billingAddress.City;
    public string BillingZip => _billingAddress.Zip;

    public string BillingLabel => _billingAddress.ToString();
}
```

A later step can expose `Address` to clients and drop the `Billing*` delegates.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged: the original class's public members return the same values as before.
