# Push Down Field

Fowler (2018), ch. 12, p. 361. Formerly / aka: —. Inverse: Pull Up Field ([pull-up-field.md](pull-up-field.md)).

## When to use
Smell: Refused Bequest. A field sits in a superclass but only one subclass, or a small share of them, uses it. The other subclasses carry state they never touch, and a reader of the base class is misled about what every instance has.

Not worth it when most subclasses use the field, or when code that works through the base type reads it. In that case the field belongs in the base class (see [pull-up-field.md](pull-up-field.md)).

## Mechanics
1. Confirm which subclasses use the field.
2. Search every usage of the field, and check that no code reaches it through the superclass type. Include reflection and serialization that may name it: a field persisted or serialized under its name must keep that name in the subclass, or the mapping must be updated.
3. Declare the field in every subclass that needs it.
4. Remove the field from the superclass.
5. Compile and run the tests. Any error shows code that still reads the field through the base type: deal with it before going on.
6. Remove the field from any subclass that declared it but does not use it.
7. Compile and run the tests.

## Example
Before: `SubtitleLanguage` is declared in the base class, but only `Video` uses it.

```csharp
public abstract class MediaItem
{
    public string Title { get; set; } = "";
    protected string SubtitleLanguage = "";
}

public class Song : MediaItem { }

public class Video : MediaItem
{
    public string Label() => $"{Title} [{SubtitleLanguage}]";
    public void SetSubtitles(string language) => SubtitleLanguage = language;
}
```

After: the field lives only where it is used.

```csharp
public abstract class MediaItem
{
    public string Title { get; set; } = "";
}

public class Song : MediaItem { }

public class Video : MediaItem
{
    private string _subtitleLanguage = "";
    public string Label() => $"{Title} [{_subtitleLanguage}]";
    public void SetSubtitles(string language) => _subtitleLanguage = language;
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
