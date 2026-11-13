# Extract Composite

Kerievsky (2004), ch. 8, p. 214. Direction: to. Pattern: Composite (GoF, p. 163).

## When to use
Smells: Duplicated Code.

- Several subclasses in one hierarchy each keep a collection of children from that same hierarchy, and each repeats the code that adds, removes and totals them.
- Moving that code into one superclass cuts the duplicated child handling, and the superclass name tells the next developer that child handling can be inherited instead of rewritten.
- This is Extract Superclass ([extract-superclass.md](../inheritance/extract-superclass.md)) aimed only at the child-handling part. Once it is done, if more shared behavior remains that has nothing to do with children, continue with Extract Superclass.

## Mechanics
1. Create the composite: a new class in the hierarchy, named for what it contains (for example `CompositeItem`). Compile.
2. Make each class that holds duplicated child-handling code (a child container) a subclass of the composite. Compile.
3. Take one child-processing method that is duplicated, fully or partially, across the containers.
   - If its name differs between containers, make it consistent with Change Function Declaration ([change-function-declaration.md](../first-set/change-function-declaration.md)).
   - Fully duplicated: move the children field it uses to the composite with Pull Up Field ([pull-up-field.md](../inheritance/pull-up-field.md)), renaming it if the old name fits only one container, then move the method with Pull Up Method ([pull-up-method.md](../inheritance/pull-up-method.md)). If it depends on constructor code in the containers, pull that up into the composite's constructor ([pull-up-constructor-body.md](../inheritance/pull-up-constructor-body.md)).
   - Partially duplicated: first try to make the bodies identical with Substitute Algorithm ([substitute-algorithm.md](../encapsulation/substitute-algorithm.md)) and treat it as fully duplicated. Otherwise extract the common part with Extract Function ([extract-function.md](../first-set/extract-function.md)) and pull it up. If the method has the same steps with different implementations, use Form Template Method ([form-template-method.md](form-template-method.md)).
   Compile and test after each step.
4. Repeat step 3 for every other duplicated child-processing method.
5. Check each client of a container: if it can talk to the container through the composite type, change it to do so. Compile and test.

## Example
Before: `Box` and `Pallet` each keep their own list of child items, with the same `Add` and a near-identical `Weight`.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class Item
{
    public abstract decimal Weight();
}

public class Crate : Item
{
    private readonly decimal _weight;
    public Crate(decimal weight) => _weight = weight;
    public override decimal Weight() => _weight;
}

public class Box : Item
{
    private readonly List<Item> _items = new();
    public void Add(Item item) => _items.Add(item);
    public override decimal Weight() => 0.5m + _items.Sum(i => i.Weight());
}

public class Pallet : Item
{
    private readonly List<Item> _contents = new();
    public void Add(Item item) => _contents.Add(item);
    public override decimal Weight() => 20m + _contents.Sum(c => c.Weight());
}
```

After: `CompositeItem` owns the children, `Add` and the sum. Each container adds only its own tare weight.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class Item
{
    public abstract decimal Weight();
}

public class Crate : Item
{
    private readonly decimal _weight;
    public Crate(decimal weight) => _weight = weight;
    public override decimal Weight() => _weight;
}

public abstract class CompositeItem : Item
{
    private readonly List<Item> _children = new();
    public void Add(Item item) => _children.Add(item);
    protected decimal ChildrenWeight() => _children.Sum(c => c.Weight());
}

public class Box : CompositeItem
{
    public override decimal Weight() => 0.5m + ChildrenWeight();
}

public class Pallet : CompositeItem
{
    public override decimal Weight() => 20m + ChildrenWeight();
}
```

## C# notes
- Make the composite `abstract` when it has no meaning alone, as above. A composite that is also a valid leaf-less container can stay concrete.
- Expose the children as `IReadOnlyList<Item>` if subclasses or clients need to read them; keep the list itself private ([encapsulate-collection.md](../encapsulation/encapsulate-collection.md)).
- A cycle (a container added to itself or to one of its own descendants) makes `Weight` recurse forever. Guard `Add` if clients can build arbitrary trees.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Totals for nested containers (a box inside a pallet) match the old results, and no container still declares its own children field.
