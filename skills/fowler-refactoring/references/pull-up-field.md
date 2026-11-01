# Pull Up Field

Fowler (2018), ch. 12, p. 353. Formerly / aka: —. Inverse: Push Down Field
([push-down-field.md](push-down-field.md)).

## When to use
It removes duplicate data declarations in sibling subclasses. No smell in the catalog links
to it directly.

- Start by reading how sibling subclasses use their fields. If two of them hold the same
  data for the same purpose, the field is a candidate, whatever each one is called.
- Once it sits in the superclass, the duplicate declaration is gone and the code that uses
  it can follow (see [pull-up-method.md](pull-up-method.md)).
- Do not use it when the fields only look alike but mean different things, or when only some
  of the subclasses need the data. Then the field belongs where it is, or in a new
  intermediate class.
- In languages where fields appear on first assignment, with no declaration in the class,
  the same effect comes from [pull-up-constructor-body.md](pull-up-constructor-body.md).

## Mechanics
1. Inspect every use of each candidate field and confirm they all play the same role
   (same meaning, same unit, same lifetime).
2. If the names differ, rename them to one name with [rename-field.md](rename-field.md). Compile and test.
3. Declare the field in the superclass, with visibility that subclasses can reach
   (`protected`, or private with a property if you prefer to encapsulate it).
4. Delete the field from the subclasses, one at a time if there are many.
5. Compile and run the tests.

## Example
Before: two kinds of invoice each keep their own `customerName`.

```csharp
public abstract class Invoice
{
    public abstract decimal Total();
}

public class ServiceInvoice : Invoice
{
    private string customerName;
    private decimal hours;
    private decimal rate;

    public ServiceInvoice(string customerName, decimal hours, decimal rate)
    {
        this.customerName = customerName;
        this.hours = hours;
        this.rate = rate;
    }

    public string Describe() => $"Service for {customerName}";
    public override decimal Total() => hours * rate;
}

public class ProductInvoice : Invoice
{
    private string customerName;
    private decimal unitPrice;
    private int quantity;

    public ProductInvoice(string customerName, decimal unitPrice, int quantity)
    {
        this.customerName = customerName;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
    }

    public string Describe() => $"Products for {customerName}";
    public override decimal Total() => unitPrice * quantity;
}
```

After: the field is declared once in `Invoice`. The subclass constructors still assign it,
which [pull-up-constructor-body.md](pull-up-constructor-body.md) can then tidy. The `= ""`
initializer avoids warning CS8618 when nullable reference types are enabled; it can go once
the assignment moves into an `Invoice` constructor.

```csharp
public abstract class Invoice
{
    protected string customerName = "";

    public abstract decimal Total();
}

public class ServiceInvoice : Invoice
{
    private decimal hours;
    private decimal rate;

    public ServiceInvoice(string customerName, decimal hours, decimal rate)
    {
        this.customerName = customerName;
        this.hours = hours;
        this.rate = rate;
    }

    public string Describe() => $"Service for {customerName}";
    public override decimal Total() => hours * rate;
}

public class ProductInvoice : Invoice
{
    private decimal unitPrice;
    private int quantity;

    public ProductInvoice(string customerName, decimal unitPrice, int quantity)
    {
        this.customerName = customerName;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
    }

    public string Describe() => $"Products for {customerName}";
    public override decimal Total() => unitPrice * quantity;
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every subclass constructor still compiles after its own field is deleted, and the output of
  `Describe()` and `Total()` is unchanged.
