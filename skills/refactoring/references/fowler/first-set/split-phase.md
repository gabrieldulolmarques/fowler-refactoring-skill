# Dividir em Fases (Split Phase)

Fowler (2018), cap. 6, p. 154. Antes / também: —. Inversa: —.

## Quando usar

Smells: Alteração Divergente (Divergent Change), Cirurgia com Espingarda (Shotgun Surgery).

- Um trecho faz duas coisas diferentes em sequência, e a saída da primeira é a entrada da segunda: interpretar e depois calcular, calcular e depois formatar, validar e depois executar.
- As entradas não correspondem ao modelo de que a lógica principal precisa, então a lógica fica atulhada de trabalho de conversão.
- Se as primeiras linhas e as últimas linhas tocam variáveis e chamadas auxiliares não relacionadas, provavelmente são duas fases.
- Vale a pena quando mudanças estão a caminho em qualquer uma das preocupações. Se as duas partes nunca vão mudar de forma independente, um simples Extrair Função (Extract Function) pode bastar.
- As fases podem ser funções, ou módulos maiores. Uma fase também pode ser um pequeno objeto (por exemplo, um transformador) em vez de uma função.

## Mecânica

1. Extraia o código da segunda fase para uma função própria ([extract-function.md](extract-function.md)). Passe o que ela precisar como parâmetros simples por enquanto, mesmo que a lista seja longa.
2. Compile e teste.
3. Crie a estrutura de dados intermediária e passe-a para a função extraída como um parâmetro extra. Nesse ponto ela pode estar vazia.
4. Compile e teste.
5. Percorra os parâmetros da segunda fase um de cada vez. Se a primeira fase produz ou usa um parâmetro, guarde-o como campo da estrutura intermediária, leia-o de lá na segunda fase e elimine o parâmetro. Compile e teste após cada movimentação.
   - Se um parâmetro não deve ser conhecido pela segunda fase de forma alguma, calcule na primeira fase o valor que ele alimenta, guarde o resultado em um campo e mova a linha que o preenche de volta para o chamador ([move-statements-to-callers.md](../moving-features/move-statements-to-callers.md)).
   - Os parâmetros usados apenas pela segunda fase continuam como parâmetros.
6. O que sobra na função original agora é a primeira fase. Transforme-a em uma função própria cujo resultado é a estrutura intermediária ([extract-function.md](extract-function.md)), depois compile e teste. Se a primeira fase ganhar funções auxiliares que compartilham as mesmas entradas, ela pode virar um objeto (um transformador) cujo método retorna a estrutura intermediária; veja a variação abaixo.
7. Opcionalmente, arrume: internalize variáveis temporárias restantes na função orquestradora para que ela se leia como "execute a fase um, alimente a fase dois".

## Exemplo

Antes: um método ao mesmo tempo calcula os totais e renderiza o texto.

```csharp
using System.Collections.Generic;
using System.Text;

public class CartLine
{
    public string Sku { get; }
    public int Quantity { get; }
    public decimal UnitPrice { get; }

    public CartLine(string sku, int quantity, decimal unitPrice)
    {
        Sku = sku;
        Quantity = quantity;
        UnitPrice = unitPrice;
    }
}

public class CheckoutSummary
{
    public string Summary(IReadOnlyList<CartLine> lines, decimal taxRate, string currencySymbol)
    {
        decimal subtotal = 0m;
        foreach (var line in lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal tax = subtotal * taxRate;
        decimal shipping = subtotal >= 50m ? 0m : 4.90m;

        var sb = new StringBuilder();
        sb.AppendLine($"Items: {lines.Count}");
        sb.AppendLine($"Subtotal: {currencySymbol}{subtotal:F2}");
        sb.AppendLine($"Tax: {currencySymbol}{tax:F2}");
        sb.AppendLine($"Shipping: {currencySymbol}{shipping:F2}");
        return sb.ToString();
    }
}
```

Depois: os totais e a renderização são fases separadas, ligadas por um objeto `CartTotals`.

