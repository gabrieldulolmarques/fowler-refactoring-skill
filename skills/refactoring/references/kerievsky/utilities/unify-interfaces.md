# Unificar Interfaces (Unify Interfaces)

Kerievsky (2004), cap. 11, p. 343. Padrão: —. Direção: —.

## Quando usar
Smells: Código Duplicado (Duplicated Code) (a contracapa interna do livro lista Unificar Interfaces com Adapter (Unify Interfaces with Adapter) ali; este utilitário é o passo de baixo nível em que ela se apoia).

- Uma superclasse ou interface não tem métodos públicos que uma subclasse tem, então o código não consegue tratar todos da mesma forma e recorre a verificações de tipo ou casts.
- Adicione os métodos que faltam ao tipo base, com comportamento vazio (null) em uma classe, para que a subclasse possa sobrescrevê-los e os chamadores possam usar o tipo base em qualquer lugar.
- O livro precisou disso duas vezes: quando um Decorator precisava da mesma interface da classe que embeleza ([move-embellishment-to-decorator.md](../simplification/move-embellishment-to-decorator.md)), e quando um Visitor precisava que suas fontes o aceitassem polimorficamente ([move-accumulation-to-visitor.md](../accumulation/move-accumulation-to-visitor.md)).
- Muitas vezes é um passo temporário. Refatorações posteriores podem permitir remover de novo os métodos acrescentados, ou você pode extrair uma interface independente, para que os implementadores não herdem os campos da classe base.

## Mecânica
Para cada *método faltante*, ou seja, um método público na subclasse que a superclasse ou interface não declara:

1. Adicione uma cópia do método à superclasse ou interface. Na superclasse, dê a ele um corpo que não faz nada, ou que devolve um padrão inofensivo. Compile.
2. Repita até que os dois compartilhem a mesma interface pública.
3. Teste tudo que usa a superclasse.

## Exemplo
Antes: só a subclasse expressa pode notificar o cliente, então um laço sobre os envios precisa verificar o tipo.

```csharp
public interface ICustomerNotifier { void Send(string message); }

public class Shipment
{
    public string Id { get; init; } = "";
    public virtual decimal Cost() => 5m;
}

public class ExpressShipment : Shipment
{
    public override decimal Cost() => 15m;
    public void Notify(ICustomerNotifier notifier) => notifier.Send($"Shipment {Id} is on its way");
}
```

Depois: `Notify` é declarado na classe base com comportamento nulo e sobrescrito na subclasse, então os chamadores usam apenas `Shipment`.

```csharp
public class Shipment
{
    public string Id { get; init; } = "";
    public virtual decimal Cost() => 5m;
    public virtual void Notify(ICustomerNotifier notifier) { }
}

public class ExpressShipment : Shipment
{
    public override decimal Cost() => 15m;
    public override void Notify(ICustomerNotifier notifier) => notifier.Send($"Shipment {Id} is on its way");
}

public static class Demo
{
    public static void NotifyAll(IEnumerable<Shipment> shipments, ICustomerNotifier notifier)
    {
        foreach (var s in shipments) s.Notify(notifier);
    }
}
```

## Notas (C#)
- O método base precisa ser `virtual` (ou `abstract`) e o método da subclasse `override`. Um método da subclasse com o mesmo nome sem `override` oculta o da base, e `Notify` por uma referência de `Shipment` não faria nada.
- Para uma interface, adicionar um membro quebra todos os implementadores existentes. Métodos de interface com implementação padrão (C# 8) permitem adicioná-lo com corpo, mas só são acessíveis pelo tipo interface, não pela classe.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As verificações de tipo ou casts que a unificação devia remover podem ser apagadas agora, e os testes que usam só o tipo base passam para cada subclasse.
