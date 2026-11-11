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
6. O que sobra na função original agora é a primeira fase. Transforme-a em uma função própria cujo resultado é a estrutura intermediária ([extract-function.md](extract-function.md)), depois compile e teste.
7. Opcionalmente, arrume: internalize variáveis temporárias restantes na função orquestradora para que ela se leia como "execute a fase um, alimente a fase dois".

## Exemplo

Antes: um método reúne estatísticas e também renderiza o texto.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, decimal Amount);

public class ReportService
{
    public string OrdersReport(IReadOnlyList<Order> orders, string currencySymbol)
    {
        var count = orders.Count;
        decimal total = 0m;
        decimal largest = 0m;
        foreach (var order in orders)
        {
            total += order.Amount;
            if (order.Amount > largest) largest = order.Amount;
        }

        var sb = new StringBuilder();
        sb.AppendLine($"Pedidos: {count}");
        sb.AppendLine($"Total: {currencySymbol}{total:F2}");
        sb.AppendLine($"Maior: {currencySymbol}{largest:F2}");
        return sb.ToString();
    }
}
```

Depois: estatísticas e renderização são fases separadas, ligadas por um `record`.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, decimal Amount);

public record OrderStats(int Count, decimal Total, decimal Largest);

public class ReportService
{
    public string OrdersReport(IReadOnlyList<Order> orders, string currencySymbol)
    {
        var stats = ComputeStats(orders);
        return Render(stats, currencySymbol);
    }

    private static OrderStats ComputeStats(IReadOnlyList<Order> orders)
    {
        decimal total = 0m;
        decimal largest = 0m;
        foreach (var order in orders)
        {
            total += order.Amount;
            if (order.Amount > largest) largest = order.Amount;
        }
        return new OrderStats(orders.Count, total, largest);
    }

    private static string Render(OrderStats stats, string currencySymbol)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Pedidos: {stats.Count}");
        sb.AppendLine($"Total: {currencySymbol}{stats.Total:F2}");
        sb.AppendLine($"Maior: {currencySymbol}{stats.Largest:F2}");
        return sb.ToString();
    }
}
```

A mesma saída para a mesma entrada. Agora um novo formato de saída toca apenas `Render`, e uma nova estatística toca `ComputeStats` mais os campos que ela alimenta.

## Notas de C#

- A estrutura de dados intermediária costuma ser um `record` (ou um `readonly record struct` para dados pequenos e muito usados). A imutabilidade impede que as fases mexam no estado uma da outra.

## Verificação

- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: mesma saída para a mesma entrada, inclusive em casos de borda como entrada vazia.
- A segunda fase não lê mais nada que só a primeira fase deveria saber; seus parâmetros são a estrutura intermediária mais os dados que ela realmente possui.
