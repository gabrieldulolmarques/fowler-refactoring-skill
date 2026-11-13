# Extrair Variável (Extract Variable)

Fowler (2018), cap. 6, p. 119. Antes / também: Introduce Explaining Variable. Inversa: Internalizar
Variável (Inline Variable) ([inline-variable.md](inline-variable.md)).

## Quando usar
- Uma expressão mistura várias ideias e o leitor precisa decifrá-la, ou um comentário existe só
  para dizer o que um pedaço dela significa. Uma variável bem nomeada torna o comentário desnecessário.
- A mesma subexpressão aparece mais de uma vez e merece um nome só.
- Você quer um lugar para pôr um breakpoint ou uma chamada de log em um valor intermediário.

Defina o escopo do nome antes de extrair. Se ele só faz sentido dentro desta função, uma variável
local é o certo. Se descreve algo sobre o objeto inteiro (ou é útil para outros
chamadores), faça dele um método ou propriedade, com Extrair Função (Extract Function)
([extract-function.md](extract-function.md)) ou depois com Substituir Variável Temporária por Consulta (Replace Temp with Query) ([replace-temp-with-query.md](../encapsulation/replace-temp-with-query.md)).
Prefira o escopo mais amplo quando for barato, porque o nome passa a ficar disponível em todo lugar.

Não use quando o nome não acrescentaria nada que a expressão já não diga (esse é o
caso de Internalizar Variável).

## Mecânica
1. Garanta que a expressão não tem efeitos colaterais, e que avaliá-la uma vez em vez de
   várias não muda nada.
2. Declare uma variável local imutável (`var` ou um tipo explícito, nunca reatribuída) e
   inicialize-a com uma cópia da expressão.
3. Substitua a expressão original pela variável.
4. Compile e execute os testes.
5. Se a mesma expressão aparecer em outro ponto do escopo, troque esses pontos pela variável
   também, um ponto por passo, e execute os testes entre as trocas.
6. Apague qualquer comentário que agora só repita o que o nome da variável diz.

## Exemplo

Antes:

```csharp
public class Cart
{
    public decimal Subtotal { get; }
    public decimal WeightKg { get; }

    public Cart(decimal subtotal, decimal weightKg)
    {
        Subtotal = subtotal;
        WeightKg = weightKg;
    }
}

public class ShippingOption
{
    public bool IsExpress { get; }

    public ShippingOption(bool isExpress) => IsExpress = isExpress;
}

public class ShippingPolicy
{
    public bool OffersFreeShipping(Cart cart, ShippingOption option)
    {
        // gasta pelo menos 50, é leve o bastante e não é expresso
        return cart.Subtotal >= 50m
            && cart.WeightKg <= 20m
            && !option.IsExpress;
    }
}
```

Depois de extrair cada condição, uma por vez, com os testes executados após cada passo (este é o estado final):

```csharp
public class ShippingPolicy
{
    public bool OffersFreeShipping(Cart cart, ShippingOption option)
    {
        var meetsMinimumSpend = cart.Subtotal >= 50m;
        var isLightEnough = cart.WeightKg <= 20m;
        var isStandardSpeed = !option.IsExpress;
        return meetsMinimumSpend && isLightEnough && isStandardSpeed;
    }
}
```

Se um nome como `meetsMinimumSpend` também for significativo para outros membros de `Cart`, transforme-o em
uma propriedade somente leitura da classe, em vez de uma variável local.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
