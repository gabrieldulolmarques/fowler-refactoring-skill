# Command

Gamma et al. (1995), cap. 5, p. 233. Também conhecido como: Action, Transaction. Categoria: comportamental de objeto.

## Intenção
Transformar uma requisição em um objeto. Isso permite passar requisições como valores, parametrizar quem chama com elas, enfileirá-las ou registrá-las em log, e desfazê-las.

## Quando compensa
- Um objeto precisa disparar uma ação sem saber o que ela faz nem sobre quem atua (botões, itens de menu, agendadores, filas de trabalho). Um objeto de comando substitui o callback.
- Requisições precisam ser enfileiradas, executadas depois, registradas em log, reexecutadas após uma falha ou enviadas a outro processo.
- Você precisa de desfazer e refazer: o comando guarda o que precisa para se reverter, e uma lista de histórico dá vários níveis.
- Benefícios: o invocador fica desacoplado do receptor, os comandos são objetos de primeira classe, eles se compõem em macros, e novos comandos não exigem mudança nas classes existentes.
- Passivo: uma classe por ação pode ser pesado. Para um callback simples, que não precisa de desfazer nem de dados, um delegate basta.

## Participantes em C#
- **Command** (`ICartCommand`): interface com `Execute` e, se houver suporte a desfazer, `Undo`.
- **ConcreteCommand** (`AddItemCommand`, `ApplyCouponCommand`, `MacroCommand`): liga um receptor a uma ação, guarda os argumentos e os dados necessários para desfazer.
- **Receiver** (`Cart`): sabe executar o trabalho real.
- **Invoker** (`CartHistory`): executa os comandos e mantém o histórico para desfazer e refazer.
- **Client** (`Program`): cria os comandos concretos e os entrega ao invocador.

## Exemplo (C#)
Um carrinho de compras online cujas alterações podem ser desfeitas. O invocador guarda os comandos executados em uma pilha; cada comando captura o que precisa para se reverter.

```csharp
using System;
using System.Collections.Generic;

public class Cart
{
    private readonly Dictionary<string, int> _quantities = new();

    public string? Coupon { get; set; }

    public int QuantityOf(string sku) => _quantities.TryGetValue(sku, out var q) ? q : 0;

    public void SetQuantity(string sku, int quantity)
    {
        if (quantity <= 0) _quantities.Remove(sku);
        else _quantities[sku] = quantity;
    }
}

public interface ICartCommand
{
    void Execute();
    void Undo();
}

public class AddItemCommand : ICartCommand
{
    private readonly Cart _cart;
    private readonly string _sku;
    private readonly int _amount;
    private int _previous;

    public AddItemCommand(Cart cart, string sku, int amount)
    {
        _cart = cart;
        _sku = sku;
        _amount = amount;
    }

    public void Execute()
    {
        _previous = _cart.QuantityOf(_sku);   // state needed to reverse exactly
        _cart.SetQuantity(_sku, _previous + _amount);
    }

    public void Undo() => _cart.SetQuantity(_sku, _previous);
}

public class ApplyCouponCommand : ICartCommand
{
    private readonly Cart _cart;
    private readonly string _code;
    private string? _previous;

    public ApplyCouponCommand(Cart cart, string code)
    {
        _cart = cart;
        _code = code;
    }

    public void Execute()
    {
        _previous = _cart.Coupon;
        _cart.Coupon = _code;
    }

    public void Undo() => _cart.Coupon = _previous;
}

public class MacroCommand : ICartCommand
{
    private readonly List<ICartCommand> _commands;

    public MacroCommand(IEnumerable<ICartCommand> commands) => _commands = new List<ICartCommand>(commands);

    public void Execute()
    {
        foreach (var command in _commands) command.Execute();
    }

    public void Undo()
    {
        for (int i = _commands.Count - 1; i >= 0; i--) _commands[i].Undo(); // reverse order
    }
}

public class CartHistory
{
    private readonly Stack<ICartCommand> _done = new();
    private readonly Stack<ICartCommand> _undone = new();

    public void Run(ICartCommand command)
    {
        command.Execute();
        _done.Push(command);
        _undone.Clear();   // a new action invalidates the redo branch
    }

    public void Undo()
    {
        if (_done.Count == 0) return;
        var command = _done.Pop();
        command.Undo();
        _undone.Push(command);
    }

    public void Redo()
    {
        if (_undone.Count == 0) return;
        var command = _undone.Pop();
        command.Execute();
        _done.Push(command);
    }
}

public static class Program
{
    public static void Main()
    {
        var cart = new Cart();
        var history = new CartHistory();

        history.Run(new AddItemCommand(cart, "sku-1", 2));
        history.Run(new MacroCommand(new ICartCommand[]
        {
            new AddItemCommand(cart, "sku-2", 1),
            new ApplyCouponCommand(cart, "WELCOME10"),
        }));

        history.Undo();   // removes sku-2 and the coupon together
        Console.WriteLine($"{cart.QuantityOf("sku-1")} {cart.QuantityOf("sku-2")} {cart.Coupon ?? "none"}");
    }
}
```

