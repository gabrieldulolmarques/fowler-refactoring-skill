# Introduzir Null Object (Introduce Null Object)

Kerievsky (2004), cap. 9, p. 301. Direção: até. Padrão: Null Object (fora do GoF; o livro credita a Bobby Woolf).

## Quando usar
Smells: Complexidade Condicional (Conditional Complexity), Código Duplicado (Duplicated Code).

- A mesma verificação de nulo no mesmo campo aparece em vários lugares, cada um com o mesmo fallback (não fazer nada, ou devolver um padrão). Um código novo que esquece a verificação ainda pode falhar com um erro de nulo.
- Um Null Object é uma instância do mesmo tipo que não faz nada ou devolve padrões inofensivos, então os chamadores sempre podem chamá-lo. O campo o referencia até que um objeto real seja atribuído.
- Ele deve encolher o código ou mantê-lo do mesmo tamanho. Se o null object acrescentar mais linhas do que as verificações que remove, não o use.
- Desvantagens: ele complica um design que tem apenas uma ou duas verificações de nulo; programadores que não o conhecem ainda podem escrever verificações que nunca disparam; e um null object baseado em subclasse precisa sobrescrever todo método público adicionado depois à sua base. Implementar uma interface evita esse último risco.
- Relação com Fowler: [introduce-special-case.md](../../fowler/conditional-logic/introduce-special-case.md) cobre o caso geral. A mecânica de Kerievsky mira um caso mais restrito e comum: uma classe tem verificações de nulo em um campo apenas porque o campo é usado antes de receber pela primeira vez um valor real.

## Mecânica
Siga [introduce-special-case.md](../../fowler/conditional-logic/introduce-special-case.md) quando a lógica de nulo existir por qualquer outro motivo (por exemplo, uma busca que não encontra nada). Para o caso de uso precoce, a classe de origem é aquela que deve ser protegida contra nulos:

1. Crie o null object: faça uma nova classe implementar a interface da classe de origem e, se essa interface ainda não existir, extraia-a antes (Extrair Interface (Extract Interface), só na 1ª ed.). A alternativa é criar uma subclasse vazia da classe de origem (Extrair Subclasse (Extract Subclass), só na 1ª ed.). Compile.
2. Para uma verificação de nulo, sobrescreva o método invocado no null object com o comportamento de fallback. Compile. Repita para as outras verificações da classe de origem.
3. Em uma classe que tem verificações de nulo, inicialize o campo com um null object no momento mais cedo possível, normalmente na construção. Deixe as atribuições existentes de objetos reais como estão; a nova atribuição apenas vem antes. Compile.
4. Remova toda verificação de nulo nesse campo na classe. Compile e teste.
5. Repita os passos 3 e 4 para cada classe que tenha a verificação.

Se muitos null objects forem criados, veja se [limit-instantiation-with-singleton.md](../protection/limit-instantiation-with-singleton.md) vale a pena, depois de medir o desempenho.

## Exemplo
Antes: um notificador é anexado quando o canal do cliente é conhecido, então cada uso verifica nulo. Veja o arquivo de Fowler para a forma geral; aqui está o caso de uso precoce.

```csharp
public interface IShipmentNotifier
{
    void Dispatched(string orderId);
    void Delivered(string orderId);
}

public class Order
{
    private readonly string _id = "A-1";
    private IShipmentNotifier? _notifier;

    public void AttachNotifier(IShipmentNotifier notifier) => _notifier = notifier;

    public void Dispatch()
    {
        if (_notifier != null)
            _notifier.Dispatched(_id);
    }

    public void Deliver()
    {
        if (_notifier != null)
            _notifier.Delivered(_id);
    }
}
```

Depois: o campo começa como um notificador que não faz nada, e as verificações desaparecem.

```csharp
public sealed class NullShipmentNotifier : IShipmentNotifier
{
    public void Dispatched(string orderId) { }
    public void Delivered(string orderId) { }
}

public class Order
{
    private readonly string _id = "A-1";
    private IShipmentNotifier _notifier = new NullShipmentNotifier();

    public void AttachNotifier(IShipmentNotifier notifier) => _notifier = notifier;

    public void Dispatch() => _notifier.Dispatched(_id);

    public void Deliver() => _notifier.Delivered(_id);
}
```

## Notas (C#)
- Com tipos de referência anuláveis ativados, o campo muda de `IShipmentNotifier?` para `IShipmentNotifier`, e o compilador então deixa de emitir alerta sobre ele.
- Prefira uma interface mais uma classe nula `sealed` em vez de subclasse, para que um novo método da interface não possa ser esquecido por herança.
- Um null object sem estado pode ser uma instância estática compartilhada (`NullShipmentNotifier.Instance`).

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhuma verificação de nulo no campo permanece, e um teste que chama os métodos antes de qualquer objeto real ser anexado passa sem exceção.
- Ninguém dependia de um null devolvido para significar "ausente"; procure chamadores que o testem.
