# Substituir Laço por Pipeline (Replace Loop with Pipeline)

Fowler (2018), cap. 8, p. 231. Antes / também: —. Inversa: —.

## Quando usar
Smell: Laços (Loops). Um laço que seleciona alguns itens, os converte e reúne os resultados
lê melhor como uma sequência de passos, cada um recebendo uma coleção e produzindo outra, lida
de cima para baixo. Use quando o corpo do laço mistura pular, filtrar, converter e
acumular, ou quando ele mantém flags apenas para pular ou selecionar elementos.

Não use quando o laço tiver efeitos colaterais reais por item que precisam acontecer em ordem, quando
ele sair antecipadamente de um jeito que nenhum passo do pipeline expresse bem, ou em um caminho crítico medido em que
as alocações extras importem.

## Mecânica
1. Introduza uma nova variável que guarde a coleção sobre a qual o laço itera (pode ser uma
   cópia simples da origem existente) e faça o laço iterar sobre ela. Compile e teste.
2. Pegue o primeiro pedaço de comportamento no topo do laço (pular itens, uma condição de
   filtro, uma conversão) e remova-o do corpo do laço. Adicione a operação correspondente à
   expressão que constrói a nova variável. Compile e teste.
3. Repita o passo 2 para cada pedaço de comportamento seguinte, em ordem, testando após cada um.
   Apague as variáveis de controle que não são mais necessárias à medida que ficam mortas.
4. Quando o laço não fizer nada além de adicionar itens a um acumulador, remova o laço e atribua
   o resultado do pipeline ao acumulador. Compile e teste.
5. Arrume: internalize o acumulador e a variável intermediária se ficar mais legível,
   renomeie os parâmetros das lambdas para dizerem o que guardam e ponha uma operação por linha.

## Exemplo
Antes: os números das primeiras faturas vencidas, até um limite.

```csharp
using System;
using System.Collections.Generic;

public record Invoice(string Number, DateOnly DueDate, bool IsPaid);

public class InvoiceReport
{
    public List<string> OverdueNumbers(IEnumerable<Invoice> invoices, DateOnly today, int limit)
    {
        var result = new List<string>();
        foreach (var invoice in invoices)
        {
            if (result.Count == limit) break;
            if (invoice.IsPaid) continue;
            if (invoice.DueDate >= today) continue;
            result.Add(invoice.Number.ToUpperInvariant());
        }
        return result;
    }
}
```

Depois: a verificação do contador e os `continue`s sumiram, e cada passo é uma linha.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public record Invoice(string Number, DateOnly DueDate, bool IsPaid);

public class InvoiceReport
{
    public List<string> OverdueNumbers(IEnumerable<Invoice> invoices, DateOnly today, int limit)
    {
        return invoices
            .Where(invoice => !invoice.IsPaid)
            .Where(invoice => invoice.DueDate < today)
            .Select(invoice => invoice.Number.ToUpperInvariant())
            .Take(limit)
            .ToList();
    }
}
```

O limite conta resultados, não itens lidos, então `Take` vem depois dos filtros.

## Notas (C#)
- Use LINQ: `Where` para filtrar, `Select` para mapear, `Skip`/`Take` para fatiar, `ToList()` ou
  `ToArray()` para produzir a coleção final.
- LINQ é preguiçoso. Enumere uma vez, no fim do pipeline, e não guarde uma consulta adiada
  que seja enumerada de novo mais tarde sobre dados alterados ou caros de ler.
- Cada passo pode alocar (delegados, iteradores, arrays intermediários). Em caminhos críticos, meça
  antes e depois, e mantenha o laço se o custo aparecer.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
