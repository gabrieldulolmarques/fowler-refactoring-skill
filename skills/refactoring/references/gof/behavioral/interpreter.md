# Interpreter

Gamma et al. (1995), cap. 5, p. 243. Categoria: comportamental de classe.

## Intenção
Para uma linguagem pequena, representar sua gramática como um conjunto de classes e escrever um interpretador que avalia sentenças da linguagem, mantidas como árvores dessas classes.

## Quando compensa
- As sentenças da linguagem podem ser representadas como árvores de sintaxe abstrata.
- Um problema se repete com frequência suficiente para que expressar as instâncias como sentenças de uma linguagem pequena valha a pena (regras de correspondência, filtros, regras de preço, segmentação de feature flags).
- A gramática é simples e o desempenho não é crítico. Cada regra da gramática vira uma classe, então o padrão escala mal para gramáticas grandes.
- Benefícios: a gramática é fácil de mudar e estender, adicionando ou editando classes, e cada classe de nó é curta e parecida com as outras.
- Custos: muitas regras significam muitas classes difíceis de manter, e percorrer uma árvore não é a forma mais rápida de avaliar. Para linguagens grandes ou muito usadas, use um gerador de parsers ou compile a árvore para outra forma.
- Não vale a pena quando alguns `if` ou uma tabela de consulta cobrem os casos, ou quando já existe uma biblioteca de expressões pronta.

## Participantes em C#
- **AbstractExpression** (`IFlagRule`): interface com a operação `Evaluate` compartilhada por todos os nós.
- **TerminalExpression** (`AttributeEquals`): uma folha. Implementa o caso base da recursão.
- **NonterminalExpression** (`AndRule`, `OrRule`, `NotRule`): uma classe por regra composta da gramática. Guarda subexpressões e as avalia recursivamente.
- **Context** (`UserContext`): informações globais que a avaliação lê (aqui, os atributos do usuário).
- **Client** (`Program`): monta a árvore, ou a recebe de um parser, e então chama `Evaluate`.

## Exemplo (C#)
Uma feature flag fica habilitada para usuários que correspondem a uma regra de segmentação. A minigramática é `regra := atributo = valor | regra AND regra | regra OR regra | NOT regra`. O cliente monta a árvore manualmente; um parser produziria a mesma árvore a partir de texto.

```csharp
using System;
using System.Collections.Generic;

public class UserContext
{
    private readonly Dictionary<string, string> _attributes;

    public UserContext(Dictionary<string, string> attributes) => _attributes = attributes;

    public string? Get(string name) => _attributes.TryGetValue(name, out var v) ? v : null;
}

public interface IFlagRule
{
    bool Evaluate(UserContext context);
}

public class AttributeEquals : IFlagRule
{
    private readonly string _name;
    private readonly string _value;

    public AttributeEquals(string name, string value)
    {
        _name = name;
        _value = value;
    }

    public bool Evaluate(UserContext context) => context.Get(_name) == _value;
}

public class AndRule : IFlagRule
{
    private readonly IFlagRule _left;
    private readonly IFlagRule _right;

    public AndRule(IFlagRule left, IFlagRule right)
    {
        _left = left;
        _right = right;
    }

    public bool Evaluate(UserContext context) => _left.Evaluate(context) && _right.Evaluate(context);
}

public class OrRule : IFlagRule
{
    private readonly IFlagRule _left;
    private readonly IFlagRule _right;

    public OrRule(IFlagRule left, IFlagRule right)
    {
        _left = left;
        _right = right;
    }

    public bool Evaluate(UserContext context) => _left.Evaluate(context) || _right.Evaluate(context);
}

public class NotRule : IFlagRule
{
    private readonly IFlagRule _inner;

    public NotRule(IFlagRule inner) => _inner = inner;

    public bool Evaluate(UserContext context) => !_inner.Evaluate(context);
}

public static class Program
{
    public static void Main()
    {
        // country = BR AND (plan = pro OR beta = true) AND NOT role = staff
        IFlagRule rule = new AndRule(
            new AndRule(
                new AttributeEquals("country", "BR"),
                new OrRule(new AttributeEquals("plan", "pro"), new AttributeEquals("beta", "true"))),
            new NotRule(new AttributeEquals("role", "staff")));

        var user = new UserContext(new Dictionary<string, string>
        {
            ["country"] = "BR",
            ["plan"] = "free",
            ["beta"] = "true",
        });

        Console.WriteLine(rule.Evaluate(user)); // True
    }
}
```

## Variações
- **Construir a árvore.** O padrão não diz como a árvore é criada. Use um parser recursivo descendente escrito à mão, um dirigido por tabela, ou monte a árvore em código como acima.
- **Onde fica o `Evaluate`.** Se a linguagem vai receber muitas operações (avaliar, imprimir, validar, otimizar), coloque-as em um visitor ([visitor.md](visitor.md)) para que as classes de nó não mudem. Se há uma única operação, mantenha-a nos nós.
- **Compartilhar terminais.** Se o mesmo terminal aparece muitas vezes, uma única instância pode ser compartilhada, desde que os dados específicos da posição sejam passados pelo contexto e não guardados no nó. Veja [Flyweight](../structural/flyweight.md).
- **Contexto mutável.** O contexto também pode carregar resultados ou estado que os nós atualizam, por exemplo associações de variáveis, quando a avaliação tem efeitos colaterais.

## Riscos e alternativas em C#
- Não aumente a gramática por hábito. Passando de meia dúzia de regras, uma biblioteca ou gerador de parsers se encaixa melhor do que uma classe por regra.
- Em C#, uma árvore de lambdas pode substituir a hierarquia de classes. Combinadores `Func<UserContext, bool>` (`And(a, b)` retornando uma nova lambda) expressam as mesmas regras com menos cerimônia, quando você não precisa inspecionar nem imprimir a árvore.
- `System.Linq.Expressions` já oferece uma árvore de expressões que pode ser compilada para um delegate, que é o caminho de compilar para outra forma em caminhos quentes.
- Pattern matching e expressões `switch` sobre um conjunto fechado de tipos de nó são uma alternativa ao `Evaluate` virtual, e mantêm a operação fora dos nós.
- Regras vindas de usuários são entrada não confiável. Valide a sentença e limite a profundidade e o custo da recursão.

## Padrões relacionados
- [Composite](../structural/composite.md): a árvore sintática é um composite.
- [Flyweight](../structural/flyweight.md): compartilha símbolos terminais na árvore.
- [Iterator](iterator.md): pode percorrer a estrutura.
- [Visitor](visitor.md): mantém cada operação sobre os nós em uma única classe, em vez de espalhada pelas classes de nó.

## Verificação
- Cada classe de nó tem um teste, e algumas sentenças completas são testadas de ponta a ponta, incluindo negação e aninhamento.
- A avaliação lê apenas o contexto e a árvore, sem estado global oculto.
- Adicionar um novo tipo de regra significa adicionar uma classe, sem editar as outras.
- O número de classes de nó continua pequeno. Se ele não para de crescer, reconsidere um gerador de parsers.
