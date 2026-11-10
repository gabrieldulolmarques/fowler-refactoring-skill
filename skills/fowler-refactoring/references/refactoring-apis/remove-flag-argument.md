# Remove Flag Argument

Fowler (2018), ch. 11, p. 314. Formerly / aka: formerly Replace Parameter with Explicit Methods. Inverse: —.

## When to use
Smells: Long Parameter List.

A flag argument is a parameter the caller sets to a literal (`true`, an enum member, a string) only to tell the method which branch to run. The call site then says nothing about what the value means, and the list of methods does not show which variations exist.

It is a flag argument only when both hold:
- the caller passes a constant that merely picks a branch, not a value that originates elsewhere in the program;
- the method uses the parameter only to choose a path, not to pass along or store.

Do not change callers that pass computed values. If some callers pass literals and others pass data, add the explicit methods, migrate only the literal callers, and keep the original method for the data callers.

With several independent flags, one method per combination is impractical, so keeping the flags can be reasonable. Treat them as a prompt to split the method into smaller composable ones.

## Mechanics
1. Create one explicit method per value of the parameter, named for what that value means.
   - If the original method already dispatches on the parameter at its outermost level, apply [decompose-conditional.md](../conditional-logic/decompose-conditional.md): each branch becomes the body of an explicit method, and the original just calls them.
   - If the parameter is tangled through the body, make each explicit method a thin wrapper that calls the original with a fixed value.
2. Compile and test.
3. Replace each caller that passes a literal with a call to the matching explicit method. Compile and test after each caller (or small group).
4. When no caller uses the parameter any more, delete the original method. If it stays as a wrapper target, reduce its visibility or rename it so it signals "internal" (for example a `Core` or `Impl` suffix).
5. Compile and test.

## Example
Before:

```csharp
using System.IO;
using System.IO.Compression;
using System.Text;

public record Report(string Title, string Body);

public static class Exporter
{
    public static byte[] Export(Report report, bool compressed)
    {
        var raw = Encoding.UTF8.GetBytes(report.Title + "\n" + report.Body);
        if (!compressed) return raw;

        using var output = new MemoryStream();
        using (var gzip = new GZipStream(output, CompressionLevel.Optimal))
        {
            gzip.Write(raw);
        }
        return output.ToArray();
    }
}
```

Callers (a separate fragment, for example top-level statements in another file):

```csharp
var report = new Report("Q3", "Totals...");
var plain = Exporter.Export(report, false);
var packed = Exporter.Export(report, true);
```

After:

```csharp
public static class Exporter
{
    public static byte[] ExportPlain(Report report)
    {
        return Encoding.UTF8.GetBytes(report.Title + "\n" + report.Body);
    }

    public static byte[] ExportCompressed(Report report)
    {
        var raw = ExportPlain(report);
        using var output = new MemoryStream();
        using (var gzip = new GZipStream(output, CompressionLevel.Optimal))
        {
            gzip.Write(raw);
        }
        return output.ToArray();
    }
}
```

Callers:

```csharp
var report = new Report("Q3", "Totals...");
var plain = Exporter.ExportPlain(report);
var packed = Exporter.ExportCompressed(report);
```

When the flag is used in several places in the body, keep the original and add wrappers instead. In the end state below, the original `Export` has been renamed to `ExportCore` and made private, which is possible once no literal caller uses it:

```csharp
public static byte[] ExportPlain(Report report) => ExportCore(report, compressed: false);
public static byte[] ExportCompressed(Report report) => ExportCore(report, compressed: true);

private static byte[] ExportCore(Report report, bool compressed)
{
    var title = compressed ? report.Title.ToUpperInvariant() : report.Title;
    var raw = Encoding.UTF8.GetBytes(title + "\n" + report.Body);
    if (!compressed) return raw;

    using var output = new MemoryStream();
    using (var gzip = new GZipStream(output, CompressionLevel.Optimal))
    {
        gzip.Write(raw);
    }
    return output.ToArray();
}
```

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Every literal caller now reads as the explicit method, and behavior for each value is unchanged.
