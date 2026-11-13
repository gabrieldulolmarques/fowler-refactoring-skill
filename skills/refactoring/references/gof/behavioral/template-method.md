# Template Method

Gamma et al. (1995), cap. 5, p. 325. Categoria: comportamental de classe.

## Intenção
Escrever o esqueleto de um algoritmo uma única vez em uma classe base e deixar algumas etapas para as subclasses. As subclasses preenchem as etapas sem poder mudar a ordem nem a estrutura do todo.

## Quando compensa
- A parte fixa de um algoritmo deve morar em um só lugar, e só as partes que variam devem ser escritas pelas subclasses.
- As subclasses repetem a mesma sequência de etapas com detalhes diferentes. Encontre as diferenças, mova cada uma para o seu próprio método e substitua a sequência duplicada por um único template method que chama esses métodos.
- Você quer permitir extensão apenas em pontos escolhidos (hooks) e manter o restante fechado.
- Benefícios: reuso da parte invariante; a classe base controla o fluxo ("não nos chame, nós chamaremos você"); um conjunto pequeno e documentado de pontos de extensão.
- Custos: quem escreve subclasses precisa aprender quais métodos sobrescrever; o design fica preso à herança, então é fixado em tempo de compilação e cada subclasse tem uma única classe base; etapas abstratas demais tornam a subclasse trabalhosa.
- Não vale a pena quando a variação pode ser passada como objeto ou delegate, ou quando há apenas uma implementação.

## Participantes em C#
- **AbstractClass** (`ReportExporter`): define o template method (`Export`, não virtual) e as etapas que ele chama. Membros abstratos são as etapas que uma subclasse deve fornecer; membros virtuais com corpo vazio ou padrão são os hooks.
- **ConcreteClass** (`CsvExporter`, `JsonExporter`): sobrescreve as etapas abstratas e os hooks de que precisa.

## Exemplo (C#)
A exportação de um relatório grava uma lista de linhas de vendas em CSV ou JSON. A ordem é sempre: cabeçalho, linhas com separadores, rodapé. O formato decide como cada parte se parece.

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

public class SaleRow
{
    public SaleRow(int id, string customer, decimal total)
    {
        Id = id;
        Customer = customer;
        Total = total;
    }

    public int Id { get; }
    public string Customer { get; }
    public decimal Total { get; }
}

public abstract class ReportExporter
{
    // Template method: ordem fixa, não sobrescrevível.
    public string Export(IReadOnlyList<SaleRow> rows)
    {
        if (rows is null) throw new ArgumentNullException(nameof(rows));

        var sb = new StringBuilder();
        WriteHeader(sb);
        for (int i = 0; i < rows.Count; i++)
        {
            if (i > 0) sb.Append(Separator);
            WriteRow(sb, rows[i]);
        }
        WriteFooter(sb);
        return sb.ToString();
    }

    // Operação primitiva: todo formato precisa fornecê-la.
    protected abstract void WriteRow(StringBuilder sb, SaleRow row);

    // Hooks: implementações padrão que um formato pode substituir.
    protected virtual string Separator => "";
    protected virtual void WriteHeader(StringBuilder sb) { }
    protected virtual void WriteFooter(StringBuilder sb) { }

    protected static string Money(decimal value) => value.ToString("0.00", CultureInfo.InvariantCulture);
}

public class CsvExporter : ReportExporter
{
    protected override string Separator => "\n";

    protected override void WriteHeader(StringBuilder sb) => sb.Append("id,customer,total\n");

    protected override void WriteRow(StringBuilder sb, SaleRow row) =>
        sb.Append(row.Id).Append(',').Append(Quote(row.Customer)).Append(',').Append(Money(row.Total));

    private static string Quote(string text) => "\"" + text.Replace("\"", "\"\"") + "\"";
}

public class JsonExporter : ReportExporter
{
    protected override string Separator => ",\n";

    protected override void WriteHeader(StringBuilder sb) => sb.Append("[\n");

    protected override void WriteFooter(StringBuilder sb) => sb.Append("\n]");

    protected override void WriteRow(StringBuilder sb, SaleRow row) =>
        sb.Append("  {\"id\":").Append(row.Id)
          .Append(",\"customer\":\"").Append(row.Customer.Replace("\\", "\\\\").Replace("\"", "\\\""))
          .Append("\",\"total\":").Append(Money(row.Total)).Append('}');
}

public static class Program
{
    public static void Main()
    {
        var rows = new List<SaleRow> { new(1, "Ana", 19.9m), new(2, "Bruno \"B\"", 5m) };

        foreach (ReportExporter exporter in new ReportExporter[] { new CsvExporter(), new JsonExporter() })
            Console.WriteLine(exporter.Export(rows));
    }
}
```

## Variações
- **Tipos de etapa.** Um template method pode chamar operações concretas da própria classe, auxiliares destinados às subclasses (`Money`), etapas abstratas que precisam ser sobrescritas (`WriteRow`), métodos de fábrica que criam partes, e hooks que podem ser sobrescritos (`WriteHeader`).
- **Deixe clara a diferença.** Deixe claro quais membros devem ser sobrescritos (abstract) e quais podem ser (virtual, geralmente com corpo vazio). Um prefixo de nome como `Do` ou `On` ajuda quem lê.
- **Poucas primitivas.** Mantenha pequeno o número de etapas abstratas. Cada etapa extra é mais uma coisa que cada subclasse precisa escrever.
- **Proteja o esqueleto.** Deixe o template method não virtual e torne as etapas `protected`, para que só o template as chame. É assim que uma classe base garante um invariante, como "adquirir um recurso, executar a etapa, sempre liberar".
- **Transformar uma sobrescrita em hook.** Se as subclasses precisam chamar a versão base de um método sobrescrito para estar corretas, transforme-o em um template method com hook, para que a classe base mantenha o controle e as subclasses não possam esquecer a chamada.

## Riscos e alternativas em C#
- Se as etapas variáveis são poucas, passe-as como delegates ou uma pequena interface para uma única classe (por exemplo, `Func<SaleRow, string>` para o formato da linha, mais as strings de cabeçalho e rodapé). Isso é Strategy: pode mudar em tempo de execução e não exige hierarquia.
- Herança acopla as subclasses aos detalhes internos da classe base. Mudar a ordem das etapas ou adicionar uma chamada no template pode quebrar subclasses que dependiam da ordem antiga. Documente o contrato de cada etapa.
- Membros `virtual` chamados a partir de um construtor base rodam antes de o construtor da subclasse terminar. Não chame etapas sobrescrevíveis a partir de construtores.
- Etapas assíncronas: faça as etapas retornarem `Task` e o template ser `async`. Um hook `async void` esconde falhas; retorne `Task`.
- Não declare o template como `virtual`. Uma subclasse que sobrescreve o template remove a garantia que o padrão oferece. Métodos em C# já são não virtuais por padrão; use `sealed override` se uma classe intermediária herdar um template de cima.

## Padrões relacionados
- [Factory Method](../creational/factory-method.md): frequentemente chamado por template methods, como uma das etapas.
- [Strategy](strategy.md): delegação em vez de herança. Uma estratégia substitui o algoritmo inteiro; um template method substitui partes dele.

## Verificação
- A ordem das etapas aparece em exatamente um lugar, o template method, e nenhuma subclasse a reimplementa.
- Cada subclasse sobrescreve apenas as etapas abstratas e os hooks de que precisa, e o arquivo se lê como "o que é diferente neste formato".
- Adicionar uma nova variante não exige mudança na classe base.
- Chamar uma etapa diretamente de fora não é possível (as etapas são `protected`), então o invariante não pode ser pulado.
