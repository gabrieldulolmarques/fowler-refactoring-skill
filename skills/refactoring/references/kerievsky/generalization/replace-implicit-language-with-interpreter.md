# Substituir Linguagem Implícita por Interpreter (Replace Implicit Language with Interpreter)

Kerievsky (2004), cap. 8, p. 269. Padrão: Interpreter. Direção: até.

## Quando usar
Smells: Explosão Combinatória (Combinatorial Explosion), Classe Grande (Large Class), Obsessão por Primitivos (Primitive Obsession), Código Duplicado (Duplicated Code).

- Uma classe tem muitos métodos que são, na prática, combinações de algumas ideias: `ByStatus`, `ByMinTotal`, `ByStatusAndMinTotal`, `ByCustomerAndStatus`... A linguagem de "encontre pedidos que são X e Y, mas não Z" está ali, mas nunca foi escrita como tal. Cada nova combinação exige um novo método, e os métodos repetem o mesmo código de filtragem.
- Modelar a linguagem com algumas classes pequenas (os critérios, mais and/or/not) permite que os chamadores montem qualquer combinação em tempo de execução, sem código novo, e permite configurar o comportamento dinamicamente, por exemplo a partir de um formulário de busca.
- Dois padrões que se apoiam muito em Interpreter são Specification e Query Object, e esta refatoração serve à seleção de objetos desse tipo.
- Serve para gramáticas pequenas (menos de cerca de uma dúzia de classes). Para uma linguagem grande, um gerador de parsers é melhor. Para uma linguagem pequena e uniforme, código simples pode bastar.
- Há um custo inicial: definir as classes e mudar os chamadores para compô-las. Ele se paga quando a alternativa é uma lista crescente de métodos quase duplicados.

## Mecânica
Estes passos assumem seleção de objetos: vários métodos percorrem uma coleção e escolhem os objetos que casam.

1. Encontre um método de seleção que use um argumento de critério (por exemplo, um total mínimo). Crie uma classe de especificação concreta para esse critério: o construtor recebe o valor e expõe um getter. No método de seleção, crie uma instância e leia o critério pelo getter. Dê à classe o nome do que ela faz (`MinTotalSpec`). Se um método usa vários critérios, faça os passos 1 e 2 para cada um. Compile e teste se a seleção ainda funciona.
2. Aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) à condição dentro do laço, criando um método booleano `IsSatisfiedBy`, e mova-o para a especificação concreta com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)). Se ainda não existir uma superclasse de especificação, crie uma com Extrair Superclasse (Extract Superclass) ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)), abstrata, declarando apenas `IsSatisfiedBy`. Compile e teste.
3. Repita os passos 1 e 2 para os outros métodos de seleção.
4. Para um método de seleção que agora monta várias especificações concretas, crie uma especificação composta que as contenha (via construtor ou método `Add`), mova a condição combinada para o seu `IsSatisfiedBy` e faça-a estender a superclasse de especificação (veja [replace-one-many-distinctions-with-composite.md](replace-one-many-distinctions-with-composite.md) e [extract-composite.md](extract-composite.md)).
5. Todo método de seleção agora recebe uma única especificação, e os métodos são idênticos, exceto pela forma como a especificação é montada. Extraia o laço compartilhado para `SelectBy(spec)` e faça cada método de seleção chamá-lo. Compile e teste após cada passo.
6. Internalize os métodos de seleção antigos com Internalizar Função (Inline Function) ([inline-function.md](../../fowler/first-set/inline-function.md)), para que os chamadores montem a especificação e chamem `SelectBy`. Compile e teste.

## Exemplo
Antes: um localizador sobre o log de chamadas de ferramentas de um assistente, com um método por combinação.

