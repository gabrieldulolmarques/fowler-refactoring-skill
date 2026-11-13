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
Before: a menu tree built by hand. Each node is created, added to its parent, and the current parent is tracked in local variables.

```csharp
public class MenuItem
{
    public string Title { get; }
    public List<MenuItem> Children { get; } = new();
    public MenuItem(string title) { Title = title; }

    public string Render(int depth = 0) =>
        new string(' ', depth * 2) + Title + "\n" + string.Concat(Children.Select(c => c.Render(depth + 1)));
}

var root = new MenuItem("File");
var open = new MenuItem("Open");
root.Children.Add(open);
var recent = new MenuItem("Recent");
open.Children.Add(recent);
var exit = new MenuItem("Exit");
root.Children.Add(exit);
var text = root.Render();
```

After: `MenuBuilder` keeps the path from the root to the current node. Clients pass titles only and read the result at the end.

```csharp
public class MenuBuilder
{
    private readonly MenuItem _root;
    private readonly Stack<MenuItem> _path = new();

    public MenuBuilder(string rootTitle)
    {
        _root = new MenuItem(rootTitle);
        _path.Push(_root);
    }

    public MenuBuilder AddChild(string title)
    {
        var item = new MenuItem(title);
        _path.Peek().Children.Add(item);
        _path.Push(item);
        return this;
    }

    public MenuBuilder AddSibling(string title)
    {
        Up();
        return AddChild(title);
    }

    public MenuBuilder Up()
    {
        if (_path.Count == 1) throw new InvalidOperationException("Already at the root.");
        _path.Pop();
        return this;
    }

    public MenuItem Build() => _root;
}

var text = new MenuBuilder("File")
    .AddChild("Open")
    .AddChild("Recent")
    .Up()
    .AddSibling("Exit")
    .Build()
    .Render();
```

The tree is the same. `Up` after `Recent` goes back to `Open`, and `AddSibling("Exit")` then goes up once more and adds under `File`.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The builder's output equals the old hand-built tree for the same input (compare the rendered or serialized form).
- No client code outside the builder references the Composite's node constructor or its child collection.
