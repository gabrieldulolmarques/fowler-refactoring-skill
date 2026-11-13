# Formar Template Method (Form Template Method)

Kerievsky (2004), cap. 8, p. 205. Direção: até. Padrão: Template Method (GoF, p. 325).

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Duas subclasses implementam o mesmo método, e ambas seguem os mesmos passos na mesma ordem, mas os passos em si diferem. O esqueleto do algoritmo é copiado em cada subclasse.
- Mover o esqueleto para a superclasse deixa cada subclasse apenas com os passos que realmente variam, e a ordem dos passos fica declarada uma única vez.
- A refatoração de Fowler de mesmo nome é a mesma ideia; a versão de Kerievsky serve ao caso em que o esqueleto compartilhado está escondido dentro dos corpos, e não já visível como instruções repetidas.
- Não use quando as subclasses precisariam implementar muitos métodos pequenos só para preencher o esqueleto: a hierarquia fica mais difícil de ler do que a duplicação que removeu. Mantenha pequeno o número de passos abstratos e torne os passos opcionais ganchos (hooks) concretos.

## Mecânica
1. Encontre um método semelhante: duas subclasses que executam passos parecidos, numa ordem parecida. Aplique Compor Método (Compose Method) ([compose-method.md](../simplification/compose-method.md)) a ele nas duas subclasses, para que cada passo seja um método. Passos com a mesma assinatura e o mesmo corpo nas duas são métodos idênticos; passos que diferem são métodos únicos. Quando não souber qual é o tipo de um passo, pergunte se as subclasses devem herdá-lo (idêntico) ou sobrescrevê-lo (único).
2. Suba os métodos idênticos com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). Compile e teste.
3. Faça o corpo do método semelhante ficar igual nas duas subclasses: renomeie cada método único para que as duas subclasses chamem os mesmos nomes, com Mudar Declaração de Função (Change Function Declaration) ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)). Compile e teste após cada renomeação.
4. Se a assinatura do método semelhante ainda não for idêntica, altere-a do mesmo modo.
5. Suba o método semelhante de uma subclasse e apague-o da outra. Declare um método abstrato na superclasse para cada método único (ou um `virtual`, quando faz sentido ter um padrão). O método agora subido é o template. Compile e teste.

## Exemplo
Antes: dois exportadores repetem a mesma sequência (cabeçalho, uma linha por pedido, rodapé), cada um com a sua formatação.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, string Customer, decimal Total);

public abstract class OrderExporter
{
    public abstract string Export(IReadOnlyList<Order> orders);
}

public class CsvOrderExporter : OrderExporter
{
    public override string Export(IReadOnlyList<Order> orders)
    {
        var sb = new StringBuilder();
        sb.AppendLine("id,customer,total");
        foreach (var o in orders)
            sb.AppendLine($"{o.Id},{o.Customer},{o.Total}");
        sb.AppendLine($"count={orders.Count}");
        return sb.ToString();
    }
}

public class TextOrderExporter : OrderExporter
{
    public override string Export(IReadOnlyList<Order> orders)
    {
        var sb = new StringBuilder();
        sb.AppendLine("ORDERS");
        foreach (var o in orders)
            sb.AppendLine($"{o.Id} for {o.Customer}: {o.Total}");
        sb.AppendLine($"count={orders.Count}");
        return sb.ToString();
    }
}
```

Depois: a superclasse é dona da sequência e do rodapé idêntico. Cada subclasse escreve apenas o seu cabeçalho e a sua linha.

```csharp
using System.Collections.Generic;
using System.Text;

public record Order(string Id, string Customer, decimal Total);

public abstract class OrderExporter
{
    public string Export(IReadOnlyList<Order> orders)
    {
        var sb = new StringBuilder();
        WriteHeader(sb);
        foreach (var o in orders)
            WriteRow(sb, o);
        WriteFooter(sb, orders.Count);
        return sb.ToString();
    }

    protected abstract void WriteHeader(StringBuilder sb);
    protected abstract void WriteRow(StringBuilder sb, Order order);
    protected virtual void WriteFooter(StringBuilder sb, int count) => sb.AppendLine($"count={count}");
}

public class CsvOrderExporter : OrderExporter
{
    protected override void WriteHeader(StringBuilder sb) => sb.AppendLine("id,customer,total");
    protected override void WriteRow(StringBuilder sb, Order o) => sb.AppendLine($"{o.Id},{o.Customer},{o.Total}");
}

public class TextOrderExporter : OrderExporter
{
    protected override void WriteHeader(StringBuilder sb) => sb.AppendLine("ORDERS");
    protected override void WriteRow(StringBuilder sb, Order o) => sb.AppendLine($"{o.Id} for {o.Customer}: {o.Total}");
}
```

## Notas (C#)
- `Export` não é `virtual`, então uma subclasse não consegue substituir a sequência por acidente. Um método que nunca foi virtual é o equivalente em C# do `final` do template em Java.
- Marque os passos obrigatórios como `abstract` e os opcionais como `virtual`, com um padrão útil (o rodapé acima). Use `protected` em ambos, já que quem chama só deve ver o template.
- Se a variação for de um ou dois pequenos passos, passar delegates ou um objeto Strategy para um único método costuma ser mais leve do que uma hierarquia.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A saída de cada subclasse é byte a byte igual à anterior (compare as strings em um teste), inclusive a ordem dos passos.
