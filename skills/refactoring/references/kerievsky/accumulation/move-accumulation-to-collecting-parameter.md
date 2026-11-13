# Mover Acumulação para Collecting Parameter (Move Accumulation to Collecting Parameter)

Kerievsky (2004), cap. 10, p. 313. Padrão: Collecting Parameter. Direção: até.

## Quando usar
Smells: Método Longo (Long Method).

- Um método volumoso constrói um resultado em uma variável local (uma string, uma lista, um relatório parcial). Para dividi-lo em métodos pequenos, cada pedaço precisa de um lugar para colocar o que encontra.
- Em vez de cada método extraído devolver um pedaço que o chamador precisa combinar, passe o objeto de resultado para cada um deles e deixe que acrescentem a ele. O objeto que reúne os dados é o Collecting Parameter.
- Combina naturalmente com Compor Método (Compose Method) ([compose-method.md](../simplification/compose-method.md)): o método de acumulação acaba sendo três coisas: criar o resultado, passá-lo adiante e ler de volta.
- Também funciona com vários objetos, por exemplo recursivamente sobre um Composite: cada nó acrescenta os seus próprios dados ao mesmo parâmetro.
- Benefícios: métodos menores e mais simples, e às vezes código mais rápido (um buffer em vez de muitas concatenações).
- Limite: serve para classes específicas com uma interface conhecida. Quando os dados vêm de muitas classes sem relação entre si, com interfaces diferentes, [move-accumulation-to-visitor.md](move-accumulation-to-visitor.md) pode ser mais limpo, mas experimente este primeiro, porque um Visitor é mais difícil de construir.

## Mecânica
1. Encontre o método de acumulação e a variável local que guarda o resultado. Se o tipo dela não pode ser construído ao longo de várias chamadas (uma string imutável, por exemplo), troque-o por um que possa, como um `StringBuilder`. Compile.
2. Escolha um passo de acumulação e aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) para movê-lo para um método privado que devolve `void` e recebe o resultado como parâmetro, escrevendo nele. Compile e teste.
3. Repita o passo 2 para cada passo. O método original agora deve apenas criar o resultado, passá-lo aos métodos extraídos e ler o valor final. Compile e teste.

Quando um passo também produz um valor que o chamador precisa (um subtotal, por exemplo), o método extraído pode devolver esse valor também. O resultado que está sendo construído continua passando pelo parâmetro.

## Exemplo
Antes: um método monta o texto CSV, concatenando em uma string enquanto também calcula o total.

```csharp
using System.Collections.Generic;

public class ExportRow
{
    public string Id { get; }
    public string Label { get; }
    public decimal Amount { get; }

    public ExportRow(string id, string label, decimal amount)
    {
        Id = id;
        Label = label;
        Amount = amount;
    }
}

public class ExportBatch
{
    public string Name { get; }
    public IReadOnlyList<ExportRow> Rows { get; }
    public decimal Fee { get; }

    public ExportBatch(string name, IReadOnlyList<ExportRow> rows, decimal fee)
    {
        Name = name;
        Rows = rows;
        Fee = fee;
    }
}

public class CsvExporter
{
    public string Export(ExportBatch batch)
    {
        var text = "";
        text += $"# {batch.Name}\n";
        text += "id,label,amount\n";
        decimal total = 0m;
        foreach (var row in batch.Rows)
        {
            text += $"{row.Id},{row.Label},{row.Amount:F2}\n";
            total += row.Amount;
        }
        if (batch.Fee > 0m)
        {
            text += $"fee,,-{batch.Fee:F2}\n";
            total -= batch.Fee;
        }
        text += $"total,,{total:F2}\n";
        return text;
    }
}
```

Depois: o `StringBuilder` é criado uma vez e passado a cada passo. Os passos que também contribuem para o total devolvem um valor.

```csharp
using System.Text;

public class CsvExporter
{
    public string Export(ExportBatch batch)
    {
        var text = new StringBuilder();
        WriteHeader(batch, text);
        var total = WriteRows(batch, text);
        total -= WriteFee(batch, text);
        text.Append($"total,,{total:F2}\n");
        return text.ToString();
    }

    private static void WriteHeader(ExportBatch batch, StringBuilder text)
    {
        text.Append($"# {batch.Name}\n");
        text.Append("id,label,amount\n");
    }

    private static decimal WriteRows(ExportBatch batch, StringBuilder text)
    {
        decimal total = 0m;
        foreach (var row in batch.Rows)
        {
            text.Append($"{row.Id},{row.Label},{row.Amount:F2}\n");
            total += row.Amount;
        }
        return total;
    }

    private static decimal WriteFee(ExportBatch batch, StringBuilder text)
    {
        if (batch.Fee <= 0m) return 0m;
        text.Append($"fee,,-{batch.Fee:F2}\n");
        return batch.Fee;
    }
}
```

## Notas (C#)
- `string` é imutável, então o passo 1 normalmente significa `StringBuilder`. Para listas, um `ICollection<T>` ou `List<T>` passado como parâmetro funciona do mesmo jeito.
- Quando o parâmetro só recebe texto, um parâmetro `TextWriter` permite que o chamador escolha o destino (uma string, um arquivo, um stream) e evita um `ToString()` final.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A saída é byte a byte igual à anterior para alguns casos representativos, incluindo os casos vazio e com taxa.
