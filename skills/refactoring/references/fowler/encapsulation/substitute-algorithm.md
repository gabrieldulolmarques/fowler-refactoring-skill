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

Antes: uma acumulação escrita à mão que soma as cobranças por conta e depois procura o maior total.

```csharp
using System.Collections.Generic;

public class Charge
{
    public Charge(string account, decimal amount) { Account = account; Amount = amount; }
    public string Account { get; }
    public decimal Amount { get; }
}

public static class BillingStats
{
    public static string? TopAccount(List<Charge> charges)
    {
        var accounts = new List<string>();
        var totals = new List<decimal>();
        foreach (var charge in charges)
        {
            int index = accounts.IndexOf(charge.Account);
            if (index < 0)
            {
                accounts.Add(charge.Account);
                totals.Add(charge.Amount);
            }
            else
            {
                totals[index] += charge.Amount;
            }
        }
        if (accounts.Count == 0) return null;
        int best = 0;
        for (int i = 1; i < accounts.Count; i++)
        {
            if (totals[i] > totals[best]) best = i;
        }
        return accounts[best];
    }
}
```

Depois: o mesmo resultado, com agrupamento, soma e ordenação delegados à biblioteca.

```csharp
using System.Collections.Generic;
using System.Linq;

public static class BillingStats
{
    public static string? TopAccount(List<Charge> charges) =>
        charges
            .GroupBy(c => c.Account)
            .Select(g => new { Account = g.Key, Total = g.Sum(c => c.Amount) })
            .OrderByDescending(x => x.Total)
            .FirstOrDefault()?.Account;
}
```

Os testes que fixavam o comportamento antigo (vence o maior total, em empate vence a primeira conta, uma
lista vazia devolve null) passam sem mudanças contra o novo corpo.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os testes da função rodaram contra os dois algoritmos, com as mesmas entradas, antes de o antigo ser apagado.
