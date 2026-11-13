# Extrair Composite (Extract Composite)

Kerievsky (2004), cap. 8, p. 214. Padrão: Composite. Direção: até.

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Várias subclasses de uma mesma hierarquia mantêm, cada uma, uma coleção de filhos vindos dessa mesma hierarquia, e cada uma repete o código que adiciona, remove e totaliza esses filhos.
- Mover esse código para uma superclasse comum reduz o tratamento duplicado de filhos, e o nome da superclasse avisa o próximo desenvolvedor que o tratamento de filhos pode ser herdado em vez de reescrito.
- Isso é Extrair Superclasse (Extract Superclass) ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)) voltado apenas para a parte de tratamento de filhos. Feito isso, se restar comportamento compartilhado que não tem nada a ver com filhos, continue com Extrair Superclasse.

## Mecânica
1. Crie o composite: uma nova classe na hierarquia, com nome que diga o que ela contém (por exemplo `CompositeItem`). Compile.
2. Torne cada classe que mantém código duplicado de filhos (um contêiner de filhos) subclasse do composite. Compile.
3. Pegue um método de processamento de filhos que esteja duplicado, total ou parcialmente, entre os contêineres.
   - Se o nome dele difere entre os contêineres, uniformize-o com Mudar Declaração de Função (Change Function Declaration) ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)).
   - Totalmente duplicado: mova o campo de filhos que ele usa para o composite com Subir Campo (Pull Up Field) ([pull-up-field.md](../../fowler/inheritance/pull-up-field.md)), renomeando-o se o nome antigo servir a apenas um contêiner. Depois mova o método com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). Se ele depender de código do construtor nos contêineres, suba esse código para o construtor do composite com Subir Corpo do Construtor (Pull Up Constructor Body) ([pull-up-constructor-body.md](../../fowler/inheritance/pull-up-constructor-body.md)).
   - Parcialmente duplicado: primeiro tente tornar os corpos idênticos com Substituir Algoritmo (Substitute Algorithm) ([substitute-algorithm.md](../../fowler/encapsulation/substitute-algorithm.md)) e trate o método como totalmente duplicado. Caso contrário, extraia a parte comum com Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) e suba-a. Se o método tem os mesmos passos com implementações diferentes, use Formar Template Method (Form Template Method) ([form-template-method.md](form-template-method.md)).
   Compile e teste após cada passo.
4. Repita o passo 3 para cada outro método duplicado de processamento de filhos.
5. Verifique cada cliente de um contêiner: se ele puder falar com o contêiner pelo tipo do composite, troque para isso. Compile e teste.

## Exemplo
Antes: `SystemPrompt` e `FewShotBlock` mantêm, cada um, a sua própria lista de partes filhas, com o mesmo `Add` e um `Render` quase idêntico.

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

Depois: `CompositePart` é dona dos filhos, do `Add` e da junção. Cada contêiner acrescenta apenas o seu próprio cabeçalho.

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

## Notas (C#)
- Exponha os filhos como `IReadOnlyList<PromptPart>` se subclasses ou clientes precisarem lê-los; mantenha a própria lista privada, como em Encapsular Coleção ([encapsulate-collection.md](../../fowler/encapsulation/encapsulate-collection.md)).
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os totais de contêineres aninhados (um bloco few-shot dentro de um prompt de sistema) batem com os resultados antigos, e nenhum contêiner ainda declara seu próprio campo de filhos.
