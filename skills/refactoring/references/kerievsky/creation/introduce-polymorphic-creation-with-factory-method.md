# Introduce Polymorphic Creation with Factory Method

Kerievsky (2004), ch. 6, p. 88. Pattern: Factory Method. Direction: to.

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
1. In one subclass, change the similar method so the creation happens in a separate *instantiation method* (apply Extract Function, [extract-function.md](../../fowler/first-set/extract-function.md)). Use a generic name (`CreateReport`) and return the type that all siblings can share. Compile and test.
2. Do the same in each sibling. The instantiation methods must end up with the same signature. Compile and test.
3. Modify the siblings' common superclass. If you cannot modify it or would rather not, apply Extract Superclass ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)) to put a new class between it and the siblings. The class you modify plays the Creator role in the pattern. Compile and test.
4. Apply Form Template Method ([form-template-method.md](../generalization/form-template-method.md)) to the similar method. This uses Pull Up Method ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)); in a strongly typed language, Pull Up Method's note applies: the pulled-up method calls the instantiation method, which exists in the siblings but not the superclass, so declare it as an abstract method on the superclass. That abstract method is the factory method. Each sibling is now a ConcreteCreator. Compile and test.
5. Repeat for other similar methods in the siblings that can use the same factory method.
6. If most subclasses create the same class, give the superclass method a default body creating that class, and let the others override it. Compile and test.

## Example
Before: two clients repeat the same method. Only the parser class differs.

```csharp
using System.Collections.Generic;
using System.Linq;

public interface IItemParser { IReadOnlyList<string> Parse(string body); }
public class CsvItemParser : IItemParser
{
    public IReadOnlyList<string> Parse(string body) => body.Split(',').Select(s => s.Trim()).ToList();
}
public class LineItemParser : IItemParser
{
    public IReadOnlyList<string> Parse(string body) => body.Split('\n').Select(s => s.Trim()).ToList();
}

public class CsvApiClient
{
    public IReadOnlyList<string> GetItems(string rawBody)
    {
        var body = rawBody.Trim();
        var parser = new CsvItemParser();
        return parser.Parse(body).Where(i => i.Length > 0).ToList();
    }
}
public class LineApiClient
{
    public IReadOnlyList<string> GetItems(string rawBody)
    {
        var body = rawBody.Trim();
        var parser = new LineItemParser();
        return parser.Parse(body).Where(i => i.Length > 0).ToList();
    }
}
```

After: `GetItems` exists once in `ApiClient`. It calls `CreateParser`, and each subclass decides what to build.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class ApiClient
{
    public IReadOnlyList<string> GetItems(string rawBody)
    {
        var body = rawBody.Trim();
        var parser = CreateParser();
        return parser.Parse(body).Where(i => i.Length > 0).ToList();
    }

    protected abstract IItemParser CreateParser();
}

public class CsvApiClient : ApiClient
{
    protected override IItemParser CreateParser() => new CsvItemParser();
}

public class LineApiClient : ApiClient
{
    protected override IItemParser CreateParser() => new LineItemParser();
}
```

## C# notes
- Make the factory method `protected abstract` unless callers outside the hierarchy need it. A default implementation is `protected virtual`.
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- The similar method now exists in one place, and no subclass repeats its body.
- Each subclass overrides only the creation step.
