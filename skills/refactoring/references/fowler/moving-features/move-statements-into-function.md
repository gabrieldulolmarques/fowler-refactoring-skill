# Mover Instruções para Função (Move Statements into Function)

Fowler (2018), cap. 8, p. 213. Nome anterior / outro nome: —. Inversa: Mover Instruções para os Chamadores (Move Statements to Callers)
([move-statements-to-callers.md](move-statements-to-callers.md)).

## Quando usar
- Toda chamada a uma função vem acompanhada das mesmas instruções, logo antes ou logo depois dela.
- Essas instruções são mais fáceis de entender como parte da função do que como algo de que cada
  chamador precisa se lembrar.
- Movê-las significa que uma mudança futura acontece em um só lugar, em vez de um por chamador.

Pule quando as instruções não pertencem de fato à função, mas ainda assim precisam rodar com ela.
Nesse caso, extraia uma nova função que envolva as instruções e a chamada (os mesmos passos
abaixo, menos a internalização e a renomeação). Pule também quando os chamadores já diferem, ou provavelmente vão diferir;
se um comportamento compartilhado precisar começar a variar, a refatoração inversa é a ferramenta.

## Mecânica
1. Garanta que as instruções estejam diretamente ao lado da chamada; se não estiverem, use Deslocar Instruções (Slide Statements)
   ([slide-statements.md](slide-statements.md)) para juntá-las.
2. Com um único chamador, basta recortar as instruções para o corpo da função, executar os testes e parar.
3. Com vários chamadores, escolha um e aplique Extrair Função (Extract Function)
   ([extract-function.md](../first-set/extract-function.md)) às instruções junto com a chamada. Dê
   à nova função um nome provisório que você possa buscar depois.
4. Substitua as instruções e a chamada antiga em cada outro chamador por uma chamada à nova função,
   executando os testes após cada substituição.
5. Quando nenhum chamador usar mais a função original, aplique Internalizar Função (Inline Function)
   ([inline-function.md](../first-set/inline-function.md)) para incorporá-la à nova e então apague-a.
6. Use Mudar Declaração de Função (Change Function Declaration)
   ([change-function-declaration.md](../first-set/change-function-declaration.md)) para renomear a nova função
   para o nome original, ou um melhor.

## Exemplo
Dois métodos imprimem o bloco de endereço de uma remessa. Cada um imprime o nome do destinatário logo antes de chamar `PrintAddress`.

Antes:

```csharp
using System.Collections.Generic;

public class Recipient
{
    public Recipient(string name, string street, string city)
    {
        Name = name;
        Street = street;
        City = city;
    }

    public string Name { get; }
    public string Street { get; }
    public string City { get; }
}

public class LabelPrinter
{
    public IEnumerable<string> PrintShippingLabel(Recipient recipient)
    {
        var lines = new List<string> { "SHIPPING LABEL" };
        lines.Add($"recipient: {recipient.Name}");
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    public IEnumerable<string> PrintDeliveryReceipt(Recipient recipient)
    {
        var lines = new List<string> { "DELIVERY RECEIPT" };
        lines.Add($"recipient: {recipient.Name}");
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    private IEnumerable<string> PrintAddress(Recipient recipient)
    {
        yield return $"street: {recipient.Street}";
        yield return $"city: {recipient.City}";
    }
}
```

Depois do passo 3, `PrintShippingLabel` chama um `PrintRecipientAndAddress(recipient)` temporário, cujo corpo é a linha do nome seguida da chamada a `PrintAddress`; `PrintDeliveryReceipt` ainda tem sua própria linha de nome e sua própria chamada a `PrintAddress`. Os passos 4 e 5 atualizam `PrintDeliveryReceipt` e internalizam `PrintAddress`, e o passo 6 renomeia a função temporária para `PrintAddress`. Depois:

```csharp
using System.Collections.Generic;

public class LabelPrinter
{
    public IEnumerable<string> PrintShippingLabel(Recipient recipient)
    {
        var lines = new List<string> { "SHIPPING LABEL" };
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    public IEnumerable<string> PrintDeliveryReceipt(Recipient recipient)
    {
        var lines = new List<string> { "DELIVERY RECEIPT" };
        lines.AddRange(PrintAddress(recipient));
        return lines;
    }

    private IEnumerable<string> PrintAddress(Recipient recipient)
    {
        yield return $"recipient: {recipient.Name}";
        yield return $"street: {recipient.Street}";
        yield return $"city: {recipient.City}";
    }
}
```

A saída dos dois métodos não muda.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Procure o nome provisório para confirmar que ele sumiu.
- Confirme que nenhum chamador ainda executa por conta própria as instruções movidas.
- Compare a saída de cada chamador antes e depois da mudança.
