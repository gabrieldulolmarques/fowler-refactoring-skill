# Extract Superclass

Fowler (2018), ch. 12, p. 375. Formerly / aka: —. Inverse: —.

## When to use
Smells: Large Class, Alternative Classes with Different Interfaces.

- Two or more classes carry the same fields or methods, or do the same job under different
  names, and they are conceptually kinds of one thing.
- The commonality usually shows up as the code evolves; no up-front classification of the
  domain is needed.
- There are two ways to remove the overlap: a shared base class, or a helper the classes
  delegate to (Extract Class, [extract-class.md](../encapsulation/extract-class.md)). A base class is
  usually the cheaper first attempt. If the hierarchy proves wrong, Replace Superclass with
  Delegate ([replace-superclass-with-delegate.md](replace-superclass-with-delegate.md)) moves
  the code to delegation.
- Do not use it when the classes only look alike but one is not a kind of the other.

## Mechanics
1. Add an empty base class and make each of the original classes derive from it. If the
   constructors need to chain to the base constructor, adjust their signatures with Change
   Function Declaration ([change-function-declaration.md](../first-set/change-function-declaration.md)).
2. Compile and test.
3. Move shared members into the base class, one at a time: constructor bodies with Pull Up
   Constructor Body ([pull-up-constructor-body.md](pull-up-constructor-body.md)), methods
   with Pull Up Method ([pull-up-method.md](pull-up-method.md)) and fields with Pull Up Field
   ([pull-up-field.md](pull-up-field.md)). Compile and test after each move.
4. When members do the same thing under different names, give them one name with Change
   Function Declaration, then pull them up.
5. Inspect what remains in each subclass for near-duplicates. Isolate the common part with
   Extract Function ([extract-function.md](../first-set/extract-function.md)) and pull that function up.
6. Review the callers of the original classes. Any caller that uses only the shared members
   can now depend on the base class instead.

## Example
Two classes each have a title and report a duration in minutes rounded up, but they name and
compute it differently.

Before:

```csharp
using System.Collections.Generic;
using System.Linq;

public class Episode
{
    private readonly string _title;
    private readonly List<int> _segmentSeconds;

    public Episode(string title, List<int> segmentSeconds)
    {
        _title = title;
        _segmentSeconds = segmentSeconds;
    }

    public string Title => _title;
    public int TotalSeconds => _segmentSeconds.Sum();
    public string MinutesLabel => $"{(TotalSeconds + 59) / 60} min";
}

public class Clip
{
    private readonly string _title;
    private readonly int _seconds;

    public Clip(string title, int seconds)
    {
        _title = title;
        _seconds = seconds;
    }

    public string Title => _title;
    public int Seconds => _seconds;
    public string DurationLabel => $"{(Seconds + 59) / 60} min";
}
```

Steps: add `MediaItem` as a base class of both, pull the title up through the constructor,
rename `Seconds` to `TotalSeconds` and `DurationLabel` to `MinutesLabel` in `Clip`, then pull
`MinutesLabel` up.

After:

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class MediaItem
{
    protected MediaItem(string title)
    {
        Title = title;
    }

    public string Title { get; }
    public abstract int TotalSeconds { get; }
    public string MinutesLabel => $"{(TotalSeconds + 59) / 60} min";
}

public class Episode : MediaItem
{
    private readonly List<int> _segmentSeconds;

    public Episode(string title, List<int> segmentSeconds) : base(title)
    {
        _segmentSeconds = segmentSeconds;
    }

    public override int TotalSeconds => _segmentSeconds.Sum();
}

public class Clip : MediaItem
{
    private readonly int _seconds;

    public Clip(string title, int seconds) : base(title)
    {
        _seconds = seconds;
    }

    public override int TotalSeconds => _seconds;
}
```

A playback queue that only needs titles and durations can now accept a `MediaItem`.

## C# notes
- Make the superclass `abstract` when it is not meant to be instantiated; members that
  subclasses must supply become `abstract`.
- If only the signatures are shared and there is no common state or behavior, extract an
  interface instead of a base class.
- C# has single inheritance: a class that already has a base class cannot take a second one.
  Consider the interface or delegation route in that case.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Behavior is unchanged: each original class returns the same values as before, and any
  renamed member has no remaining callers under the old name.
