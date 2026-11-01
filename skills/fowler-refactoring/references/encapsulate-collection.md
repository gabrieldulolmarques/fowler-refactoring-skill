# Encapsulate Collection

Fowler (2018), ch. 7, p. 170. Formerly / aka: —. Inverse: —.

## When to use
Smell: none specific in the book (related: Mutable Data). The motivation is encapsulating
mutable data, so the collection cannot be changed from anywhere.

- A class has a property that returns its internal collection, so any caller can add, remove
  or reorder items and the owner never finds out.
- The owner has rules about membership (limits, totals, validation, change notifications)
  that callers can bypass today.
- A setter lets callers replace the whole collection, and they keep a reference to it.

A property over the field guards who owns the list, not who edits it.

Avoid hiding collections entirely (`CountOfLines`, `LineAt(i)`): callers lose LINQ. Return a
safe collection, and pick one protection (copy or read-only view) for every getter.

## Mechanics
1. If the field is not yet behind a property or accessor, apply Encapsulate Variable first
   ([encapsulate-variable.md](encapsulate-variable.md)).
2. Add methods on the owner to add and remove single items. Decide what removal of a missing
   item does (ignore it, throw, or let the caller choose) and write that down in the method.
3. If there is a setter for the whole collection, remove it when possible
   ([remove-setting-method.md](remove-setting-method.md)). If it must stay, make it copy the incoming collection
   into the field instead of keeping the caller's reference.
4. Build and run the tests.
5. Find every use of the collection property. Change each call that modifies it (`Add`,
   `Remove`, `Clear`, indexer assignment, `Sort` in place) to use the new methods. Test after
   each change.
6. Search for any remaining `Add`/`Remove` on the getter, then change it to return a
   protected view: a copy, or a read-only wrapper. With a copy, a stray write is lost
   silently, which is why the search comes first.
7. Run the tests. Anything that still tried to modify the collection now fails to compile
   or fails loudly.

## Example
Before:

```csharp
public class OrderLine
{
    public OrderLine(string sku, int quantity) { Sku = sku; Quantity = quantity; }
    public string Sku { get; }
    public int Quantity { get; }
}

public class Order
{
    public List<OrderLine> Lines { get; set; } = new();
}

// callers
order.Lines.Add(new OrderLine("A-1", 2));
order.Lines = LoadLines(id);
var total = order.Lines.Sum(l => l.Quantity);
```

After:

```csharp
public class Order
{
    private readonly List<OrderLine> _lines = new();

    public IReadOnlyList<OrderLine> Lines => _lines.ToArray();

    public void AddLine(OrderLine line) => _lines.Add(line);

    public void RemoveLine(OrderLine line)
    {
        if (!_lines.Remove(line))
            throw new InvalidOperationException("The order does not contain this line.");
    }

    public void ReplaceLines(IEnumerable<OrderLine> lines)
    {
        var copy = lines.ToList();
        _lines.Clear();
        _lines.AddRange(copy);
    }
}

// callers (usings and LoadLines omitted, as in Before)
order.AddLine(new OrderLine("A-1", 2));
order.ReplaceLines(LoadLines(id)); // the setter is gone
var total = order.Lines.Sum(l => l.Quantity);
```

Reads keep working with LINQ. Writes now go through `Order`, so a rule such as "no more than
50 lines" has one place to live.

## C# notes
- Expose `IReadOnlyList<T>` or `IReadOnlyCollection<T>`, with `Add`/`Remove` methods on the
  owner.
- A read-only interface does not stop a caller from casting back to `List<T>` and modifying
  it. Where that matters, return a copy (`ToArray()`, `ToList()`) or a wrapper such as
  `AsReadOnly()`.
- A copy is a snapshot: later changes to the owner are not visible in it. A wrapper is a live
  view. Pick one and be consistent. For large collections that are read often, a wrapper
  avoids the copy cost.
- Mutating operations on a collection you do not own can still bite: `List<T>.Sort()` and
  `Reverse()` change the list in place, so copy first when sorting what a getter returned.

## Verification
- Compiles and the tests pass after every step; commit after each green step.
- No caller modifies the collection except through the owner's methods.
