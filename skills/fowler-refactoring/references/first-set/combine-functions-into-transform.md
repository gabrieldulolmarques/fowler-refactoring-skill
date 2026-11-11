# Combinar Funções em Transformação (Combine Functions into Transform)

Fowler (2018), cap. 6, p. 149. Antes / também: —. Inversa: —. Alternativa:
Combinar Funções em Classe (Combine Functions into Class) ([combine-functions-into-class.md](combine-functions-into-class.md)).

## Quando usar
Smells: Cirurgia com Espingarda (Shotgun Surgery), Dados Mutáveis (Mutable Data).

- Vários clientes derivam valores (um total, uma cobrança, um status) do mesmo registro de origem, e
  as fórmulas são repetidas ou ficam em auxiliares que ninguém conhece.
- Você quer um só lugar para consultar e alterar cada derivação: a transformação.
- Os dados de origem são somente leitura na prática (um relatório, um view model, uma entrada que só é lida).

Não use quando os clientes modificam a origem depois da transformação. Os campos derivados são
armazenados na cópia, então uma mudança posterior na origem os deixa desatualizados. Nesse caso use
Combinar Funções em Classe, em que os valores derivados são calculados sob demanda.

Escolha entre transformação e classe principalmente pelo estilo que a base de código já usa, com essa
única exceção.

## Mecânica
1. Crie uma função de transformação que receba o registro de origem e devolva uma cópia com os mesmos
   valores. Faça a cópia profunda se o registro guardar dados aninhados mutáveis.
2. Adicione um teste de que a transformação não altera o registro recebido.
3. Escolha uma derivação. Se a lógica dela ainda não for uma função, aplique antes Extrair Função (Extract Function).
4. Mova o corpo para a transformação, de modo que ele preencha um novo campo na cópia. Mova também qualquer auxiliar de que o
   corpo precise, ou torne-o acessível a partir da transformação.
5. Faça um cliente chamar a transformação e ler o novo campo em vez de calcular.
6. Compile e teste.
7. Repita os passos 3 a 6 para cada derivação restante e cada cliente restante. Uma derivação
   que se apoia em outra deve ler o campo da outra.
8. Quando nenhum cliente chamar mais o auxiliar antigo, apague-o ou aninhe-o na transformação. Internalize
   as variáveis que agora só copiam um campo.

## Exemplo
Antes: dois lugares calculam o mesmo subtotal.

```csharp
using System;

public record Order(string Customer, int Units, decimal UnitPrice, int Year);

public static class Reports
{
    private static decimal TaxFreeAllowance(int year) => year >= 2024 ? 100m : 50m;

    public static decimal InvoiceTotal(Order order)
    {
        var subtotal = order.Units * order.UnitPrice;
        return subtotal;
    }

    public static decimal TaxDue(Order order)
    {
        var subtotal = order.Units * order.UnitPrice;
        var taxable = Math.Max(0, subtotal - TaxFreeAllowance(order.Year));
        return taxable * 0.2m;
    }
}
```

Depois: uma transformação guarda as duas derivações; os clientes leem campos.

```csharp
using System;

public record Order(string Customer, int Units, decimal UnitPrice, int Year);

public record EnrichedOrder(
    string Customer, int Units, decimal UnitPrice, int Year,
    decimal Subtotal, decimal TaxableAmount);

public static class OrderEnricher
{
    private static decimal TaxFreeAllowance(int year) => year >= 2024 ? 100m : 50m;

    public static EnrichedOrder Enrich(Order order)
    {
        var subtotal = order.Units * order.UnitPrice;
        var taxable = Math.Max(0, subtotal - TaxFreeAllowance(order.Year));
        return new EnrichedOrder(
            order.Customer, order.Units, order.UnitPrice, order.Year,
            subtotal, taxable);
    }
}

public static class Reports
{
    public static decimal InvoiceTotal(Order order) => OrderEnricher.Enrich(order).Subtotal;

    public static decimal TaxDue(Order order) => OrderEnricher.Enrich(order).TaxableAmount * 0.2m;
}
```

O comportamento é o mesmo. As fórmulas agora vivem em `Enrich`; um novo valor derivado é mais um
campo ali. Se o tipo enriquecido deve estender `Order` em vez de repetir seus campos, torne
`Order` um record não selado e derive dele. O record derivado recebe a origem em um construtor de cópia
(`EnrichedOrder(Order o, decimal subtotal, decimal taxable) : base(o)`), porque uma
expressão `with` em um `Order` devolve um `Order`, não um `EnrichedOrder`.

## Notas de C#
- Esta refatoração é idiomática em JavaScript. Em C#, a transformação costuma ser uma função que
  devolve um novo `record` enriquecido (construído com um construtor, ou um construtor de cópia quando
  deriva do record de origem; `with` só serve quando o tipo enriquecido é o mesmo tipo),
  de modo que o original nunca é mutado e nenhuma cópia profunda é necessária.
- Records são rasos: se a origem guarda coleções ou objetos mutáveis, copie-os também.
- Se os dados forem mutados, ou as derivações precisarem do comportamento do objeto, prefira
  Combinar Funções em Classe.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A transformação deixa sua entrada inalterada (o teste do passo 2).
