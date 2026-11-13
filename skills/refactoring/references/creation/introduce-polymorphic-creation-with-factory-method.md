# Introduce Polymorphic Creation with Factory Method

Kerievsky (2004), ch. 6, p. 88. Direction: to. Pattern: Factory Method (GoF, p. 107).

## When to use
Smells: Duplicated Code.

- Classes in a hierarchy implement a method almost identically, and the only difference is which class they instantiate. The rest of the method is the same.
- A Factory Method needs three things: a type (interface or base class) for what gets created, the classes that implement that type, and several classes that each decide locally which one to create.
- It is usually found where a Template Method calls a Factory Method for its one varying step. Removing duplicated methods in a hierarchy often ends up in this combination.
- Frameworks use it the same way: they declare a creation method and let your subclass override it to plug in your own object.
- Costs: the signature is shared by all implementers, so some of them may receive parameters they do not need. The pattern is harder to set up than `new`, but the code that uses it is shorter than the duplicated methods it replaces.
- Compare [replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md): a plain Creation Method is not polymorphic, a Factory Method is.

## Mechanics
This covers the case of sibling subclasses with a *similar method*. A superclass and one subclass is the same with fewer steps.
1. In one subclass, change the similar method so the creation happens in a separate *instantiation method* (apply Extract Function, [extract-function.md](../first-set/extract-function.md)). Use a generic name (`CreateReport`) and return the type that all siblings can share. Compile and test.
2. Do the same in each sibling. The instantiation methods must end up with the same signature. Compile and test.
3. Make sure the siblings have a common superclass you can change. If not, apply Extract Superclass ([extract-superclass.md](../inheritance/extract-superclass.md)). This class plays the Creator role in the pattern. Compile and test.
4. Apply Form Template Method ([form-template-method.md](../generalization/form-template-method.md)) to the similar method. This uses Pull Up Method ([pull-up-method.md](../inheritance/pull-up-method.md)), and the instantiation method becomes an abstract method on the superclass: that is the factory method. Each sibling is now a ConcreteCreator. Compile and test.
5. Repeat for other similar methods in the siblings that can use the same factory method.
6. If most subclasses create the same class, give the superclass method a default body creating that class, and let the others override it. Compile and test.

## Example
Before: two exporters repeat the same method. Only the report class differs.

```csharp
public interface IReport { string Render(); }
public class TextReport : IReport
{
    private readonly string _text;
    public TextReport(string text) { _text = text; }
    public string Render() => _text;
}
public class HtmlReport : IReport
{
    private readonly string _text;
    public HtmlReport(string text) { _text = text; }
    public string Render() => "<p>" + _text + "</p>";
}

public class TextExporter
{
    public string Export(IEnumerable<string> lines)
    {
        var body = string.Join("\n", lines.Select(l => l.Trim()));
        var report = new TextReport(body);
        return "== Report ==\n" + report.Render();
    }
}
public class HtmlExporter
{
    public string Export(IEnumerable<string> lines)
    {
        var body = string.Join("\n", lines.Select(l => l.Trim()));
        var report = new HtmlReport(body);
        return "== Report ==\n" + report.Render();
    }
}
```

After: `Export` exists once in `Exporter`. It calls `CreateReport`, and each subclass decides what to build.

```csharp
public abstract class Exporter
{
    public string Export(IEnumerable<string> lines)
    {
        var body = string.Join("\n", lines.Select(l => l.Trim()));
        var report = CreateReport(body);
        return "== Report ==\n" + report.Render();
    }

    protected abstract IReport CreateReport(string body);
}

public class TextExporter : Exporter
{
    protected override IReport CreateReport(string body) => new TextReport(body);
}

public class HtmlExporter : Exporter
{
    protected override IReport CreateReport(string body) => new HtmlReport(body);
}
```

## C# notes
- Make the factory method `protected abstract` unless callers outside the hierarchy need it. A default implementation is `protected virtual`.
- If the variation is only a choice of class, a constructor passed as `Func<string, IReport>` can replace the subclass hierarchy. Use the factory method when the hierarchy already exists for other reasons.

## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The similar method now exists in one place, and no subclass repeats its body.
- Each subclass overrides only the creation step.
