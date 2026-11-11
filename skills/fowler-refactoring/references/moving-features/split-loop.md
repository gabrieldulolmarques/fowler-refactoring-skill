# Dividir Laço (Split Loop)

Fowler (2018), cap. 8, p. 227. Antes / também: —. Inversa: —.

## Quando usar
Smells: Função Longa (Long Function).

- Um laço faz dois ou mais trabalhos sem relação apenas porque eles podem compartilhar uma única passada pelos dados.
- Você quer extrair um desses trabalhos para sua própria função, mas o laço teria que retornar vários valores ou preencher várias variáveis.
- Quem modifica um cálculo precisa entender todos os outros do laço.

Não decida contra isso só porque os dados são percorridos duas vezes. A clareza vem primeiro; meça depois e junte os laços de volta se a travessia for um gargalo comprovado. Um laço dividido também costuma ser mais fácil de otimizar isoladamente. Deixe o laço em paz se os dois cálculos realmente dependerem um do outro (um lê o que o outro escreve na mesma passada).

## Mecânica
1. Garanta que os testes cubram os resultados do laço.
2. Copie o laço, de modo que a mesma travessia apareça duas vezes em sequência.
3. Em cada cópia, remova as instruções que pertencem à outra responsabilidade, especialmente qualquer coisa com efeitos colaterais (atribuições, acumulação, chamadas que mudam estado). Instruções sem efeitos colaterais podem ficar por enquanto.
4. Compile e execute os testes.
5. Opcionalmente, use Deslocar Instruções (Slide Statements) ([slide-statements.md](slide-statements.md)) para mover a declaração de cada acumulador para junto do seu próprio laço.
6. Considere Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) em cada laço e Substituir Laço por Pipeline (Replace Loop with Pipeline) ([replace-loop-with-pipeline.md](replace-loop-with-pipeline.md)) onde ficar mais legível.

## Exemplo
Antes: uma passada calcula tanto o total quanto a data de vencimento mais recente.

```csharp
using System;
using System.Collections.Generic;

public record Invoice(decimal Amount, DateTime DueDate);

public static class InvoiceReport
{
    public static string Summarize(IReadOnlyList<Invoice> invoices)
    {
        decimal total = 0;
        DateTime latestDue = DateTime.MinValue;
        foreach (var invoice in invoices)
        {
            total += invoice.Amount;
            if (invoice.DueDate > latestDue) latestDue = invoice.DueDate;
        }

        return $"total: {total}, latest due: {latestDue:yyyy-MM-dd}";
    }
}
```

Depois: um laço por responsabilidade, e depois cada um extraído para uma função.

```csharp
using System;
using System.Collections.Generic;

public record Invoice(decimal Amount, DateTime DueDate);

public static class InvoiceReport
{
    public static string Summarize(IReadOnlyList<Invoice> invoices)
    {
        return $"total: {TotalAmount(invoices)}, latest due: {LatestDueDate(invoices):yyyy-MM-dd}";
    }

    private static decimal TotalAmount(IReadOnlyList<Invoice> invoices)
    {
        decimal total = 0;
        foreach (var invoice in invoices)
        {
            total += invoice.Amount;
        }
        return total;
    }

    private static DateTime LatestDueDate(IReadOnlyList<Invoice> invoices)
    {
        DateTime latestDue = DateTime.MinValue;
        foreach (var invoice in invoices)
        {
            if (invoice.DueDate > latestDue) latestDue = invoice.DueDate;
        }
        return latestDue;
    }
}
```

O comportamento é o mesmo. Cada função agora tem um único propósito e mais tarde pode virar uma expressão LINQ (`invoices.Sum(i => i.Amount)`).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Não misture uma otimização ou uma reescrita para pipeline no mesmo commit da divisão.