## Variações
- **Quão inteligente é o comando.** Em uma ponta, ele apenas liga um receptor a uma chamada. Na outra, faz todo o trabalho sozinho, sem receptor, o que serve a ações que não se encaixam em nenhuma classe existente.
- **Desfazer e refazer.** O comando guarda o receptor, os argumentos e os valores anteriores do receptor. Um nível precisa apenas do último comando; vários níveis exigem uma lista de histórico cujo tamanho máximo é o número de níveis.
- **Copiar antes de guardar.** Se um mesmo objeto de comando é reutilizado em muitas invocações e seu estado muda a cada vez, guarde uma cópia no histórico, e não o objeto compartilhado. Se o estado nunca muda após a execução, mantenha a referência.
- **Evitar desvio.** Desfazer e refazer repetidamente pode acumular pequenos erros. Guarde o estado anterior exato (um snapshot), em vez de recalcular uma operação inversa, quando a exatidão importar.
- **Comandos macro.** Um composto de comandos. Seu desfazer deve executar as partes em ordem inversa.
- **Registro para recuperação.** Comandos que podem ser serializados podem ser gravados em log e reexecutados após uma falha.

## Riscos e alternativas em C#
- Se não há desfazer nem dados a carregar, um delegate (`Action`, `Func<Task>`) é o comando. Use uma classe apenas quando precisar de estado, desfazer, nome ou serialização.
- Um comando que guarda um snapshot em vez de um delta usa mais memória. Limite o tamanho do histórico.
- Comandos em uma fila que rodam depois podem encontrar o receptor em outro estado. Faça-os verificar as pré-condições em `Execute`.
- Comandos `async`: retorne `Task` de `ExecuteAsync` e decida o que desfazer significa se a ação já saiu do processo (um e-mail não pode ser "desenviado"; modele um comando compensatório).
- Bibliotecas de requisição/handler que despacham objetos `IRequest` para handlers aplicam a mesma ideia, com o handler no papel de receptor.

## Padrões relacionados
- [Composite](../structural/composite.md): implementa comandos macro.
- [Memento](memento.md): guarda o estado que um comando precisa para desfazer seu efeito.
- [Prototype](../creational/prototype.md): um comando que precisa ser copiado antes de entrar na lista de histórico atua como protótipo.
- [Chain of Responsibility](chain-of-responsibility.md): comandos são frequentemente as requisições que percorrem uma cadeia.

## Verificação
- Executar e depois desfazer um comando deixa o receptor exatamente como estava, para cada comando e para uma macro.
- O invocador compila sem referências a comandos ou receptores concretos.
- Desfazer, refazer e desfazer de novo leva a um estado consistente (sem desvio).
- Adicionar uma nova ação significa adicionar uma classe e nenhuma edição no invocador ou no histórico.
