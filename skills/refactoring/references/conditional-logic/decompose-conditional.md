# Decompor Condicional (Decompose Conditional)

Fowler (2018), cap. 10, p. 260. Antes / também: —. Inversa: —. É Extrair Função (Extract Function)
([extract-function.md](../first-set/extract-function.md)) aplicada às partes de uma condicional.

## Quando usar
Smells: Função Longa (Long Function) (lógica condicional que esconde a intenção).

- A condição é uma expressão booleana composta e o leitor precisa descobrir o que ela significa.
- Os ramos guardam cálculos ou sequências de instruções cujo propósito não é óbvio.
- Um comentário acima do `if` explica a condição, ou comentários rotulam cada ramo.

O ponto é dar nomes: a condição ganha um nome para a pergunta de negócio que faz, e cada
ramo ganha um nome para o que produz. Pule quando a condição e os ramos já forem
de uma linha e lerem como a intenção.

## Mecânica
1. Extraia a condição para sua própria função (ou propriedade) com o nome da pergunta que ela faz.
   Compile e teste.
2. Extraia o corpo do ramo `then` para uma função com o nome do seu resultado. Compile e
   teste.
3. Extraia o corpo do ramo `else` da mesma forma. Compile e teste.
4. Para uma cadeia de `else if`, trate cada condição e ramo seguintes do mesmo jeito, um de cada vez.
5. Opcionalmente, quando cada ramo apenas atribui ou retorna um valor, reescreva a instrução como uma
   expressão ternária (`x = Condition() ? A() : B();`). Compile e teste.

## Exemplo
Antes:

```csharp
public decimal ShippingCost(Order order, DateTime today)
{
    decimal cost;
    if (today >= order.Promo.Start && today <= order.Promo.End && order.Total >= order.Promo.MinimumTotal)
        cost = order.Weight * order.Promo.RatePerKg;
    else
        cost = order.Weight * order.StandardRatePerKg + order.HandlingFee;
    return cost;
}
```

Depois:

```csharp
public decimal ShippingCost(Order order, DateTime today)
{
    return QualifiesForPromo(order, today)
        ? PromoShipping(order)
        : StandardShipping(order);
}

private static bool QualifiesForPromo(Order order, DateTime today) =>
    today >= order.Promo.Start
    && today <= order.Promo.End
    && order.Total >= order.Promo.MinimumTotal;

private static decimal PromoShipping(Order order) =>
    order.Weight * order.Promo.RatePerKg;

private static decimal StandardShipping(Order order) =>
    order.Weight * order.StandardRatePerKg + order.HandlingFee;
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
