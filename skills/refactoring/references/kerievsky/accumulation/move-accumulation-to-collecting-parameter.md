# Mover Acumulação para Collecting Parameter (Move Accumulation to Collecting Parameter)

Kerievsky (2004), cap. 10, p. 313. Direção: até. Padrão: Collecting Parameter (fora do GoF; o livro credita a Kent Beck, Smalltalk Best Practice Patterns).

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
Antes: um método monta o texto, concatenando em uma string enquanto também calcula o total.

```csharp
public record Line(string Sku, int Qty, decimal UnitPrice);
public record Invoice(string Number, string Customer, IReadOnlyList<Line> Lines, decimal Discount);

public class InvoiceRenderer
{
    public string Render(Invoice invoice)
    {
        var text = "";
        text += $"Invoice {invoice.Number}\n";
        text += $"Customer: {invoice.Customer}\n";
        decimal total = 0m;
        foreach (var line in invoice.Lines)
        {
            var amount = line.Qty * line.UnitPrice;
            text += $"{line.Sku} x{line.Qty} = {amount:F2}\n";
            total += amount;
        }
        if (invoice.Discount > 0m)
        {
            text += $"Discount: -{invoice.Discount:F2}\n";
            total -= invoice.Discount;
        }
        text += $"Total: {total:F2}\n";
        return text;
    }
}
```

Depois: o `StringBuilder` é criado uma vez e passado a cada passo. Os passos que também contribuem para o total devolvem um valor.

```csharp
using System.Text;

public class InvoiceRenderer
{
    public string Render(Invoice invoice)
    {
        var text = new StringBuilder();
        WriteHeader(invoice, text);
        var total = WriteLines(invoice, text);
        total -= WriteDiscount(invoice, text);
        text.Append($"Total: {total:F2}\n");
        return text.ToString();
    }

    private static void WriteHeader(Invoice invoice, StringBuilder text)
    {
        text.Append($"Invoice {invoice.Number}\n");
        text.Append($"Customer: {invoice.Customer}\n");
    }

    private static decimal WriteLines(Invoice invoice, StringBuilder text)
    {
        decimal total = 0m;
        foreach (var line in invoice.Lines)
        {
            var amount = line.Qty * line.UnitPrice;
            text.Append($"{line.Sku} x{line.Qty} = {amount:F2}\n");
            total += amount;
        }
        return total;
    }

    private static decimal WriteDiscount(Invoice invoice, StringBuilder text)
    {
        if (invoice.Discount <= 0m) return 0m;
        text.Append($"Discount: -{invoice.Discount:F2}\n");
        return invoice.Discount;
    }
}
```

## Notas (C#)
- `string` é imutável, então o passo 1 geralmente significa `StringBuilder`. Para listas, um `ICollection<T>` ou `List<T>` passado como argumento funciona do mesmo modo.
- Quando o parâmetro só recebe texto, um parâmetro `TextWriter` permite que o chamador escolha o destino (uma string, um arquivo, um stream) e evita um `ToString()` final.
- Um método que acrescenta ao seu parâmetro tem efeito colateral; nomeie os métodos extraídos como `Write...` ou `Append...` para deixar isso visível.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A saída é byte a byte igual à anterior para algumas entradas representativas, incluindo os casos vazio e com desconto.
