# Replace Function with Command

Fowler (2018), ch. 11, p. 337. Formerly / aka: Replace Method with Method Object. Inverse:
Replace Command with Function ([replace-command-with-function.md](replace-command-with-function.md)).

## When to use
Smell: Long Function. The typical trigger is a function whose locals and parameters are so
intertwined that Extract Function would need long parameter lists or return several values.
Turning the function into an object makes those locals fields, so the pieces can share them.

A command also helps when the operation needs more than a call can offer: undo, being queued or
logged, parameters supplied in stages, subclass or hook customization, or tests aimed at its
inner steps.

Do not use it by default. A command is extra structure; a plain function (or delegate) is the
better choice most of the time. Reach for a command only when a simpler device cannot give you
what you need.

## Mechanics
1. Create an empty class named after the function (follow the language's naming convention for
   commands).
2. Apply Move Function ([move-function.md](move-function.md)) to move the function body into the class as a
   single method. Use the convention's name for it, or a generic one such as `Execute`.
   Leave the original function in place as a forwarder that creates the command and calls it;
   keep it until the end.
3. Compile and test.
4. Move the arguments to the constructor one at a time: add a field and a constructor
   parameter, pass it from the forwarder, remove it from the method's parameter list and
   update its uses in the body. Compile and test after each one.
5. Optionally, to enable decomposition: promote the local variables to fields, one at a time,
   compiling and testing after each.
6. Now apply Extract Function ([extract-function.md](extract-function.md)) to the body; the new methods read
   and write the fields directly.

## Example
Before: a function that prices an invoice, with several interacting locals.

```csharp
public record Customer(string Region, bool IsPreferred);
public record Order(int Units, decimal UnitPrice);
public interface ITaxTable { decimal RateFor(string region); }

public static class Billing
{
    public static decimal InvoiceTotal(Order order, Customer customer, ITaxTable taxes)
    {
        decimal subtotal = order.Units * order.UnitPrice;
        decimal discount = 0m;
        if (order.Units > 100)
            discount += subtotal * 0.05m;
        if (customer.IsPreferred)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * taxes.RateFor(customer.Region);
        return taxable + tax;
    }
}
```

After steps 1 to 4 (the forwarder stays, the command owns the arguments):

```csharp
public static class Billing
{
    public static decimal InvoiceTotal(Order order, Customer customer, ITaxTable taxes)
        => new InvoiceTotalCalculator(order, customer, taxes).Execute();
}

public class InvoiceTotalCalculator
{
    private readonly Order _order;
    private readonly Customer _customer;
    private readonly ITaxTable _taxes;

    public InvoiceTotalCalculator(Order order, Customer customer, ITaxTable taxes)
    {
        _order = order;
        _customer = customer;
        _taxes = taxes;
    }

    public decimal Execute()
    {
        decimal subtotal = _order.Units * _order.UnitPrice;
        decimal discount = 0m;
        if (_order.Units > 100)
            discount += subtotal * 0.05m;
        if (_customer.IsPreferred)
            discount += subtotal * 0.02m;
        decimal taxable = subtotal - discount;
        decimal tax = taxable * _taxes.RateFor(_customer.Region);
        return taxable + tax;
    }
}
```

After steps 5 and 6 (locals promoted to fields, then pieces extracted):

```csharp
public class InvoiceTotalCalculator
{
    private readonly Order _order;
    private readonly Customer _customer;
    private readonly ITaxTable _taxes;
    private decimal _subtotal;
    private decimal _discount;

    public InvoiceTotalCalculator(Order order, Customer customer, ITaxTable taxes)
    {
        _order = order;
        _customer = customer;
        _taxes = taxes;
    }

    public decimal Execute()
    {
        _subtotal = _order.Units * _order.UnitPrice;
        ApplyDiscounts();
        decimal taxable = _subtotal - _discount;
        return taxable + taxable * _taxes.RateFor(_customer.Region);
    }

    private void ApplyDiscounts()
    {
        _discount = 0m;
        if (_order.Units > 100)
            _discount += _subtotal * 0.05m;
        if (_customer.IsPreferred)
            _discount += _subtotal * 0.02m;
    }
}
```

Behavior is the same at every stage. Note that `Execute` now mutates fields, so a command
instance is single-use unless the fields are reset at the start of `Execute`.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
