# Substituir Distinções Um/Muitos por Composite (Replace One/Many Distinctions with Composite)

Kerievsky (2004), cap. 8, p. 224. Padrão: Composite. Direção: até.

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Uma classe tem um método que processa um único objeto e um quase gêmeo que processa uma coleção deles. Os dois repetem a mesma lógica.
- Os clientes precisam passar formatos de dados diferentes conforme quantos objetos têm, então o código deles não é uniforme.
- Os resultados não se combinam bem: por exemplo, "A e B" é fácil com uma lista, mas "(A e B) ou C" exige várias chamadas e uma mescla manual dos resultados.
- Um composite permite que um único método trate um objeto, muitos objetos ou uma árvore deles, então os clientes fazem uma única chamada.
- Não use quando só a duplicação incomoda e clientes uniformes e combinações mais ricas não importam: extrair o código compartilhado pode bastar, e um Composite seria exagero. O composite também pode precisar de checagens em tempo de execução sobre o que é adicionado, já que o sistema de tipos sozinho pode não impedir filhos inválidos.

## Mecânica
Chame o método que recebe um objeto de método de um-objeto, e o que recebe uma coleção de método de muitos-objetos.

1. Crie uma classe composite cujo construtor recebe a coleção e a expõe por um getter. No método de muitos-objetos, crie uma instância dela e leia a coleção somente pelo getter. Compile e teste.
2. Aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) ao código do método de muitos-objetos que trabalha sobre a coleção, torne o novo método público e mova-o para o composite com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)). Compile e teste.
3. O método de muitos-objetos agora deve ser quase igual ao de um-objeto, exceto por montar o composite. Remova quaisquer outras diferenças. Compile e teste.
4. Reduza o método de muitos-objetos a uma linha: uma chamada ao método de um-objeto com o composite como argumento. Para isso, o composite precisa compartilhar um tipo com o que o método de um-objeto aceita: faça-o implementar a mesma interface ou classe base (extraia uma interface se não existir nenhuma; Extrair Interface (Extract Interface) só existe na 1ª ed., sem equivalente na 2ª). Compile e teste.
5. Internalize o método de muitos-objetos com Internalizar Função (Inline Function) ([inline-function.md](../../fowler/first-set/inline-function.md)). Compile e teste.
6. Aplique Encapsular Coleção (Encapsulate Collection) ([encapsulate-collection.md](../../fowler/encapsulation/encapsulate-collection.md)) ao composite: os clientes agora chamam `Add` em vez de passar uma coleção ao construtor, e o getter devolve uma visão somente leitura. Compile e teste.

## Exemplo
Antes: um verificador de moderação tem um método para uma regra e outro para muitas regras, que repetem o mesmo trabalho.

```csharp
using System.Collections.Generic;

public class ChatMessage
{
    public string Id { get; }
    public string Text { get; }
    public ChatMessage(string id, string text) { Id = id; Text = text; }
}

public class ModerationResult
{
    public bool Allowed { get; }
    public IReadOnlyList<string> Violations { get; }
    public ModerationResult(bool allowed, IReadOnlyList<string> violations)
    {
        Allowed = allowed;
        Violations = violations;
    }
}

public interface IModerationRule
{
    IReadOnlyList<string> Violations(ChatMessage message);
}

public class MaxLength : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Length <= 2000 ? new List<string>() : new List<string> { "message too long" };
}

public class NoLinks : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Contains("http") ? new List<string> { "contains a link" } : new List<string>();
}

public class ModerationChecker
{
    public ModerationResult Check(ChatMessage message, IModerationRule rule)
    {
        var violations = rule.Violations(message);
        return new ModerationResult(violations.Count == 0, violations);
    }

    public ModerationResult CheckAll(ChatMessage message, List<IModerationRule> rules)
    {
        var violations = new List<string>();
        foreach (var rule in rules)
            violations.AddRange(rule.Violations(message));
        return new ModerationResult(violations.Count == 0, violations);
    }
}
```

Depois: `AllOf` é uma regra composta. `CheckAll` deixou de existir, e os chamadores passam uma regra só, seja uma regra simples ou um grupo.

```csharp
using System.Collections.Generic;

public class ChatMessage
{
    public string Id { get; }
    public string Text { get; }
    public ChatMessage(string id, string text) { Id = id; Text = text; }
}

public class ModerationResult
{
    public bool Allowed { get; }
    public IReadOnlyList<string> Violations { get; }
    public ModerationResult(bool allowed, IReadOnlyList<string> violations)
    {
        Allowed = allowed;
        Violations = violations;
    }
}

public interface IModerationRule
{
    IReadOnlyList<string> Violations(ChatMessage message);
}

public class MaxLength : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Length <= 2000 ? new List<string>() : new List<string> { "message too long" };
}

public class NoLinks : IModerationRule
{
    public IReadOnlyList<string> Violations(ChatMessage m) =>
        m.Text.Contains("http") ? new List<string> { "contains a link" } : new List<string>();
}

public class AllOf : IModerationRule
{
    private readonly List<IModerationRule> _rules = new();
    public IReadOnlyList<IModerationRule> Rules => _rules;
    public void Add(IModerationRule rule) => _rules.Add(rule);

    public IReadOnlyList<string> Violations(ChatMessage message)
    {
        var violations = new List<string>();
        foreach (var rule in _rules)
            violations.AddRange(rule.Violations(message));
        return violations;
    }
}

public class ModerationChecker
{
    public ModerationResult Check(ChatMessage message, IModerationRule rule)
    {
        var violations = rule.Violations(message);
        return new ModerationResult(violations.Count == 0, violations);
    }
}

// Um cliente agora monta um grupo e faz uma única chamada:
//   var rules = new AllOf(); rules.Add(new MaxLength()); rules.Add(new NoLinks());
//   var result = new ModerationChecker().Check(message, rules);
```

Um composite irmão, como `AnyOf` (passa quando pelo menos um filho passa), pode ser acrescentado sem tocar em `ModerationChecker`; é o caso "(A e B) ou C" que a versão com lista não conseguia expressar em uma chamada.

## Notas (C#)
- Quando um método recebe `IEnumerable<T>` apenas para percorrer, verifique se um composite compensa: se os clientes nunca precisarem de aninhamento ou de outros combinadores, uma sobrecarga com `params`/`IEnumerable` e código compartilhado pode bastar.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As violações relatadas para um grupo são as mesmas, na mesma ordem, que `CheckAll` retornava antes, e `Check` com uma regra só não muda.
