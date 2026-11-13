# Internalizar Função (Inline Function)

Fowler (2018), cap. 6, p. 115. Nome anterior / outro nome: Inline Method. Inversa: Extrair Função (Extract Function)
([extract-function.md](extract-function.md)).

## Quando usar
Smells: Elemento Ocioso (Lazy Element), Intermediário (Middle Man), Generalidade Especulativa (Speculative Generality), Cirurgia com Espingarda (Shotgun Surgery).

- O corpo diz tudo o que o nome diz, então a função acrescenta um salto e nenhum significado.
- Uma cadeia de funções em que cada uma apenas encaminha para a próxima, e você perde de vista onde o trabalho acontece. Internalize-as, mantenha os saltos que se justificam, descarte o resto.
- Uma responsabilidade espalhada por muitas funções pequenas (Cirurgia com Espingarda). Internalize-as e depois extraia de novo por linhas melhores.
- Um conjunto de funções dividido pelas linhas erradas. Internalize todas em uma função e depois extraia de novo com fronteiras melhores.

Não use quando a função é polimórfica (sobrescrita), é recursiva, tem vários pontos de retorno que não se encaixam no chamador, ou quando encaixar o corpo no chamador dá muito trabalho. Nesses casos o custo é maior que o ganho: deixe a função em paz.

## Mecânica
1. Verifique se a função não é polimórfica: nenhuma subclasse a sobrescreve e ela não implementa um membro de interface que outros tipos também implementam.
2. Encontre todos os chamadores (busque na base de código inteira, não só no arquivo).
3. Substitua uma chamada pelo corpo, renomeando os parâmetros para os argumentos em uso e ajustando as variáveis locais para que não colidam com as do chamador.
4. Compile e execute os testes após cada substituição. A internalização não precisa ser feita toda de uma vez.
5. Se o corpo for difícil de encaixar, mova-o uma instrução por vez (veja [move-statements-to-callers.md](../moving-features/move-statements-to-callers.md)) até que a função fique vazia.
6. Quando não restar nenhum chamador, apague a função.
7. Se um passo quebrar os testes e a causa não for óbvia, reverta ao último estado verde e refaça em passos menores.

## Exemplo

Antes: `IsBulkOrder` apenas envolve uma comparação.

```csharp
public class Cart
{
    public int Id { get; }
    public int Units { get; }

    public Cart(int id, int units)
    {
        Id = id;
        Units = units;
    }
}

public class Discounts
{
    public decimal UnitDiscount(Cart cart)
    {
        return IsBulkOrder(cart) ? 1.50m : 0m;
    }

    private bool IsBulkOrder(Cart c)
    {
        return c.Units >= 10;
    }
}
```

Depois: a chamada é substituída (o parâmetro `c` vira o argumento `cart`) e o auxiliar é removido.

```csharp
public class Discounts
{
    public decimal UnitDiscount(Cart cart)
    {
        return cart.Units >= 10 ? 1.50m : 0m;
    }
}
```

Um caso que precisa de mais cuidado: o auxiliar escreve em um objeto que pertence ao chamador.

```csharp
using System.Linq;
using System.Text;

public class PricedCart
{
    public decimal[] ItemPrices { get; }

    public PricedCart(decimal[] itemPrices) => ItemPrices = itemPrices;
}

public class CartSummary
{
    // Antes
    public string BuildSummary(PricedCart cart)
    {
        var sb = new StringBuilder();
        AppendTotals(sb, cart);
        return sb.ToString();
    }

    private void AppendTotals(StringBuilder target, PricedCart source)
    {
        target.Append($"items: {source.ItemPrices.Length}; ");
        target.Append($"total: {source.ItemPrices.Sum()}");
    }
}

public class CartSummaryAfter
{
    // Depois
    public string BuildSummary(PricedCart cart)
    {
        var sb = new StringBuilder();
        sb.Append($"items: {cart.ItemPrices.Length}; ");
        sb.Append($"total: {cart.ItemPrices.Sum()}");
        return sb.ToString();
    }
}
```

## Notas (C#)
- Não internalize um método `virtual` ou `override`, nem uma implementação de interface, sem verificar as outras
  implementações: os chamadores que passam pelo tipo base ou pela interface ainda precisam do método.
- Um método alcançado por reflexão, injeção de dependência, serialização ou inscrição em evento tem chamadores
  que uma busca por texto não encontra.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
