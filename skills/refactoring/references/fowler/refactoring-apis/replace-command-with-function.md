# Substituir Comando por Função (Replace Command with Function)

Fowler (2018), cap. 11, p. 344. Nome anterior / outro nome: —. Inversa: Substituir Função por Comando (Replace Function with Command)
([replace-function-with-command.md](replace-function-with-command.md)).

## Quando usar
Converta quando a classe apenas recebe as suas entradas, executa uma computação e retorna o resultado,
e a lógica é simples o bastante para ser lida como uma função (ou algumas funções pequenas). Não converta
quando os chamadores dependem de desfazer, enfileiramento, vários pontos de entrada ou configuração incremental.

## Mecânica
1. Extraia uma função que envolva a criação do comando e a chamada ao seu método execute ([extract-function.md](../first-set/extract-function.md)). Esta será a função substituta, e os chamadores agora passam por ela.
2. Para cada função auxiliar que o método execute chama, internalize-a no método execute ([inline-function.md](../first-set/inline-function.md)). Se a auxiliar retorna um valor, primeiro extraia essa chamada para uma variável ([extract-variable.md](../first-set/extract-variable.md)), depois internalize.
3. Mude a assinatura do método execute para que ele receba todos os parâmetros do construtor ([change-function-declaration.md](../first-set/change-function-declaration.md)). Atualize a função invólucro (wrapper) para passá-los.
4. No método execute, substitua cada uso de um campo pelo parâmetro correspondente, um campo de cada vez, testando após cada um. Remova também a atribuição do campo no construtor, para que um uso esquecido falhe de forma evidente. O construtor e os seus campos agora estão mortos, mas permanecem até que o passo 7 apague a classe.
5. Internalize a chamada ao construtor e a chamada a execute na função invólucro, para que ela contenha a lógica diretamente.
6. Teste.
7. Apague a classe de comando agora sem uso ([remove-dead-code.md](../moving-features/remove-dead-code.md)).

## Exemplo
Antes:

```csharp
public class Channel
{
    public Channel(decimal pricePerMessage) => PricePerMessage = pricePerMessage;
    public decimal PricePerMessage { get; }
}

public class Surcharge
{
    public Surcharge(decimal fee) => Fee = fee;
    public decimal Fee { get; }
}

public class BatchCostCalculator
{
    private readonly Channel _channel;
    private readonly int _messages;
    private readonly Surcharge _surcharge;

    public BatchCostCalculator(Channel channel, int messages, Surcharge surcharge)
    {
        _channel = channel;
        _messages = messages;
        _surcharge = surcharge;
    }

    private decimal Subtotal() => _channel.PricePerMessage * _messages;

    public decimal Execute()
    {
        return Subtotal() + _surcharge.Fee;
    }
}

// chamador
// decimal cost = new BatchCostCalculator(channel, messages, surcharge).Execute();
```

Passo 1, envolva a chamada:

```csharp
public static class Billing
{
    public static decimal BatchCost(Channel channel, int messages, Surcharge surcharge)
        => new BatchCostCalculator(channel, messages, surcharge).Execute();
}
```

Passos 2 a 4: `Subtotal` internalizado, parâmetros movidos para `Execute`, campos que não são mais usados. O invólucro estático do passo 1 fica na mesma classe ou em uma classe auxiliar estática, e agora chama `new BatchCostCalculator(channel, messages, surcharge).Execute(channel, messages, surcharge)`. O construtor ainda recebe seus três argumentos, mas não os armazena mais; ele desaparece junto com a classe no passo 7:

```csharp
public class BatchCostCalculator
{
    public BatchCostCalculator(Channel channel, int messages, Surcharge surcharge) { }

    public decimal Execute(Channel channel, int messages, Surcharge surcharge)
    {
        var subtotal = channel.PricePerMessage * messages;
        return subtotal + surcharge.Fee;
    }
}
```

Passos 5 a 7: a lógica é internalizada no invólucro, e a classe é apagada:

```csharp
public static class Billing
{
    public static decimal BatchCost(Channel channel, int messages, Surcharge surcharge)
    {
        var subtotal = channel.PricePerMessage * messages;
        return subtotal + surcharge.Fee;
    }
}

// chamador
// decimal cost = Billing.BatchCost(channel, messages, surcharge);
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