```csharp
using System.Collections.Generic;
using System.Text;

public class CartTotals
{
    public int ItemCount { get; }
    public decimal Subtotal { get; }
    public decimal Tax { get; }
    public decimal Shipping { get; }

    public CartTotals(int itemCount, decimal subtotal, decimal tax, decimal shipping)
    {
        ItemCount = itemCount;
        Subtotal = subtotal;
        Tax = tax;
        Shipping = shipping;
    }
}

public class CheckoutSummary
{
    public string Summary(IReadOnlyList<CartLine> lines, decimal taxRate, string currencySymbol)
    {
        var totals = ComputeTotals(lines, taxRate);
        return Render(totals, currencySymbol);
    }

    private static CartTotals ComputeTotals(IReadOnlyList<CartLine> lines, decimal taxRate)
    {
        decimal subtotal = 0m;
        foreach (var line in lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal tax = subtotal * taxRate;
        decimal shipping = subtotal >= 50m ? 0m : 4.90m;
        return new CartTotals(lines.Count, subtotal, tax, shipping);
    }

    private static string Render(CartTotals totals, string currencySymbol)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Items: {totals.ItemCount}");
        sb.AppendLine($"Subtotal: {currencySymbol}{totals.Subtotal:F2}");
        sb.AppendLine($"Tax: {currencySymbol}{totals.Tax:F2}");
        sb.AppendLine($"Shipping: {currencySymbol}{totals.Shipping:F2}");
        return sb.ToString();
    }
}
```

A mesma entrada gera a mesma saída. Agora um novo formato de saída toca apenas `Render`, e um novo total toca
`ComputeTotals` mais os campos que ele alimenta.

### Variação: a primeira fase como objeto transformador

Quando a primeira fase precisa de vários auxiliares sobre a mesma entrada, uma pequena classe os mantém juntos. A
classe recebe a entrada bruta, e um método devolve a estrutura intermediária. `Render` não muda.

```csharp
using System.Collections.Generic;
using System.Linq;
using System.Text;

public class CartTotals
{
    public int ItemCount { get; }
    public decimal Subtotal { get; }
    public decimal Tax { get; }
    public decimal Shipping { get; }

    public CartTotals(int itemCount, decimal subtotal, decimal tax, decimal shipping)
    {
        ItemCount = itemCount;
        Subtotal = subtotal;
        Tax = tax;
        Shipping = shipping;
    }
}

public class CartTotalsCalculator
{
    private readonly IReadOnlyList<CartLine> _lines;
    private readonly decimal _taxRate;

    public CartTotalsCalculator(IReadOnlyList<CartLine> lines, decimal taxRate)
    {
        _lines = lines;
        _taxRate = taxRate;
    }

    public CartTotals Run()
    {
        var subtotal = Subtotal();
        return new(_lines.Count, subtotal, subtotal * _taxRate, ShippingFor(subtotal));
    }

    private decimal Subtotal() => _lines.Sum(l => l.Quantity * l.UnitPrice);

    private static decimal ShippingFor(decimal subtotal) => subtotal >= 50m ? 0m : 4.90m;
}

public class CheckoutSummary
{
    public string Summary(IReadOnlyList<CartLine> lines, decimal taxRate, string currencySymbol)
    {
        var totals = new CartTotalsCalculator(lines, taxRate).Run();
        return Render(totals, currencySymbol);
    }

    private static string Render(CartTotals totals, string currencySymbol)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Items: {totals.ItemCount}");
        sb.AppendLine($"Subtotal: {currencySymbol}{totals.Subtotal:F2}");
        sb.AppendLine($"Tax: {currencySymbol}{totals.Tax:F2}");
        sb.AppendLine($"Shipping: {currencySymbol}{totals.Shipping:F2}");
        return sb.ToString();
    }
}
```

Mesma saída de antes, inclusive para um carrinho vazio (o frete continua sendo `4.90`, como no original).

## Notas (C#)

- A estrutura de dados intermediária costuma ser um `record` (ou um `readonly record struct` para dados pequenos e
  muito usados; C# 9+, e no Unity precisa de um shim de `IsExternalInit`). A imutabilidade impede que as fases
  alcancem o estado uma da outra.

## Verificação

- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: mesma saída para a mesma entrada, inclusive casos de borda como entrada vazia.
- A segunda fase não lê mais nada que só a primeira fase deveria conhecer; seus parâmetros são a estrutura
  intermediária mais os dados que ela realmente possui.
