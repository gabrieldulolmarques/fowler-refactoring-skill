# Abstract Factory

Gamma et al. (1995), ch. 3, p. 87. Also known as: Kit. Category: object creational.

## Intent
Offer one interface for creating a whole family of related objects, so client code never names the concrete classes of that family.

## When it pays off
- The system should not depend on how its products are created, composed or represented.
- The system must work with one of several product families (for example one set of classes per region or per provider) and must not depend on which one.
- The products of a family only make sense together, and you want the compiler and the factory, not discipline, to keep them from being mixed.
- You ship a library of products and want to expose only their interfaces, not their implementations.
- Switching the family is a single decision at one place: the concrete factory is created once and handed to the code that needs products.
- It isolates concrete classes: product names appear only inside the concrete factories.
- Liability: adding a new kind of product changes the factory interface and every concrete factory.
- Not worth it when there is only one family, or when the "family" is a single product (a plain [Factory Method](factory-method.md) or a `Func<T>` is enough).

## Participants in C#
- **AbstractFactory** (`ICheckoutFactory`): interface with one creation method per product kind.
- **ConcreteFactory** (`BrazilCheckoutFactory`, `GermanyCheckoutFactory`): classes implementing the interface, each returning the products of one family.
- **AbstractProduct** (`ITaxCalculator`, `IInvoiceFormatter`): one interface per kind of product.
- **ConcreteProduct** (`BrazilTaxCalculator`, `GermanyInvoiceFormatter`, ...): the classes a concrete factory instantiates.
- **Client** (`CheckoutService`): receives an `ICheckoutFactory` and uses only the interfaces.

## Example (C#)
An online checkout must compute tax and format the invoice according to the buyer's country. Tax rules and invoice layout belong together, so each country gets one factory that creates both.

```csharp
using System;
using System.Globalization;

public interface ITaxCalculator
{
    decimal TaxFor(decimal amount);
}

public interface IInvoiceFormatter
{
    string Format(string orderId, decimal amount, decimal tax);
}

public interface ICheckoutFactory
{
    ITaxCalculator CreateTaxCalculator();
    IInvoiceFormatter CreateInvoiceFormatter();
}

public class BrazilTaxCalculator : ITaxCalculator
{
    public decimal TaxFor(decimal amount) => amount * 0.17m;
}

public class BrazilInvoiceFormatter : IInvoiceFormatter
{
    public string Format(string orderId, decimal amount, decimal tax) =>
        string.Format(new CultureInfo("pt-BR"), "Pedido {0}: total {1:N2}, imposto {2:N2}", orderId, amount + tax, tax);
}

public class GermanyTaxCalculator : ITaxCalculator
{
    public decimal TaxFor(decimal amount) => amount * 0.19m;
}

public class GermanyInvoiceFormatter : IInvoiceFormatter
{
    public string Format(string orderId, decimal amount, decimal tax) =>
        string.Format(new CultureInfo("de-DE"), "Bestellung {0}: Summe {1:N2}, MwSt. {2:N2}", orderId, amount + tax, tax);
}

public class BrazilCheckoutFactory : ICheckoutFactory
{
    public ITaxCalculator CreateTaxCalculator() => new BrazilTaxCalculator();
    public IInvoiceFormatter CreateInvoiceFormatter() => new BrazilInvoiceFormatter();
}

public class GermanyCheckoutFactory : ICheckoutFactory
{
    public ITaxCalculator CreateTaxCalculator() => new GermanyTaxCalculator();
    public IInvoiceFormatter CreateInvoiceFormatter() => new GermanyInvoiceFormatter();
}

public class CheckoutService
{
    private readonly ITaxCalculator _tax;
    private readonly IInvoiceFormatter _invoice;

    public CheckoutService(ICheckoutFactory factory)
    {
        _tax = factory.CreateTaxCalculator();
        _invoice = factory.CreateInvoiceFormatter();
    }

    public string Close(string orderId, decimal amount) =>
        _invoice.Format(orderId, amount, _tax.TaxFor(amount));
}

public static class Program
{
    public static void Main()
    {
        // the country is decided once, at the composition point
        ICheckoutFactory factory = new GermanyCheckoutFactory();
        var checkout = new CheckoutService(factory);
        Console.WriteLine(checkout.Close("A-1001", 100m));
    }
}
```

## Variations
- **Factory methods inside the factory.** The usual form: each creation method is a factory method, and a concrete factory implements them. Simple, but it takes one factory class per family.
- **Prototype-based factory.** The factory keeps one prototype of each product and clones it on demand (see [prototype.md](prototype.md)). A new family is then just a new set of prototypes, with no new factory class.
- **Parameterized creation.** One `Create(kind)` method replaces the one-method-per-product interface, so new product kinds need no interface change. The price is type safety: every result comes back as the common base type, and callers that need more must cast.
- **One factory per family, normally one instance.** The factory is usually created once and shared. Handing it down by constructor, as above, is enough; it does not have to be a [Singleton](singleton.md).

## Risks and C# alternatives
- If the family is just "which implementation of this interface", register the implementations in a dependency injection container, selected by configuration (country, tenant). The container is then the abstract factory and no factory interface is written by hand.
- When the product kinds are few and stable, a pair of delegates (`Func<ITaxCalculator>`, `Func<IInvoiceFormatter>`) passed to the client does the same job with less ceremony.
- When families are chosen at runtime by key, keep a `Dictionary<string, ICheckoutFactory>` and fail loudly on an unknown key at the boundary, instead of falling back to a default family.
- Do not let clients receive a factory and then ignore it by constructing concrete classes elsewhere; that breaks the guarantee that a family is never mixed.
- Adding a product kind later forces edits in every factory. If that happens often, the family boundary is probably wrong.

## Related patterns
- [Factory Method](factory-method.md): a concrete factory is usually a set of factory methods.
- [Prototype](prototype.md): an alternative way to implement the concrete factory, by cloning.
- [Singleton](singleton.md): a concrete factory is often a single shared instance.
- [Builder](builder.md): also creates complex objects, but step by step and returns the product at the end; Abstract Factory returns each product at once and stresses families.

## Verification
- No client code outside the composition point names a concrete product or concrete factory class.
- Changing the family requires touching one line (the place the factory is created).
- A test creates each concrete factory and checks that its products belong together (same region, same rules).
- Adding a second family needed new classes only, not edits to the client.
