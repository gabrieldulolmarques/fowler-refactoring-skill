# Encapsulate Composite with Builder

Kerievsky (2004), ch. 6, p. 96. Pattern: Builder. Direction: to (Builder); away (Composite).

## When to use
Smells: Primitive Obsession, Duplicated Code.

- Building a Composite takes the same three steps every time: create a node, set it up, attach it to the right parent. Skipping the last step, or attaching to the wrong parent, is an easy mistake, and the code is repetitive.
- Client code is tied to the Composite's classes. When the underlying tree library changes, every place that builds a tree has to change. A Builder that takes simple arguments (strings, numbers) and returns nothing of the library's types hides it. You can later write another Builder with the same interface for a different representation.
- The pattern's original intent is to let one construction process make different representations. Simplifying construction and decoupling the client are equally good reasons.
- Liability: a Builder's interface is sometimes not obvious, because it hides a lot of work (current position, parent tracking). Its tests or documentation may be the best way to learn it.
- Related: the Composite itself can come from [replace-implicit-tree-with-composite.md](../simplification/replace-implicit-tree-with-composite.md). The "away from Composite" direction means clients stop touching the Composite directly.

## Mechanics
There is no single set of mechanics: Builders for Composites can be designed in many ways. These are the general steps. The book suggests building the Builder test-first.
1. Create the builder class. Make it able to produce a one-node Composite and add a method to get the result. Compile and test.
2. Make it able to build children. This usually means a few methods to create a node and position it (add a child of the current node, add a sibling, go back up). Compile and test.
3. If the code you are replacing sets attributes or values on nodes, let the builder set them too. Compile and test.
4. Look at how simple it is to use, and simplify it.
5. Change the Composite-building code to use the builder. The client becomes the Director in the pattern. Compile and test.

## Example
Before: a route tree built by hand. Each node is created, added to its parent, and the current parent is tracked in local variables.

```csharp
using System.Collections.Generic;
using System.Linq;

public class RouteNode
{
    public string Segment { get; }
    public List<RouteNode> Children { get; } = new();
    public RouteNode(string segment) { Segment = segment; }

    public string Render(int depth = 0) =>
        new string(' ', depth * 2) + Segment + "\n" + string.Concat(Children.Select(c => c.Render(depth + 1)));
}

public static class Caller
{
    public static string BuildText()
    {
        var root = new RouteNode("api");
        var v1 = new RouteNode("v1");
        root.Children.Add(v1);
        var users = new RouteNode("users");
        v1.Children.Add(users);
        var orders = new RouteNode("orders");
        v1.Children.Add(orders);
        var health = new RouteNode("health");
        root.Children.Add(health);
        return root.Render();
    }
}
```

After: `RouteBuilder` keeps the path from the root to the current node. Clients pass segment names only and read the result at the end.

```csharp
using System;
using System.Collections.Generic;

public class RouteBuilder
{
    private readonly RouteNode _root;
    private readonly Stack<RouteNode> _path = new();

    public RouteBuilder(string rootSegment)
    {
        _root = new RouteNode(rootSegment);
        _path.Push(_root);
    }

    public RouteBuilder AddChild(string segment)
    {
        var node = new RouteNode(segment);
        _path.Peek().Children.Add(node);
        _path.Push(node);
        return this;
    }

    public RouteBuilder AddSibling(string segment)
    {
        Up();
        return AddChild(segment);
    }

    public RouteBuilder Up()
    {
        if (_path.Count == 1) throw new InvalidOperationException("Already at the root.");
        _path.Pop();
        return this;
    }

    public RouteNode Build() => _root;
}

public static class Caller
{
    public static string BuildText() =>
        new RouteBuilder("api")
            .AddChild("v1")
            .AddChild("users")
            .AddSibling("orders")
            .Up()
            .AddSibling("health")
            .Build()
            .Render();
}
```

The tree is the same. `AddSibling("orders")` goes up from `users` and adds under `v1`. The next `Up` leaves `orders` for `v1`, and `AddSibling("health")` goes up once more and adds under `api`.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The builder's output equals the old hand-built tree for the same input (compare the rendered or serialized form).
- No client code outside the builder references the Composite's node constructor or its child collection.
