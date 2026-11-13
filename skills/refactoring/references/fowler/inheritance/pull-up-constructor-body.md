# Pull Up Constructor Body

Fowler (2018), ch. 12, p. 355. Formerly / aka: —. Inverse: —.

## When to use
Smell: none specific in the book (related: Duplicated Code). Two or more subclasses assign the same fields, or
run the same setup, at the start of their constructors. A constructor cannot be treated
like a regular method: the superclass part must be initialized first and the subclass
constructor calls it explicitly, so the usual "extract, then Pull Up Method" route does not
work directly for the shared initialization. Pull the code into a superclass constructor and
pass what it needs through the call.

If part of the shared code needs values that only the subclass has set by then, it cannot be
hoisted into the base constructor. Handle that part separately, as in step 4. If the whole
thing gets messy, consider Replace Constructor with Factory Function
([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)).

## Mechanics
1. Make sure the superclass has a constructor (create one if needed) and that every subclass
   constructor calls it.
2. In each subclass constructor, use Slide Statements ([slide-statements.md](../moving-features/slide-statements.md)) to reorder
   the shared assignments so they sit immediately after the base call. Test.
3. Move the shared statements into the superclass constructor, delete them from each subclass,
   add a superclass constructor parameter for every value the moved code uses, and pass those
   values from each subclass call. These edits only compile together, so test once at the end.
4. If some common code cannot go at the start (it needs state the subclass sets first),
   Extract Function on it ([extract-function.md](../first-set/extract-function.md)), then Pull Up Method
   ([pull-up-method.md](pull-up-method.md)), and call it at the end of each subclass constructor.
   If the copies differ only in values, turn those values into parameters of the extracted
   method before pulling it up (Change Function Declaration,
   [change-function-declaration.md](../first-set/change-function-declaration.md)). Test.

## Example
Before: two kinds of media item share a title and a language, each assigned in its own
constructor.

```csharp
public abstract class MediaItem
{
}

public class Track : MediaItem
{
    private readonly string _title;
    private readonly string _language;
    private readonly int _bitrateKbps;

    public Track(string title, string language, int bitrateKbps)
    {
        _bitrateKbps = bitrateKbps;
        _title = title;
        _language = language;
    }
}

public class Podcast : MediaItem
{
    private readonly string _title;
    private readonly string _language;
    private readonly int _episodeNumber;

    public Podcast(string title, string language, int episodeNumber)
    {
        _title = title;
        _language = language;
        _episodeNumber = episodeNumber;
    }
}
```

After: the shared fields and their assignments live in `MediaItem`. `Track` first slid its
assignments next to the base call, then both were moved up.

```csharp
public abstract class MediaItem
{
    protected readonly string Title;
    protected readonly string Language;

    protected MediaItem(string title, string language)
    {
        Title = title;
        Language = language;
    }
}

public class Track : MediaItem
{
    private readonly int _bitrateKbps;

    public Track(string title, string language, int bitrateKbps)
        : base(title, language)
    {
        _bitrateKbps = bitrateKbps;
    }
}

public class Podcast : MediaItem
{
    private readonly int _episodeNumber;

    public Podcast(string title, string language, int episodeNumber)
        : base(title, language)
    {
        _episodeNumber = episodeNumber;
    }
}
```

Common behavior that must run after subclass data is set is extracted into a method, pulled
up, and called as the last line of each subclass constructor. Before, each subclass ended its
constructor with a similar label-building statement:

```csharp
public abstract class MediaItem
{
    protected readonly string Title;

    protected MediaItem(string title)
    {
        Title = title;
    }
}

public class Track : MediaItem
{
    private readonly int _bitrateKbps;
    public string Label { get; private set; }

    public Track(string title, int bitrateKbps) : base(title)
    {
        _bitrateKbps = bitrateKbps;
        Label = "TRK " + Title + " " + _bitrateKbps;
    }
}

public class Podcast : MediaItem
{
    private readonly int _episodeNumber;
    public string Label { get; private set; }

    public Podcast(string title, int episodeNumber) : base(title)
    {
        _episodeNumber = episodeNumber;
        Label = "POD " + Title + " " + _episodeNumber;
    }
}
```

After: the label-building step is a method in `MediaItem` that reads a subclass-supplied
prefix and detail, and each constructor calls it once its own field is set.

```csharp
public abstract class MediaItem
{
    protected readonly string Title;
    public string Label { get; private set; } = "";

    protected MediaItem(string title)
    {
        Title = title;
    }

    protected void Finish(string prefix, object detail)
    {
        Label = prefix + " " + Title + " " + detail;
    }
}

public class Track : MediaItem
{
    private readonly int _bitrateKbps;

    public Track(string title, int bitrateKbps) : base(title)
    {
        _bitrateKbps = bitrateKbps;
        Finish("TRK", _bitrateKbps);
    }
}

public class Podcast : MediaItem
{
    private readonly int _episodeNumber;

    public Podcast(string title, int episodeNumber) : base(title)
    {
        _episodeNumber = episodeNumber;
        Finish("POD", _episodeNumber);
    }
}
```

## C# notes
- The superclass constructor is reached with `: base(...)` constructor chaining. The base
  constructor runs before the subclass body and before the subclass's own field assignments in
  the constructor body (field initializers of the subclass run even earlier).
- Do not call a `virtual` member from the base constructor to finish construction: it can run
  on a subclass whose fields are not yet set. That is why the late common code goes to a
  method each subclass calls at the end of its own constructor.
- Pulled-up fields are usually `private readonly` plus a `protected`/`public` property, or
  `protected readonly`, depending on who needs them.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The shared assignments no longer appear in any subclass constructor, each subclass passes
  the values through `: base(...)`, and the order of observable side effects during
  construction is unchanged.
