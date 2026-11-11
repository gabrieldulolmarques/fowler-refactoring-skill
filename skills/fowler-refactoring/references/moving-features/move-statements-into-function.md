# Mover Instruções para Função (Move Statements into Function)

Fowler (2018), cap. 8, p. 213. Antes / também: —. Inversa: Mover Instruções para os Chamadores (Move Statements to Callers)
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
Dois métodos imprimem as linhas de contato de um cliente. Cada um imprime o nome do cliente logo antes de
chamar `PrintContact`.

Antes:

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);

public class StatementPrinter
{
    public IEnumerable<string> PrintInvoiceHeader(Customer customer)
    {
        var lines = new List<string> { "INVOICE" };
        lines.Add($"customer: {customer.Name}");
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    public IEnumerable<string> PrintReminder(Customer customer)
    {
        var lines = new List<string> { "PAYMENT REMINDER" };
        lines.Add($"customer: {customer.Name}");
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    private IEnumerable<string> PrintContact(Customer customer)
    {
        yield return $"email: {customer.Email}";
        yield return $"phone: {customer.Phone}";
    }
}
```

Após o passo 3, `PrintInvoiceHeader` chama uma `PrintCustomerAndContact(customer)` temporária, cujo
corpo é a linha do nome seguida da chamada a `PrintContact`; `PrintReminder` ainda tem sua própria linha de nome
e a chamada a `PrintContact`. Os passos 4 e 5 atualizam `PrintReminder` e internalizam `PrintContact`, e
o passo 6 renomeia a função temporária para `PrintContact`. Depois:

```csharp
using System.Collections.Generic;

public record Customer(string Name, string Email, string Phone);

public class StatementPrinter
{
    public IEnumerable<string> PrintInvoiceHeader(Customer customer)
    {
        var lines = new List<string> { "INVOICE" };
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    public IEnumerable<string> PrintReminder(Customer customer)
    {
        var lines = new List<string> { "PAYMENT REMINDER" };
        lines.AddRange(PrintContact(customer));
        return lines;
    }

    private IEnumerable<string> PrintContact(Customer customer)
    {
        yield return $"customer: {customer.Name}";
        yield return $"email: {customer.Email}";
        yield return $"phone: {customer.Phone}";
    }
}
```

A saída dos dois métodos não muda.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Busque o nome provisório para confirmar que ele sumiu.
- Confirme que nenhum chamador ainda executa por conta própria as instruções movidas.
- Compare a saída de cada chamador antes e depois da mudança.
