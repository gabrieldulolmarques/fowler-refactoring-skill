# Substituir Condicional Aninhada por Cláusulas de Guarda (Replace Nested Conditional with Guard Clauses)

Fowler (2018), cap. 10, p. 266. Antes / também: —. Inversa: —.

## Quando usar
- Uma condicional tem um ramo que é o comportamento normal e outros ramos que são casos incomuns
  ou terminais (entrada inválida, dados ausentes, "nada a fazer").
- O aninhamento empurra o trabalho real para a direita, e o leitor precisa manter todas as condições
  envolventes em mente para entendê-lo.
- Uma variável `result` é atribuída em vários ramos apenas para ser retornada no final.

Uma cláusula de guarda marca um caso como um caminho lateral: trate-o e saia. Um if/else apresenta dois
caminhos como igualmente comuns. Escolha o formato que corresponde ao que o código significa.

Não use quando os dois ramos são comportamento normal: mantenha um if/else simples. Saída única é uma
preferência de estilo, então decida pela legibilidade.

## Mecânica
1. Escolha a condição mais externa que protege um caso incomum e reescreva-a como uma cláusula de
   guarda: teste o caso incomum e retorne seu resultado imediatamente. Se a condição protege
   o caso normal, inverta-a primeiro (aplique De Morgan se necessário e simplifique qualquer
   `!` que sobrar) para que o caso incomum se torne o retorno antecipado.
2. Compile e execute os testes.
3. Repita para a próxima condição, avançando para dentro, uma guarda de cada vez.
4. Quando as guardas não precisarem mais da variável de resultado, remova-a e retorne os valores
   diretamente.
5. Se várias guardas retornarem o mesmo valor, una-as com
   Consolidar Expressão Condicional (Consolidate Conditional Expression) ([consolidate-conditional-expression.md](consolidate-conditional-expression.md)).

## Exemplo
Antes: a taxa só é calculada quando o pedido não é retirada nem vazio, e fica abaixo do limite de frete grátis.

```csharp
public class Order
{
    public bool IsPickup { get; }
    public bool IsIsland { get; }
    public int ItemCount { get; }
    public int Zone { get; }
    public decimal Subtotal { get; }

    public Order(bool isPickup, bool isIsland, int itemCount, int zone, decimal subtotal)
    {
        IsPickup = isPickup;
        IsIsland = isIsland;
        ItemCount = itemCount;
        Zone = zone;
        Subtotal = subtotal;
    }
}

public class ShippingService
{
    public decimal ShippingFee(Order order)
    {
        decimal result;
        if (order.IsPickup)
        {
            result = 0m;
        }
        else
        {
            if (order.ItemCount == 0)
            {
                result = 0m;
            }
            else
            {
                if (order.Subtotal >= 100m)
                {
                    result = 0m;
                }
                else
                {
                    result = 7.5m + order.Zone * 1.5m;
                }
            }
        }
        return result;
    }
}
```

Depois da primeira cláusula de guarda (um passo, com testes rodando):

```csharp
public class ShippingService
{
    public decimal ShippingFee(Order order)
    {
        decimal result;
        if (order.IsPickup) return 0m;
        if (order.ItemCount == 0)
        {
            result = 0m;
        }
        else
        {
            if (order.Subtotal >= 100m) result = 0m;
            else result = 7.5m + order.Zone * 1.5m;
        }
        return result;
    }
}
```

Final, com a variável eliminada e os resultados iguais consolidados:

```csharp
public class ShippingService
{
    public decimal ShippingFee(Order order)
    {
        if (order.IsPickup || order.ItemCount == 0 || order.Subtotal >= 100m) return 0m;
        return 7.5m + order.Zone * 1.5m;
    }
}
```

Invertendo uma condição: quando um teste com `||` protege o caminho normal, inverta-o (De Morgan transforma o `||` em `&&`).

```csharp
// antes
public class SurchargeRules
{
    public decimal RemoteSurcharge(Order order)
    {
        if (order.Zone >= 4 || order.IsIsland)
        {
            if (!order.IsPickup)
                return 12m;
        }
        return 0m;
    }
}
```

```csharp
// depois
public class SurchargeRules
{
    public decimal RemoteSurcharge(Order order)
    {
        if (order.Zone < 4 && !order.IsIsland) return 0m;
        if (order.IsPickup) return 0m;
        return 12m;
    }
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada cláusula de guarda mantém o valor de retorno original para o seu caso, e a ordem das cláusulas segue a ordem original de avaliação (uma cláusula que chama algo com efeitos colaterais não pode passar antes de outra).
