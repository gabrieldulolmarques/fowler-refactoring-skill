# Composite

Gamma et al. (1995), ch. 4, p. 163. Category: object structural.

## Intent
Arrange objects in a tree of parts and wholes where a single item and a group of items are used through the same interface.

## When it pays off
- The domain is a part-whole hierarchy (a cart with products and bundles, folders and files, nested permission groups) and callers should not care whether a node is a leaf or a group.
- Client code gets simpler: no loops that test the kind of each node, and new node kinds work with existing code.
- Liability: the design can become too general. It is hard to forbid a group from containing certain kinds, since the type system sees every node as the same type. Such rules become runtime checks.
- Skip it when the tree has one fixed depth (a list of items and nothing nested), where a plain collection is clearer.

## Participants in C#
- **Component** (`IPriced`): interface or abstract class for every node. In the example it has one operation, `Total()`, and child management lives only in the composite.
- **Leaf** (`Product`): a node without children, implements the operation directly.
- **Composite** (`Bundle`): holds child components and implements the operation by combining the children's results.
- **Client** (the code in `Main`): works only with the component interface when it prices things.

## Example (C#)
A checkout prices individual products and bundles. A bundle can contain products and other bundles, and applies its own discount to the sum of its children.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public interface IPriced
{
    string Name { get; }
    decimal Total();
}

public class Product : IPriced
{
    public string Name { get; }
    private readonly decimal _price;

    public Product(string name, decimal price)
    {
        Name = name;
        _price = price;
    }

    public decimal Total() => _price;
}

public class Bundle : IPriced
{
    public string Name { get; }
    private readonly decimal _discountRate;
    private readonly List<IPriced> _children = new();

    public Bundle(string name, decimal discountRate)
    {
        Name = name;
        _discountRate = discountRate;
    }

    public Bundle Add(IPriced child)
    {
        if (ReferenceEquals(child, this))
            throw new ArgumentException("A bundle cannot contain itself.");
        _children.Add(child);
        return this;
    }

    public bool Remove(IPriced child) => _children.Remove(child);

    public IEnumerable<IPriced> Children => _children;

    public decimal Total() => _children.Sum(c => c.Total()) * (1m - _discountRate);
}

public static class Program
{
    public static void Main()
    {
        var starter = new Bundle("Starter kit", 0.10m)
            .Add(new Product("Keyboard", 50m))
            .Add(new Product("Mouse", 20m));

        var cart = new Bundle("Cart", 0m)
            .Add(starter)
            .Add(new Product("Monitor", 200m));

        Console.WriteLine($"{cart.Name}: {cart.Total()}"); // 263.00
    }
}
```

## Variations
- **Where child management is declared**: on the component, so every node looks the same (transparent, but adding to a leaf is meaningless and has to throw), or only on the composite (safe, since the compiler rejects it, but clients must know which nodes can have children). The example takes the safe choice and exposes `Add` only on `Bundle`.
- **Leaf with empty children**: if the component exposes `Children`, a leaf can return an empty sequence, so traversal needs no kind checks.
- **Parent references**: keep a link to the parent in each node to ease moving up or removing. Then update it only inside `Add` and `Remove`, so the link and the child list never disagree. It also blocks sharing one node in two parents.
- **Child order**: if order matters (steps in a pipeline), use a list and design the access API for it.
- **Caching**: a composite can cache a computed result (a total, a bounding size) and drop the cache when a child changes. That needs a way for children to tell the parent, hence parent links or events.
- **Storage**: a list, array, dictionary or even named fields per child, when each composite has a fixed set of children.

## Risks and C# alternatives
- Recursion depth: a very deep tree can overflow the stack. Traverse with an explicit stack or `yield return` when depth is not bounded.
- Cycles: guard against adding a node to its own descendants. The example only checks the direct self-reference; check ancestors if nodes can be reused.
- Expose children as `IEnumerable<T>` or `IReadOnlyList<T>`, never the internal `List<T>`, or callers bypass your invariants.
- For traversals that vary a lot (print, export, validate), keep the nodes small and add operations by a visitor or by plain pattern matching in a function, instead of growing the component interface.
- A one-off nested structure that never gets new operations may be simpler as plain data plus a recursive function.

## Related patterns
- [decorator.md](decorator.md): often combined with composite and shares the recursive structure, but it adds behavior to one component instead of aggregating several.
- [flyweight.md](flyweight.md): lets leaves be shared, but shared leaves cannot hold a parent reference.
- [iterator.md](../behavioral/iterator.md): traverses a composite.
- [visitor.md](../behavioral/visitor.md): keeps operations across leaf and composite classes in one place.
- [chain-of-responsibility.md](../behavioral/chain-of-responsibility.md): the parent link often serves as the chain.
- [command.md](../behavioral/command.md): a macro command is a composite of commands.

## Verification
- Client code calls `Total()` on a product, a bundle and a bundle of bundles without checking types.
- A new node kind (for example a gift card) works in existing carts without editing the client.
- Tests cover an empty group, nested groups and the rule you enforce at runtime (no self-containment).
- The internal child collection cannot be modified from outside.