```csharp
using System.Collections.Generic;

public enum CallStatus { Ok, Failed, TimedOut }

public class ToolCall
{
    public string Id { get; }
    public string Tool { get; }
    public CallStatus Status { get; }
    public int DurationMs { get; }
    public ToolCall(string id, string tool, CallStatus status, int durationMs)
    {
        Id = id;
        Tool = tool;
        Status = status;
        DurationMs = durationMs;
    }
}

public class ToolCallFinder
{
    private readonly List<ToolCall> _calls;
    public ToolCallFinder(List<ToolCall> calls) => _calls = calls;

    public List<ToolCall> ByStatus(CallStatus status)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.Status == status) found.Add(c);
        return found;
    }

    public List<ToolCall> ByMinDuration(int minMs)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.DurationMs >= minMs) found.Add(c);
        return found;
    }

    public List<ToolCall> ByStatusAndMinDuration(CallStatus status, int minMs)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.Status == status && c.DurationMs >= minMs) found.Add(c);
        return found;
    }

    public List<ToolCall> ByToolNotStatus(string tool, CallStatus status)
    {
        var found = new List<ToolCall>();
        foreach (var c in _calls)
            if (c.Tool == tool && c.Status != status) found.Add(c);
        return found;
    }
}
```

Depois: um pequeno conjunto de classes de especificação e um único `SelectBy`. Qualquer combinação é montada pelo chamador. `OrSpec` e `NotSpec` são acrescentadas aqui porque os chamadores precisam delas; não são um passo da mecânica.

```csharp
using System.Collections.Generic;
using System.Linq;

public enum CallStatus { Ok, Failed, TimedOut }

public class ToolCall
{
    public string Id { get; }
    public string Tool { get; }
    public CallStatus Status { get; }
    public int DurationMs { get; }
    public ToolCall(string id, string tool, CallStatus status, int durationMs)
    {
        Id = id;
        Tool = tool;
        Status = status;
        DurationMs = durationMs;
    }
}

public abstract class ToolCallSpec
{
    public abstract bool IsSatisfiedBy(ToolCall call);
}

public class StatusSpec : ToolCallSpec
{
    private readonly CallStatus _status;
    public StatusSpec(CallStatus status) => _status = status;
    public override bool IsSatisfiedBy(ToolCall c) => c.Status == _status;
}

public class MinDurationSpec : ToolCallSpec
{
    private readonly int _minMs;
    public MinDurationSpec(int minMs) => _minMs = minMs;
    public override bool IsSatisfiedBy(ToolCall c) => c.DurationMs >= _minMs;
}

public class ToolSpec : ToolCallSpec
{
    private readonly string _tool;
    public ToolSpec(string tool) => _tool = tool;
    public override bool IsSatisfiedBy(ToolCall c) => c.Tool == _tool;
}

public class AndSpec : ToolCallSpec
{
    private readonly ToolCallSpec[] _specs;
    public AndSpec(params ToolCallSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(ToolCall c) => _specs.All(s => s.IsSatisfiedBy(c));
}

public class OrSpec : ToolCallSpec
{
    private readonly ToolCallSpec[] _specs;
    public OrSpec(params ToolCallSpec[] specs) => _specs = specs;
    public override bool IsSatisfiedBy(ToolCall c) => _specs.Any(s => s.IsSatisfiedBy(c));
}

public class NotSpec : ToolCallSpec
{
    private readonly ToolCallSpec _spec;
    public NotSpec(ToolCallSpec spec) => _spec = spec;
    public override bool IsSatisfiedBy(ToolCall c) => !_spec.IsSatisfiedBy(c);
}

public class ToolCallFinder
{
    private readonly List<ToolCall> _calls;
    public ToolCallFinder(List<ToolCall> calls) => _calls = calls;

    public List<ToolCall> SelectBy(ToolCallSpec spec) => _calls.Where(spec.IsSatisfiedBy).ToList();
}

// O antigo ByToolNotStatus(t, s) agora é:
//   finder.SelectBy(new AndSpec(new ToolSpec(t), new NotSpec(new StatusSpec(s))));
```

## Notas (C#)
- Em C#, um `Func<ToolCall, bool>` (e combinadores sobre ele) ou o `Where` do LINQ costumam bastar para filtragem em memória. Classes se justificam quando os critérios precisam ser inspecionados, impressos, serializados ou traduzidos (por exemplo, para SQL).
- Se o alvo é um banco de dados, `Expression<Func<T, bool>>` permite que o provedor traduza os critérios; criar as suas próprias classes de especificação duplicaria o que o provedor já faz.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Para cada método antigo do localizador, um teste monta a especificação equivalente e confirma que ela retorna as mesmas chamadas, na mesma ordem, antes de o método antigo ser internalizado.
