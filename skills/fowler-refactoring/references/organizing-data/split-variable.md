# Dividir Variável (Split Variable)

Fowler (2018), cap. 9, p. 240. Antes / também: antes Remove Assignments to Parameters, antes Split Temp. Inversa: —.

## Quando usar
Smell: Dados Mutáveis (Mutable Data).

Uma variável que guarda o resultado de alguma computação para referência posterior deve ser atribuída uma só vez. Se ela é atribuída uma segunda vez com um valor que significa outra coisa, ela tem dois trabalhos, e o leitor precisa acompanhar qual deles ela tem em cada linha. Dê a cada trabalho a sua própria variável e o seu próprio nome.

Deixe em paz:
- Variáveis de laço, que mudam a cada iteração por natureza.
- Variáveis de coleta, que acumulam um valor (`total = total + x`, construção de string, adição a uma coleção). As atribuições posteriores dependem do valor anterior, então elas têm uma única responsabilidade.

Atribuir a um parâmetro de entrada é um caso comum: o parâmetro é ao mesmo tempo a entrada e o resultado de trabalho. Dividi-lo separa "o que o chamador me deu" de "o que estou calculando".

## Mecânica
1. Escolha o primeiro valor que a variável guarda. Na sua declaração e primeira atribuição, renomeie a variável para um nome que descreva apenas esse primeiro uso.
2. Atualize toda referência que lê esse primeiro valor, parando antes da segunda atribuição.
3. Compile e teste.
4. Na segunda atribuição, declare uma nova variável e nomeie-a para esse segundo uso.
5. Repita os passos 2 a 4 para cada atribuição posterior, testando após cada etapa. Na atribuição final o nome original não tem mais referências.
6. Para um parâmetro: declare uma variável local inicializada a partir do parâmetro no início da função, renomeie o parâmetro para dizer que é a entrada original e aponte para o parâmetro as leituras que significam a entrada original. Depois continue com os passos acima na variável local, renomeando-a para dizer o que ela guarda.

## Exemplo
Antes: `amount` primeiro guarda o subtotal do pedido e depois é reutilizada para o valor após o desconto, que é uma grandeza diferente.

```csharp
public decimal InvoiceTotal(Order order, Customer customer)
{
    decimal amount = order.Quantity * order.UnitPrice;
    Console.WriteLine($"Subtotal: {amount}");

    amount = amount - amount * customer.DiscountRate;
    return amount + order.ShippingFee;
}
```

Depois: uma variável por responsabilidade, cada uma nomeada pelo que guarda.

```csharp
public decimal InvoiceTotal(Order order, Customer customer)
{
    decimal subtotal = order.Quantity * order.UnitPrice;
    Console.WriteLine($"Subtotal: {subtotal}");

    decimal discounted = subtotal - subtotal * customer.DiscountRate;
    return discounted + order.ShippingFee;
}
```

Caso do parâmetro. Antes, `weight` é ao mesmo tempo a entrada e o custo de envio:

```csharp
public decimal ShippingCost(decimal weight, bool express)
{
    weight = Math.Max(weight, 1m) * 4.5m;
    if (express) weight *= 1.8m;
    return weight;
}
```

Intermediário: o parâmetro é renomeado para dizer que é a entrada, e uma variável local assume como valor de trabalho.

```csharp
public decimal ShippingCost(decimal weightKg, bool express)
{
    decimal weight = weightKg;
    weight = Math.Max(weight, 1m) * 4.5m;
    if (express) weight *= 1.8m;
    return weight;
}
```

Depois: a variável local é renomeada pelo que guarda.

```csharp
public decimal ShippingCost(decimal weightKg, bool express)
{
    decimal cost = Math.Max(weightKg, 1m) * 4.5m;
    if (express) cost *= 1.8m;
    return cost;
}
```

## Notas (C#)
- C# não tem variáveis locais imutáveis (`const` só serve para constantes de tempo de compilação), então mantenha cada nova variável atribuída exatamente uma vez.
- Renomear um parâmetro de um método público quebra os chamadores que o passam por nome (argumentos nomeados).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhuma variável é atribuída duas vezes para propósitos diferentes; as únicas atribuições repetidas que restam são contadores de laço e variáveis de coleta.
