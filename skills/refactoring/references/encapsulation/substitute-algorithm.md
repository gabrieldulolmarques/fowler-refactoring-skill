# Substituir Algoritmo (Substitute Algorithm)

Fowler (2018), cap. 7, p. 195. Antes / também: —. Inversa: —.

## Quando usar
- Você entende melhor o problema agora e enxerga um jeito muito mais simples de obter o mesmo resultado.
- Uma biblioteca, framework ou recurso da linguagem já oferece o que seu código faz à mão.
- O comportamento precisa mudar um pouco, e trocar antes por um algoritmo diferente tornaria essa mudança fácil.

Não use em uma função grande e emaranhada do jeito que está. Quebre a função antes, de modo que o que você substitui seja pequeno e seu comportamento fácil de fixar.

## Mecânica
1. Isole o código a substituir para que ele preencha uma função inteira sozinho. Use Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) e simplifique mais até a função ficar pequena.
2. Escreva testes que exercitem apenas essa função e capturem seu comportamento atual, incluindo casos extremos (entrada vazia, nenhuma correspondência, duplicatas, valores limite).
3. Escreva o novo algoritmo ao lado do antigo (por exemplo, com um nome temporário), sem remover o antigo ainda.
4. Execute o compilador e qualquer análise estática no novo código.
5. Execute os testes contra o novo algoritmo e compare sua saída com a do antigo nas mesmas entradas. Se os resultados coincidirem, apague o algoritmo antigo e dê à função seu nome final. Se diferirem, mantenha a versão antiga como referência enquanto depura a nova.

## Exemplo
Antes: uma acumulação escrita à mão que soma os pedidos por cliente e depois varre em busca do maior total.

```csharp
using System.Collections.Generic;

public record Order(string Customer, decimal Total);

public static class OrderStats
{
    public static string? TopCustomer(List<Order> orders)
    {
        var customers = new List<string>();
        var totals = new List<decimal>();
        foreach (var order in orders)
        {
            int index = customers.IndexOf(order.Customer);
            if (index < 0)
            {
                customers.Add(order.Customer);
                totals.Add(order.Total);
            }
            else
            {
                totals[index] += order.Total;
            }
        }
        if (customers.Count == 0) return null;
        int best = 0;
        for (int i = 1; i < customers.Count; i++)
        {
            if (totals[i] > totals[best]) best = i;
        }
        return customers[best];
    }
}
```

Depois: o mesmo resultado, com o agrupamento, a soma e a escolha do máximo delegados à biblioteca.

```csharp
using System.Collections.Generic;
using System.Linq;

public record Order(string Customer, decimal Total);

public static class OrderStats
{
    public static string? TopCustomer(List<Order> orders) =>
        orders
            .GroupBy(o => o.Customer)
            .Select(g => new { Customer = g.Key, Total = g.Sum(o => o.Total) })
            .MaxBy(x => x.Total)?.Customer;
}
```

Os testes que fixavam o comportamento antigo (o maior total vence, o primeiro cliente vence um empate, uma lista vazia retorna null) passam sem alteração contra o novo corpo.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os testes da função rodaram contra os dois algoritmos com as mesmas entradas antes de o antigo ser apagado.
