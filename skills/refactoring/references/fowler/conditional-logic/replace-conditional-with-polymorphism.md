# Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism)

Fowler (2018), cap. 10, p. 272. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smells: Switches Repetidos (Repeated Switches), Obsessão por Primitivos (Primitive Obsession), Função Longa (Long Function).

- Várias funções fazem switch sobre o mesmo código de tipo (tipo de conta, tipo de documento, plano). Cada novo tipo força você a editar todos os switches. Mover cada tipo para uma classe põe todo o seu comportamento em um só lugar e remove a duplicação.
- Um caso é o caminho normal e alguns outros o ajustam. Mantenha o caminho normal na classe base e dê a cada ajuste sua própria subclasse.

Um `if`/`switch` simples costuma bastar. Use isto quando a mesma condicional é repetida ou difícil de acompanhar e os casos são tipos de verdade.

## Mecânica
1. Se não existirem classes para os casos, crie-as: uma classe base (ou interface) com uma subclasse por caso, mais uma função de fábrica que retorne a instância correta.
2. Altere os chamadores para obter o objeto da fábrica em vez de construí-lo ou de passar o código de tipo adiante. Compile e teste.
3. Se a condicional ainda não for um método autocontido, isole-a com [extract-function.md](../first-set/extract-function.md) e depois coloque esse método na classe base.
4. Escolha um caso. Adicione uma sobrescrita em sua subclasse contendo a lógica desse ramo, ajustada para usar os membros da própria subclasse. Opcionalmente, faça o ramo correspondente no método base lançar exceção, para que um teste falhe se ele ainda for alcançado. Compile e teste.
5. Repita o passo 4 para cada ramo, testando após cada um.
6. Decida o que o método base faz. Mantenha o ramo padrão como a implementação base ou, se a classe base nunca deve ser usada sozinha, torne o método `abstract`. Se a base continuar concreta, a fábrica deve retornar a classe base para valores desconhecidos; se for abstrata, a fábrica deve rejeitá-los.

**Além do livro:** se a lógica estiver espalhada em funções livres, agrupe-as antes com [combine-functions-into-class.md](../first-set/combine-functions-into-class.md). Quando o último ramo tiver sido movido, remova o `switch` agora vazio e, se nada mais o usar, o código de tipo; mantenha o código como propriedade até que seu último leitor desapareça. Para um caso de base e variante, talvez seja preciso extrair antes a parte variável de um método grande, para que a subclasse sobrescreva apenas essa parte e chame `base` para o resto; dê às partes extraídas nomes pelo que significam, não pelo caso.

## Exemplo
Antes: dois métodos fazem `switch` sobre o mesmo método de envio.

```csharp
using System;

public enum ShippingMethod { Standard, Express, Pickup }

public class Shipment
{
    public ShippingMethod Method { get; }
    public decimal WeightKg { get; }

    public Shipment(ShippingMethod method, decimal weightKg)
    {
        Method = method;
        WeightKg = weightKg;
    }

    public decimal Cost()
    {
        switch (Method)
        {
            case ShippingMethod.Standard: return 4m + WeightKg * 1.2m;
            case ShippingMethod.Express: return WeightKg > 20m ? 60m : 12m + WeightKg * 2.5m;
            case ShippingMethod.Pickup: return 0m;
            default: throw new InvalidOperationException();
        }
    }

    public int EstimatedDays()
    {
        switch (Method)
        {
            case ShippingMethod.Standard: return 5;
            case ShippingMethod.Express: return 2;
            case ShippingMethod.Pickup: return 1;
            default: throw new InvalidOperationException();
        }
    }
}
```

Depois: uma classe por método, criada por uma fábrica; os `switch` somem. Um método desconhecido agora falha na criação do objeto, e não na chamada de um método (mesmo tipo de exceção). Neste exemplo, nada lê mais `Method`, então ele foi removido. Em código real, mantenha-o até que o último leitor desapareça.

```csharp
using System;

public enum ShippingMethod { Standard, Express, Pickup }

public abstract class Shipment
{
    public decimal WeightKg { get; }

    protected Shipment(decimal weightKg) => WeightKg = weightKg;

    public static Shipment Create(ShippingMethod method, decimal weightKg) => method switch
    {
        ShippingMethod.Standard => new StandardShipment(weightKg),
        ShippingMethod.Express => new ExpressShipment(weightKg),
        ShippingMethod.Pickup => new PickupShipment(weightKg),
        _ => throw new InvalidOperationException()
    };

    public abstract decimal Cost();
    public abstract int EstimatedDays();
}

public class StandardShipment : Shipment
{
    public StandardShipment(decimal weightKg) : base(weightKg) { }
    public override decimal Cost() => 4m + WeightKg * 1.2m;
    public override int EstimatedDays() => 5;
}

public class ExpressShipment : Shipment
{
    public ExpressShipment(decimal weightKg) : base(weightKg) { }
    public override decimal Cost() => WeightKg > 20m ? 60m : 12m + WeightKg * 2.5m;
    public override int EstimatedDays() => 2;
}

public class PickupShipment : Shipment
{
    public PickupShipment(decimal weightKg) : base(weightKg) { }
    public override decimal Cost() => 0m;
    public override int EstimatedDays() => 1;
}
```

Variante da mesma ideia, base mais uma variante: `ParcelQuote` guarda as regras normais, e `OversizedParcelQuote` sobrescreve apenas a parte que difere. A fábrica escolhe a subclasse. Antes, era um único método: `Total(weightKg, oversized) => weightKg * 2m + (oversized ? 15m : 0m)`.

```csharp
public class ParcelQuote
{
    protected readonly decimal WeightKg;
    public ParcelQuote(decimal weightKg) => WeightKg = weightKg;

    public static ParcelQuote Create(decimal weightKg, bool oversized) =>
        oversized ? new OversizedParcelQuote(weightKg) : new ParcelQuote(weightKg);

    public decimal Total() => WeightKg * 2m + Surcharge();
    protected virtual decimal Surcharge() => 0m;
}

public class OversizedParcelQuote : ParcelQuote
{
    public OversizedParcelQuote(decimal weightKg) : base(weightKg) { }
    protected override decimal Surcharge() => base.Surcharge() + 15m;
}
```

## Notas (C#)
- Um `switch` sobre um código de tipo vira membros `abstract` ou `virtual`, ou uma interface, dependendo de os casos compartilharem código ou não.
- A fábrica é o único lugar que ainda faz `switch` sobre o código. Mantenha-a pequena e cubra-a com um teste para cada valor, inclusive o desconhecido.
- Se o código de tipo for persistido ou serializado, mantenha-o como dado e faça o mapeamento na fábrica.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada ramo movido tem um teste que falha se a sobrescrita for removida (se você usou o `throw` opcional do passo 4, o método base lança exceção até o último ramo ser movido).
