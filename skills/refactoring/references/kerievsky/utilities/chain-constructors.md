# Chain Constructors

Kerievsky (2004), ch. 11, p. 340. Pattern: —. Direction: —.

## When to use
Smells: Duplicated Code.

- Two or more constructors repeat the same assignments. When someone adds a field and updates only one constructor, the others silently leave it unset.
- Let the more specific constructors call a more general one, until you reach a catch-all constructor that handles every case. It usually takes the most parameters.
- If a class has so many constructors that it is hard to use, consider [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md), which itself relies on this refactoring.

## Mechanics
1. Find two constructors with duplicate code, and check whether one can call the other so the duplicated lines can be deleted from the caller. Make it call it. Compile and test.
2. Repeat for every constructor in the class, including those already changed, until duplication is as low as possible.
3. Re-check callers and reduce the visibility of any constructor that no longer needs to be public. Compile and test.

## Example
Before: three constructors each assign the fields themselves, and two repeat the same default retention date.

```csharp
using System;

public enum StorageTier { Hot, Cool, Archive }

public class UploadRequest
{
    private readonly string _path;
    private readonly string _contentType;
    private readonly StorageTier _tier;
    private readonly DateTime _retainUntil;
    private readonly string? _notifyUrl;

    public UploadRequest(string path)
    {
        _path = path;
        _contentType = "application/octet-stream";
        _tier = StorageTier.Hot;
        _retainUntil = DateTime.UtcNow.AddDays(30);
    }

    public UploadRequest(string path, string contentType)
    {
        _path = path;
        _contentType = contentType;
        _tier = StorageTier.Hot;
        _retainUntil = DateTime.UtcNow.AddDays(30);
    }

    public UploadRequest(string path, string contentType, StorageTier tier, DateTime retainUntil, string? notifyUrl)
    {
        _path = path;
        _contentType = contentType;
        _tier = tier;
        _retainUntil = retainUntil;
        _notifyUrl = notifyUrl;
    }
}
```

After: only the last constructor assigns fields; each of the others calls a more general one, passing defaults.

```csharp
public class UploadRequest
{
    private readonly string _path;
    private readonly string _contentType;
    private readonly StorageTier _tier;
    private readonly DateTime _retainUntil;
    private readonly string? _notifyUrl;

    public UploadRequest(string path)
        : this(path, "application/octet-stream")
    {
    }

    public UploadRequest(string path, string contentType)
        : this(path, contentType, StorageTier.Hot, DateTime.UtcNow.AddDays(30), null)
    {
    }

    public UploadRequest(string path, string contentType, StorageTier tier, DateTime retainUntil, string? notifyUrl)
    {
        _path = path;
        _contentType = contentType;
        _tier = tier;
        _retainUntil = retainUntil;
        _notifyUrl = notifyUrl;
    }
}
```

## C# notes
- C# chains with `: this(...)` before the constructor body, and `: base(...)` for the superclass. The chained call runs first, so a default expression cannot use instance members.
- Optional parameters are often the simpler alternative: one constructor, `UploadRequest(string path, string contentType = "application/octet-stream", StorageTier tier = StorageTier.Hot, DateTime? retainUntil = null, string? notifyUrl = null)`, with `retainUntil ?? ...` inside. Use chaining instead when a default is computed, when two defaults must change together, or when the signature is part of a public API (adding an optional parameter changes call sites in other assemblies only after they recompile, while overloads stay binary compatible).
- On C# 12 and later, a class with a primary constructor makes the other constructors call `this(...)` on it by rule.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every field is assigned in exactly one constructor, and each public constructor produces the same object as before for the same arguments.
