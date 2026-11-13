# Substituir Código de Erro por Exceção (Replace Error Code with Exception)

Fowler (2018), só na edição web (não está no livro impresso); resumo em https://refactoring.com/catalog/replaceErrorCodeWithException.html. Nome anterior / outro nome: —. Inversa: —.
Relacionada: Substituir Exceção por Verificação Prévia (Replace Exception with Precheck) ([replace-exception-with-precheck.md](replace-exception-with-precheck.md)).

## Quando usar
Uma função reporta falha pelo seu valor de retorno: um número mágico, `null`, `false` ou um objeto de
status. Os chamadores precisam verificá-lo após cada chamada, e quem esquece deixa o programa
continuar com estado ruim. Lançar uma exceção tira o sinal do caminho normal de retorno e o deixa
chegar à camada que souber tratá-lo.

Use apenas para falhas que sejam realmente excepcionais. Se a condição é rotineira e se espera
que os chamadores ramifiquem por ela (uma busca que muitas vezes não encontra nada, uma entrada frequentemente inválida),
mantenha um resultado baseado em retorno ou ofereça uma verificação prévia; veja [replace-exception-with-precheck.md](replace-exception-with-precheck.md).

## Mecânica
1. Adicione um tratador de exceção mais acima na cadeia de chamadas, na camada que deve lidar com a
   falha. No começo ele captura e relança tudo (`catch { throw; }`), então o comportamento não
   muda. Se já existe um tratador adequado, amplie-o para cobrir o novo caminho. Compile
   e teste.
2. Escolha um jeito de distinguir as novas exceções de todas as outras. Em C#, uma classe de
   exceção própria, que carrega o que o código de erro carregava (um motivo, o valor problemático). Compile.
3. Altere o tratador para executar a ação de erro para esse tipo de exceção e deixar qualquer
   outra exceção propagar. Compile e teste.
4. Substitua cada lugar que retorna o código de erro por um `throw` da nova exceção, um de cada
   vez. Compile e teste após cada um.
5. Quando nenhum lugar retornar mais o código, remova o código que o verificava e o repassava
   pela pilha de chamadas, testando após cada mudança. Um jeito seguro é primeiro transformar cada verificação
   numa armadilha (`Debug.Fail` ou um throw) e apagá-la quando os testes mostrarem que ela nunca dispara. Limpe as
   sobras com [remove-dead-code.md](../moving-features/remove-dead-code.md).
6. Se o tipo de retorno da função existia apenas para carregar o código (um status `int`, um `bool`),
   simplifique-o, por exemplo para `void`, como um passo separado com [change-function-declaration.md](../first-set/change-function-declaration.md).

## Exemplo
Antes: `Send` retorna um código, e o chamador precisa interpretá-lo.

```csharp
using System;

public class SmsGateway
{
    private int _sentThisMinute;

    public int Send(string phone, string text)
    {
        if (!phone.StartsWith("+")) return -1;      // número inválido
        if (_sentThisMinute >= 100) return -2;      // limite de envios excedido
        _sentThisMinute++;
        return 0;
    }
}

public class NotificationService
{
    private readonly SmsGateway _gateway = new();

    public string Notify(string phone, string text)
    {
        var result = _gateway.Send(phone, text);
        if (result == -1) return "invalid number";
        if (result == -2) return "rate limit exceeded";
        return "sent";
    }
}
```

Depois: as falhas viram exceções, e o chamador as trata onde preferir.

```csharp
using System;

public class DeliveryException : Exception
{
    public DeliveryException(string message) : base(message) { }
}

public class SmsGateway
{
    private int _sentThisMinute;

    public void Send(string phone, string text)
    {
        if (!phone.StartsWith("+"))
            throw new DeliveryException("invalid number");
        if (_sentThisMinute >= 100)
            throw new DeliveryException("rate limit exceeded");
        _sentThisMinute++;
    }
}

public class NotificationService
{
    private readonly SmsGateway _gateway = new();

    public string Notify(string phone, string text)
    {
        try
        {
            _gateway.Send(phone, text);
            return "sent";
        }
        catch (DeliveryException e)
        {
            return e.Message;
        }
    }
}
```

## Notas (C#)
- Não use exceções para fluxo de controle esperado: elas são lentas em comparação com um desvio e escondem os caminhos normais do programa. Reserve-as para falhas que o chamador não consegue razoavelmente evitar verificando antes.
- Prefira um tipo de exceção específico (ou um embutido, como `ArgumentException` ou `InvalidOperationException`, quando couber) em vez de um `Exception` genérico, e capture o tipo mais restrito possível.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Adicione um teste por antigo código de erro que verifique se a exceção é lançada com os dados certos.
- Procure chamadores fora da solução (reflexão, outros assemblies) que ainda esperem o código.
