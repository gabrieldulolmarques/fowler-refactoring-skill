# Extract Composite

Kerievsky (2004), ch. 8, p. 214. Pattern: Composite. Direction: to.

## When to use
Smells: Duplicated Code.

- Several subclasses in one hierarchy each keep a collection of children from that same hierarchy, and each repeats the code that adds, removes and totals them.
- Moving that code into one superclass cuts the duplicated child handling, and the superclass name tells the next developer that child handling can be inherited instead of rewritten.
- This is Extract Superclass ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)) aimed only at the child-handling part. Once it is done, if more shared behavior remains that has nothing to do with children, continue with Extract Superclass.

## Mechanics
1. Create the composite: a new class in the hierarchy, named for what it contains (for example `CompositeItem`). Compile.
2. Make each class that holds duplicated child-handling code (a child container) a subclass of the composite. Compile.
3. Take one child-processing method that is duplicated, fully or partially, across the containers.
   - If its name differs between containers, make it consistent with Change Function Declaration ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)).
   - Fully duplicated: move the children field it uses to the composite with Pull Up Field ([pull-up-field.md](../../fowler/inheritance/pull-up-field.md)), renaming it if the old name fits only one container, then move the method with Pull Up Method ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). If it depends on constructor code in the containers, pull that up into the composite's constructor ([pull-up-constructor-body.md](../../fowler/inheritance/pull-up-constructor-body.md)).
   - Partially duplicated: first try to make the bodies identical with Substitute Algorithm ([substitute-algorithm.md](../../fowler/encapsulation/substitute-algorithm.md)) and treat it as fully duplicated. Otherwise extract the common part with Extract Function ([extract-function.md](../../fowler/first-set/extract-function.md)) and pull it up. If the method has the same steps with different implementations, use Form Template Method ([form-template-method.md](form-template-method.md)).
   Compile and test after each step.
4. Repeat step 3 for every other duplicated child-processing method.
5. Check each client of a container: if it can talk to the container through the composite type, change it to do so. Compile and test.

## Example
Before: `SystemPrompt` and `FewShotBlock` each keep their own list of child parts, with the same `Add` and a near-identical `Render`.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class PromptPart
{
    public abstract string Render();
}

public class TextPart : PromptPart
{
    private readonly string _text;
    public TextPart(string text) => _text = text;
    public override string Render() => _text;
}

public class SystemPrompt : PromptPart
{
    private readonly List<PromptPart> _parts = new();
    public void Add(PromptPart part) => _parts.Add(part);
    public override string Render() => "[system]\n" + string.Join("\n", _parts.Select(p => p.Render()));
}

public class FewShotBlock : PromptPart
{
    private readonly List<PromptPart> _examples = new();
    public void Add(PromptPart example) => _examples.Add(example);
    public override string Render() => "Examples:\n" + string.Join("\n", _examples.Select(e => e.Render()));
}
```

After: `CompositePart` owns the children, `Add` and the joining. Each container adds only its own heading.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class PromptPart
{
    public abstract string Render();
}

public class TextPart : PromptPart
{
    private readonly string _text;
    public TextPart(string text) => _text = text;
    public override string Render() => _text;
}

public abstract class CompositePart : PromptPart
{
    private readonly List<PromptPart> _children = new();
    public void Add(PromptPart part) => _children.Add(part);
    protected string RenderChildren() => string.Join("\n", _children.Select(c => c.Render()));
}

public class SystemPrompt : CompositePart
{
    public override string Render() => "[system]\n" + RenderChildren();
}

public class FewShotBlock : CompositePart
{
    public override string Render() => "Examples:\n" + RenderChildren();
}
```

## C# notes
- Expose the children as `IReadOnlyList<PromptPart>` if subclasses or clients need to read them; keep the list itself private ([encapsulate-collection.md](../../fowler/encapsulation/encapsulate-collection.md)).
## Verification
- Compiles and the tests pass after every step; one commit per refactoring.
- Totals for nested containers (a few-shot block inside a system prompt) match the old results, and no container still declares its own children field.
