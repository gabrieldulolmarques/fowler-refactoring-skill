# Substituir Despachante Condicional por Command (Replace Conditional Dispatcher with Command)

Kerievsky (2004), cap. 7, p. 191. Direção: até, rumo a. Padrão: Command (GoF, p. 233).

## Quando usar
Smells: Comandos Switch (Switch Statements), Classe Grande (Large Class), Método Longo (Long Method).

- Um despachante condicional é um `switch` ou uma cadeia de `if` que roteia uma requisição (um nome de comando, um tipo de mensagem, um código de ação) para o código que a trata. Um pequeno, que cabe na tela, com handlers curtos, pode ficar como está.
- Dois motivos para migrar para Command: o conjunto de requisições ou de handlers precisa ser configurável em tempo de execução (o `switch` fixo no código não pode ser estendido de fora), ou o despachante e seus handlers cresceram tanto que extrair métodos já não ajuda, porque a classe continua grande demais.
- Cada handler vira uma classe de comando com um método de execução comum. Um mapa do nome da requisição para a instância do comando substitui o `switch`, e a classe antiga passa a ser o invocador.
- Command também abre espaço para desfazer, enfileirar ou registrar operações depois, mas não construa isso antes de precisar: esta refatoração é fácil de fazer quando a necessidade aparecer.
- Desvantagem: complica o design quando um despachante simples bastaria.

## Mecânica
1. Na classe que guarda o despachante, pegue o código que trata uma requisição e aplique [extract-function.md](../first-set/extract-function.md) até que um método execute esse comportamento: o método de execução. Compile e teste.
2. Faça o mesmo com as demais requisições.
3. Aplique [extract-class.md](../encapsulation/extract-class.md) a cada método de execução, para que cada handler seja uma classe: um comando concreto. O método de execução geralmente precisará ser público. Se o método for longo, aplique [compose-method.md](compose-method.md). Compile e teste. Quando todos estiverem prontos, procure duplicação entre os comandos e, se encontrar, aplique [form-template-method.md](../generalization/form-template-method.md).
4. Defina o tipo de comando (uma interface ou classe abstrata) com a única assinatura de execução que todos os comandos compartilham. Para escolhê-la, compare os comandos concretos:
   - quais dados precisam ser passados ao método comum?
   - quais poderiam ser dados ao construtor de cada comando?
   - quais o comando poderia buscar chamando de volta um parâmetro?
   - qual é a assinatura mais simples que serve a todos?

   Você pode começar aplicando [extract-superclass.md](../inheritance/extract-superclass.md) ou Extrair Interface (Extract Interface; só na 1ª ed.; sem link) a um comando concreto. Compile.
5. Faça cada comando concreto implementar o tipo de comando, e faça todo o código cliente usá-los por meio dele. Compile e teste.
6. Na classe do despachante, crie e preencha um mapa de comandos: um dicionário de instâncias de comando indexado pelo identificador da requisição. Se houver tantos comandos que registrá-los dá uma lista longa, carregue-os de uma configuração (o padrão Plugin, de *Patterns of Enterprise Application Architecture*, de Fowler). Compile.
7. Substitua o despacho condicional por uma busca no mapa seguida de uma chamada ao método de execução do comando. A classe agora é o invocador. Compile e teste.

## Exemplo
Antes: um único `switch` faz o roteamento e o trabalho de todos os handlers.

```csharp
using System.Globalization;

public class Order
{
    public int Id { get; init; }
    public string Status { get; set; } = "new";
    public string? Carrier { get; set; }
    public decimal Refunded { get; set; }
}

public class OrderDesk
{
    public string Execute(string command, Order order, string[] args)
    {
        switch (command)
        {
            case "ship":
                order.Carrier = args[0];
                order.Status = "shipped";
                return $"order {order.Id} shipped with {order.Carrier}";
            case "cancel":
                if (order.Status == "shipped")
                    return $"order {order.Id} already shipped";
                order.Status = "cancelled";
                return $"order {order.Id} cancelled";
            case "refund":
                var amount = decimal.Parse(args[0], CultureInfo.InvariantCulture);
                order.Refunded += amount;
                return $"order {order.Id} refunded {amount}";
            case "invoice":
                return $"invoice for order {order.Id}";
            default:
                return $"unknown command {command}";
        }
    }
}
```

Depois: cada requisição é uma classe de comando, e a mesa é um invocador com um mapa. Novos comandos podem ser registrados em tempo de execução, até de outro assembly. O mapa mantém a busca exata de antes (troque o comparador de propósito, não como efeito colateral).

```csharp
using System.Collections.Generic;
using System.Globalization;

public class Order
{
    public int Id { get; init; }
    public string Status { get; set; } = "new";
    public string? Carrier { get; set; }
    public decimal Refunded { get; set; }
}

public interface IOrderCommand
{
    string Execute(Order order, string[] args);
}

public class ShipCommand : IOrderCommand
{
    public string Execute(Order order, string[] args)
    {
        order.Carrier = args[0];
        order.Status = "shipped";
        return $"order {order.Id} shipped with {order.Carrier}";
    }
}

public class CancelCommand : IOrderCommand
{
    public string Execute(Order order, string[] args)
    {
        if (order.Status == "shipped")
            return $"order {order.Id} already shipped";
        order.Status = "cancelled";
        return $"order {order.Id} cancelled";
    }
}

public class RefundCommand : IOrderCommand
{
    public string Execute(Order order, string[] args)
    {
        var amount = decimal.Parse(args[0], CultureInfo.InvariantCulture);
        order.Refunded += amount;
        return $"order {order.Id} refunded {amount}";
    }
}

public class InvoiceCommand : IOrderCommand
{
    public string Execute(Order order, string[] args) => $"invoice for order {order.Id}";
}

public class OrderDesk
{
    private readonly Dictionary<string, IOrderCommand> _commands = new()
    {
        ["ship"] = new ShipCommand(),
        ["cancel"] = new CancelCommand(),
        ["refund"] = new RefundCommand(),
        ["invoice"] = new InvoiceCommand(),
    };

    public void Register(string name, IOrderCommand command) => _commands[name] = command;

    public string Execute(string command, Order order, string[] args) =>
        _commands.TryGetValue(command, out var handler)
            ? handler.Execute(order, args)
            : $"unknown command {command}";
}
```

## Notas (C#)
- Onde os handlers são minúsculos, um `Dictionary<string, Func<Order, string[], string>>` é um tipo de comando mais leve do que uma classe por handler. Passe para classes quando um handler precisar de estado, dependências ou testes próprios.
- Com injeção de dependência, injete `IEnumerable<IOrderCommand>` e deixe cada comando expor seu nome, em vez de uma longa lista de registro.
- Os argumentos chegam como `string[]` aqui porque a assinatura antiga era assim; um objeto de requisição tipado por comando fica para um passo posterior.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Mantenha um teste para cada nome roteado, um para o nome desconhecido e (após o passo 7) um que registra um novo comando em tempo de execução e o executa.
- Confirme que nenhum handler guardou referência aos campos privados do despachante: os comandos devem receber o que precisam pelos argumentos.
