# Iterator

Gamma et al. (1995), ch. 5, p. 257. Also known as: Cursor. Category: object behavioral.

## Intent
Give sequential access to the elements of a collection without exposing how it is stored.

## When it pays off
- Clients need to read the contents of an aggregate without knowing its internal representation.
- You need several traversals at once over the same aggregate, or several traversal orders (filtered, reversed, depth-first).
- You want one way to walk different kinds of aggregates.
- Benefits: traversal variants are easy to add by swapping the iterator, the aggregate interface stays small, and each iterator holds its own position so traversals do not interfere.
- Not worth it for a plain list or array where `foreach` already does the job. Write a custom iterator only when the data is not in memory (pages, streams) or the order is not the storage order.

## Participants in C#
- **Iterator** (`IEnumerator<T>`): interface for accessing and advancing through elements. Built into .NET.
- **ConcreteIterator** (`StoredFileEnumerator` or a method with `yield return`): keeps the current position.
- **Aggregate** (`IEnumerable<T>`): interface that creates an iterator through `GetEnumerator`.
- **ConcreteAggregate** (`FileListing`): returns the proper iterator.

## Example (C#)
A cloud-storage client lists files in pages. The caller wants one plain sequence and does not care about page tokens. `yield return` makes the compiler write the iterator, and the next page is fetched only when the caller needs it.

```csharp
using System;
using System.Collections;
using System.Collections.Generic;

public class FilePage
{
    public FilePage(IReadOnlyList<string> names, string? nextToken)
    {
        Names = names;
        NextToken = nextToken;
    }

    public IReadOnlyList<string> Names { get; }
    public string? NextToken { get; }
}

public interface IStorageApi
{
    FilePage ListPage(string? pageToken);
}

public class FileListing : IEnumerable<string>
{
    private readonly IStorageApi _api;

    public FileListing(IStorageApi api) => _api = api;

    public IEnumerator<string> GetEnumerator()
    {
        string? token = null;
        do
        {
            FilePage page = _api.ListPage(token);   // fetched lazily
            foreach (string name in page.Names)
                yield return name;
            token = page.NextToken;
        } while (token != null);
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    // Another traversal over the same aggregate, as its own iterator.
    public IEnumerable<string> WithExtension(string extension)
    {
        foreach (string name in this)
            if (name.EndsWith(extension, StringComparison.OrdinalIgnoreCase))
                yield return name;
    }
}

public class FakeStorageApi : IStorageApi
{
    private readonly string[][] _pages =
    {
        new[] { "a.txt", "b.png" },
        new[] { "c.txt" },
    };

    public FilePage ListPage(string? pageToken)
    {
        int index = pageToken == null ? 0 : int.Parse(pageToken);
        bool hasNext = index + 1 < _pages.Length;
        return new FilePage(_pages[index], hasNext ? (index + 1).ToString() : null);
    }
}

public static class Program
{
    public static void Main()
    {
        var files = new FileListing(new FakeStorageApi());

        foreach (string name in files.WithExtension(".txt"))
            Console.WriteLine(name);

        // Two independent traversals at once: each enumerator has its own state.
        using var first = files.GetEnumerator();
        using var second = files.GetEnumerator();
        first.MoveNext();
        first.MoveNext();
        second.MoveNext();
        Console.WriteLine($"{first.Current} {second.Current}"); // b.png a.txt
    }
}
```

## Variations
- **Who controls the loop.** An external iterator (the client calls `MoveNext`) is flexible: you can walk two collections in step or stop early. An internal iterator (the collection calls your delegate for each element, like `List<T>.ForEach`) is shorter to use but cannot be paused or paired.
- **Who owns the traversal algorithm.** The iterator can contain it, which makes algorithms reusable across aggregates but may need access to the aggregate's internals. Or the aggregate can own it and hand out a cursor that only marks a position. A cursor is a lightweight snapshot of position, close to a memento ([memento.md](memento.md)).
- **Robustness.** Changing a collection during a traversal can skip or repeat elements. .NET collections throw `InvalidOperationException` on modification. The alternatives are to traverse a copy or to design the aggregate so that it adjusts live iterators.
- **Extra operations.** Besides the minimum (`MoveNext`, `Current`) an iterator may offer `Reset`, `Previous`, skip or peek, if a use needs them.
- **Composite structures.** Walking a tree through an external iterator needs a stack of positions. A recursive `yield return` method, or a cursor over node links, are the usual ways. Preorder, postorder and breadth-first can each be a separate method.
- **Null iterator.** An always-empty iterator (`Enumerable.Empty<T>()`) removes special cases for leaves.

## Risks and C# alternatives
- In C#, prefer `IEnumerable<T>` with `yield return` to a hand-written enumerator class. The compiler generates the state machine.
- `yield` defers execution: a bug or an exception in the source shows up at enumeration, not at the call. Validate arguments in an outer non-iterator method when this matters.
- Enumerating twice runs the source twice (two network calls above). Materialize with `ToList()` when you need several passes.
- `IEnumerator<T>` is `IDisposable`. `foreach` and `using` dispose it. A hand-driven enumerator must be disposed, especially if it holds a connection.
- For asynchronous sources, `IAsyncEnumerable<T>` with `await foreach` fits paged APIs better than blocking calls.
- LINQ is a library of iterators. Check whether a query already does the traversal you plan to write.

## Related patterns
- [Composite](../structural/composite.md): iterators are often applied to recursive structures like composites.
- [Factory Method](../creational/factory-method.md): polymorphic iterators rely on a factory method (`GetEnumerator`) to create the right one.
- [Memento](memento.md): an iterator can capture its position as a memento.

## Verification
- The consumer enumerates with `foreach` and never touches the storage details (page tokens, indexes).
- Two enumerations over the same aggregate do not disturb each other.
- An empty aggregate and a single-element aggregate both work.
- Work is lazy: stopping early (`First`, `break`) does not read the rest.
