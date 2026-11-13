# Mover Instruções para os Chamadores (Move Statements to Callers)

Fowler (2018), cap. 8, p. 217. Antes / também: —. Inversa: Mover Instruções para Função (Move Statements into Function) ([move-statements-into-function.md](move-statements-into-function.md)).

## Quando usar
- Uma função que era uma unidade coesa agora agrupa duas coisas diferentes, e a fronteira da abstração está no lugar errado.
- O comportamento compartilhado por vários chamadores agora precisa diferir em um ou mais deles. Mova a parte variável para fora para que cada chamador possa alterá-la livremente.
- Preparação típica: use [slide-statements.md](slide-statements.md) para levar as instruções variáveis ao início ou ao fim da função e depois movê-las para os chamadores.
- Não serve quando a fronteira precisa de um redesenho completo. Nesse caso, internalize a função ([inline-function.md](../first-set/inline-function.md)) e depois desloque e extraia novas funções para traçar fronteiras melhores.

## Mecânica
1. Caso simples (um ou dois chamadores, uma função pequena): recorte a primeira ou a última instrução da função, cole em cada chamador, ajuste nomes ou argumentos conforme necessário, faça o build e teste. Pronto.
2. Caso contrário, use [extract-function.md](../first-set/extract-function.md) nas instruções que permanecem na função. Dê à função extraída um nome temporário fácil de buscar. Faça o build e teste.
3. Se a função for sobrescrita em subclasses, extraia o mesmo restante em cada override até que os métodos restantes sejam idênticos, então apague os overrides e mantenha um.
4. Internalize a função original ([inline-function.md](../first-set/inline-function.md)) em um chamador. Faça o build e teste. Repita para cada chamador.
5. Apague a função original quando não restar nenhum chamador.
6. Dê à função extraída seu nome final: o nome antigo da função apagada, ou um mais claro se você tiver ([change-function-declaration.md](../first-set/change-function-declaration.md)). Faça o build e teste.

## Exemplo
Antes: `PrintInvoice` e `PrintReminder` chamam ambos `WriteSummary`, que termina com a data de vencimento. Os lembretes precisam mostrar a data de vencimento de outro jeito.

```csharp
using System;
using System.IO;

public record Invoice(string Number, decimal Total, DateTime DueDate);

public static class InvoicePrinter
{
    public static void PrintInvoice(TextWriter output, Invoice invoice)
    {
        output.WriteLine("INVOICE");
        WriteSummary(output, invoice);
    }

    public static void PrintReminder(TextWriter output, Invoice invoice)
    {
        output.WriteLine("REMINDER");
        WriteSummary(output, invoice);
    }

    private static void WriteSummary(TextWriter output, Invoice invoice)
    {
        output.WriteLine($"Number: {invoice.Number}");
        output.WriteLine($"Total: {invoice.Total:C}");
        output.WriteLine($"Due: {invoice.DueDate:d}");
    }
}
```

Passo 2: extraia o que fica (nome temporário `ZzTmp`), depois internalize `WriteSummary` em cada chamador e apague-a. Passo 6: renomeie `ZzTmp` de volta para `WriteSummary`.

Depois: a linha da data de vencimento agora vive nos chamadores, e o lembrete pode alterá-la.

```csharp
using System;
using System.IO;

public record Invoice(string Number, decimal Total, DateTime DueDate);

public static class InvoicePrinter
{
    public static void PrintInvoice(TextWriter output, Invoice invoice)
    {
        output.WriteLine("INVOICE");
        WriteSummary(output, invoice);
        output.WriteLine($"Due: {invoice.DueDate:d}");
    }

    public static void PrintReminder(TextWriter output, Invoice invoice)
    {
        output.WriteLine("REMINDER");
        WriteSummary(output, invoice);
        output.WriteLine($"Due: {invoice.DueDate:d}");
    }

    private static void WriteSummary(TextWriter output, Invoice invoice)
    {
        output.WriteLine($"Number: {invoice.Number}");
        output.WriteLine($"Total: {invoice.Total:C}");
    }
}
```

O comportamento não muda neste ponto. A próxima mudança (um formato diferente de data de vencimento no lembrete) agora toca apenas `PrintReminder`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
