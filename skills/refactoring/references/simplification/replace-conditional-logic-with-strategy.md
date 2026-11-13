# Substituir Lógica Condicional por Strategy (Replace Conditional Logic with Strategy)

Kerievsky (2004), cap. 7, p. 129. Direção: até, rumo a. Padrão: Strategy (GoF, p. 315).

## Quando usar
Smells: Complexidade Condicional (Conditional Complexity), Método Longo (Long Method), Obsessão por Primitivos (Primitive Obsession).

- Um método de cálculo tem muita lógica condicional que escolhe uma entre várias variantes de um algoritmo, e pequenos métodos auxiliares que servem a uma única variante estão lotando a classe.
- Prefira uma Strategy (composição) a [replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md) (herança) quando a classe hospedeira ainda não tem subclasses, quando criar subclasses multiplicaria classes (variantes de um algoritmo vezes outros eixos), ou quando os chamadores precisam trocar o algoritmo em tempo de execução sem mudar a classe do objeto.
- Se o hospedeiro já tem subclasses que mapeiam bem para as variantes, ou se um código de tipo dirige os condicionais, o polimorfismo é mais simples.
- Desvantagens: complica o design quando um refactoring condicional mais simples bastaria, e as strategies agora precisam de um jeito de ler os dados do contexto (veja o passo 2).

## Mecânica
Identifique o contexto: a classe com o método de cálculo cheio de condicionais.

1. Crie uma classe concreta, a strategy, com nome que descreva o que o cálculo faz (um sufixo `Strategy` serve). Ela se torna uma strategy concreta de verdade ao final.
2. Aplique Mover Função (Move Function) ([move-function.md](../moving-features/move-function.md)) para mover o método de cálculo para a strategy. Mantenha no contexto um método que delega a ela por meio de um novo campo. Decida como a strategy receberá seus dados:
   - Passe o contexto (no construtor ou no método). Menos parâmetros, e os novos membros do contexto ficam disponíveis de imediato, mas o contexto precisa expor mais de si mesmo.
   - Passe apenas os dados, como parâmetros. Menor acoplamento, mas cada strategy recebe dados que pode não usar. Se a lista crescer, aplique Introduzir Objeto de Parâmetros (Introduce Parameter Object) ([introduce-parameter-object.md](../first-set/introduce-parameter-object.md)) ou passe o contexto. Dados que só uma variante usa podem ir para o construtor dela depois.

   Mova para a strategy os métodos auxiliares usados apenas pelo cálculo. Compile e teste.
3. Deixe os clientes escolherem a strategy: aplique Extrair Parâmetro (Extract Parameter) ([extract-parameter.md](../utilities/extract-parameter.md)) ao código do contexto que cria a strategy e atribui o campo. Compile e teste.
4. Aplique Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) ([replace-conditional-with-polymorphism.md](../conditional-logic/replace-conditional-with-polymorphism.md)) ao método de cálculo da strategy. Use Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses) ([replace-type-code-with-subclasses.md](../inheritance/replace-type-code-with-subclasses.md)) como primeiro passo, mesmo que as variantes estejam só implícitas nas condições e não exista código explícito. Crie uma subclasse por vez, e torne a strategy abstrata (ou uma interface), se for possível. Compile e teste com todas as combinações de contexto e strategy concreta.
5. Se o contexto for construído em muitos lugares, esconda a construção da strategy atrás de um método de criação ([encapsulate-classes-with-factory.md](../creation/encapsulate-classes-with-factory.md)).

## Exemplo
Antes: a variante é deduzida de quais campos anuláveis estão preenchidos, e uma combinação cai no zero.

```csharp
using System;

public class Order
{
    public decimal Weight { get; init; }
    public decimal DistanceKm { get; init; }
    public bool Fragile { get; init; }
    public DateTime? ExpressDeadline { get; init; }
    public string? PickupPoint { get; init; }

    public decimal ShippingCost()
    {
        if (PickupPoint != null && ExpressDeadline == null)
            return 2m;
        if (ExpressDeadline != null && PickupPoint == null)
        {
            decimal cost = Weight * 3m + DistanceKm * 0.5m;
            return Fragile ? cost + 10m : cost;
        }
        if (PickupPoint == null && ExpressDeadline == null)
            return Weight * 1.2m + DistanceKm * 0.1m;
        return 0m;
    }
}
```

Depois: cada variante é uma strategy, e o pedido recebe uma delas. O pedido se passa a si mesmo porque as strategies leem várias de suas propriedades. O caso impossível "os dois preenchidos" desaparece, porque o chamador agora escolhe a variante explicitamente. Trocar é uma atribuição de propriedade.

```csharp
public interface IShippingStrategy
{
    decimal Cost(Order order);
}

public class PickupShipping : IShippingStrategy
{
    public decimal Cost(Order order) => 2m;
}

public class ExpressShipping : IShippingStrategy
{
    public decimal Cost(Order order)
    {
        decimal cost = order.Weight * 3m + order.DistanceKm * 0.5m;
        return order.Fragile ? cost + 10m : cost;
    }
}

public class StandardShipping : IShippingStrategy
{
    public decimal Cost(Order order) => order.Weight * 1.2m + order.DistanceKm * 0.1m;
}

public class Order
{
    public decimal Weight { get; init; }
    public decimal DistanceKm { get; init; }
    public bool Fragile { get; init; }
    public IShippingStrategy Shipping { get; set; } = new StandardShipping();

    public decimal ShippingCost() => Shipping.Cost(this);
}
```

## Notas (C#)
- Uma interface basta quando as strategies não compartilham código. Use uma classe abstrata se elas compartilham auxiliares.
- Strategies sem estado podem ser compartilhadas como instâncias `static readonly`. Faça isso quando um profiler pedir, não antes.
- Com injeção de dependência, registre as strategies e deixe uma fábrica ou o chamador escolher uma pela chave.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Um teste por strategy concreta, mais um que troca a strategy de um contexto existente e verifica o novo resultado.
- Confirme que nenhuma entrada aceita pelo condicional antigo ficou inalcançável ou passou a ter preço diferente (aqui, a queda para zero).
