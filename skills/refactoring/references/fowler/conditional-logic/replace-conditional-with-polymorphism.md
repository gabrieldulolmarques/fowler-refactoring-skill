# Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism)

Fowler (2018), cap. 10, p. 272. Antes / também: —. Inversa: —.

## Quando usar
Smells: Switches Repetidos (Repeated Switches), Obsessão por Primitivos (Primitive Obsession), Função Longa (Long Function).

- Várias funções fazem switch sobre o mesmo código de tipo (tipo de conta, tipo de documento, plano). Cada novo tipo força você a editar todos os switches. Mover cada tipo para uma classe põe todo o seu comportamento em um só lugar e remove a duplicação.
- Um caso é o caminho normal e alguns outros o ajustam. Mantenha o caminho normal na classe base e dê a cada ajuste sua própria subclasse.

Um `if`/`switch` simples costuma bastar. Use isto quando a mesma condicional é repetida ou difícil de acompanhar e os casos são tipos de verdade.

## Mecânica
1. Primeiro passo opcional: se a lógica estiver espalhada em funções livres, agrupe-as antes com [combine-functions-into-class.md](../first-set/combine-functions-into-class.md).
2. Se não existirem classes para os casos, crie-as: uma classe base (ou interface) com uma subclasse por caso, mais uma função de fábrica que retorne a instância correta.
3. Altere os chamadores para obter o objeto da fábrica em vez de construí-lo ou de passar o código de tipo adiante. Compile e teste.
4. Se a condicional ainda não for um método autocontido, isole-a com [extract-function.md](../first-set/extract-function.md) e depois coloque esse método na classe base.
5. Escolha um caso. Adicione um override em sua subclasse contendo a lógica desse ramo, ajustada para usar os membros da própria subclasse. Opcionalmente, faça o ramo correspondente no método base lançar exceção, para que um teste falhe se ele ainda for alcançado. Compile e teste.
6. Repita o passo 5 para cada ramo, testando após cada um.
7. Decida o que o método base faz. Mantenha o ramo padrão como a implementação base ou, se a classe base nunca deve ser usada sozinha, torne o método `abstract`. Se a base continuar concreta, a fábrica deve retornar a classe base para valores desconhecidos; se for abstrata, a fábrica deve rejeitá-los.
8. Remova o `switch` agora vazio e, se nada mais o usar, o código de tipo. Mantenha o código como propriedade até que seu último leitor desapareça.
9. Para um caso de base e variante, talvez seja preciso extrair antes a parte variável de um método grande, para que a subclasse sobrescreva apenas essa parte e chame `base` para o resto. Dê às partes extraídas nomes pelo que significam, não pelo caso.

## Exemplo
Antes: dois métodos fazem switch sobre o mesmo tipo de conta.

```csharp
using System;

public enum AccountKind { Standard, Premium, Student }

public class Account
{
    public AccountKind Kind { get; }
    public decimal Balance { get; }

    public Account(AccountKind kind, decimal balance)
    {
        Kind = kind;
        Balance = balance;
    }

    public decimal MonthlyFee()
    {
        switch (Kind)
        {
            case AccountKind.Standard: return 5m;
            case AccountKind.Premium: return Balance > 10000m ? 0m : 12m;
            case AccountKind.Student: return 0m;
            default: throw new InvalidOperationException();
        }
    }

    public int FreeTransfers()
    {
        switch (Kind)
        {
            case AccountKind.Standard: return 3;
            case AccountKind.Premium: return 20;
            case AccountKind.Student: return 5;
            default: throw new InvalidOperationException();
        }
    }
}
```

Depois: uma classe por tipo, criada por uma fábrica; os switches sumiram. Um tipo desconhecido agora falha quando o objeto é criado, e não quando um método é chamado (mesmo tipo de exceção). Neste exemplo nada mais lê `Kind`, então ele foi removido. Em código real, mantenha-o até que seu último leitor desapareça.

```csharp
using System;

public enum AccountKind { Standard, Premium, Student }

public abstract class Account
{
    public decimal Balance { get; }

    protected Account(decimal balance) => Balance = balance;

    public static Account Create(AccountKind kind, decimal balance) => kind switch
    {
        AccountKind.Standard => new StandardAccount(balance),
        AccountKind.Premium => new PremiumAccount(balance),
        AccountKind.Student => new StudentAccount(balance),
        _ => throw new InvalidOperationException()
    };

    public abstract decimal MonthlyFee();
    public abstract int FreeTransfers();
}

public class StandardAccount : Account
{
    public StandardAccount(decimal balance) : base(balance) { }
    public override decimal MonthlyFee() => 5m;
    public override int FreeTransfers() => 3;
}

public class PremiumAccount : Account
{
    public PremiumAccount(decimal balance) : base(balance) { }
    public override decimal MonthlyFee() => Balance > 10000m ? 0m : 12m;
    public override int FreeTransfers() => 20;
}

public class StudentAccount : Account
{
    public StudentAccount(decimal balance) : base(balance) { }
    public override decimal MonthlyFee() => 0m;
    public override int FreeTransfers() => 5;
}
```

Variante da mesma ideia, base mais uma variante: `ShippingQuote` guarda as regras normais, e `ExpressShippingQuote` sobrescreve apenas a parte que difere. A fábrica escolhe a subclasse. Antes, era um único método: `Total(weight, express) => weight * 2m + (express ? 15m : 0m)`.

```csharp
public class ShippingQuote
{
    protected readonly decimal Weight;
    public ShippingQuote(decimal weight) => Weight = weight;

    public static ShippingQuote Create(decimal weight, bool express) =>
        express ? new ExpressShippingQuote(weight) : new ShippingQuote(weight);

    public decimal Total() => Weight * 2m + Surcharge();
    protected virtual decimal Surcharge() => 0m;
}

public class ExpressShippingQuote : ShippingQuote
{
    public ExpressShippingQuote(decimal weight) : base(weight) { }
    protected override decimal Surcharge() => base.Surcharge() + 15m;
}
```

## Notas (C#)
- Um `switch` sobre um código de tipo vira membros `abstract` ou `virtual`, ou uma interface, conforme os casos compartilhem código ou não.
- A fábrica é o único lugar que ainda faz switch sobre o código. Mantenha-a pequena e cubra-a com um teste para cada valor, inclusive o desconhecido.
- Se o código de tipo for persistido ou serializado, mantenha-o como dado e mapeie-o na fábrica.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada ramo movido tem um teste que falha se o override for removido (se você usou o lançamento de exceção opcional no passo 5, o método base lança exceção até que o último ramo seja movido).
