# Composite

Gamma et al. (1995), cap. 4, p. 163. Categoria: estrutural de objeto.

## Intenção
Organizar objetos em uma árvore de partes e todos, em que um item isolado e um grupo de itens são usados pela mesma interface.

## Quando compensa
- O domínio é uma hierarquia parte-todo (um carrinho com produtos e pacotes, pastas e arquivos, grupos de permissão aninhados) e quem chama não deve se importar se um nó é folha ou grupo.
- O código cliente fica mais simples: sem laços que testam o tipo de cada nó, e novos tipos de nó funcionam com o código existente.
- Custo: o design pode ficar genérico demais. É difícil proibir que um grupo contenha certos tipos, já que o sistema de tipos vê todo nó como do mesmo tipo. Essas regras viram verificações em tempo de execução.
- Não vale a pena quando a árvore tem uma profundidade fixa (uma lista de itens e nada aninhado), caso em que uma coleção simples é mais clara.

## Participantes em C#
- **Component** (`IPriced`): interface ou classe abstrata para todo nó. No exemplo tem uma operação, `Total()`, e o gerenciamento de filhos fica apenas no composite.
- **Leaf** (`Product`): um nó sem filhos, que implementa a operação diretamente.
- **Composite** (`Bundle`): guarda componentes filhos e implementa a operação combinando os resultados dos filhos.
- **Client** (o código em `Main`): trabalha apenas com a interface do componente ao calcular preços.

## Exemplo (C#)
Um checkout precifica produtos avulsos e pacotes. Um pacote pode conter produtos e outros pacotes, e aplica o seu próprio desconto sobre a soma dos filhos.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public interface IPriced
{
    string Name { get; }
    decimal Total();
}

public class Product : IPriced
{
    public string Name { get; }
    private readonly decimal _price;

    public Product(string name, decimal price)
    {
        Name = name;
        _price = price;
    }

    public decimal Total() => _price;
}

public class Bundle : IPriced
{
    public string Name { get; }
    private readonly decimal _discountRate;
    private readonly List<IPriced> _children = new();

    public Bundle(string name, decimal discountRate)
    {
        Name = name;
        _discountRate = discountRate;
    }

    public Bundle Add(IPriced child)
    {
        if (ReferenceEquals(child, this))
            throw new ArgumentException("A bundle cannot contain itself.");
        _children.Add(child);
        return this;
    }

    public bool Remove(IPriced child) => _children.Remove(child);

    public IEnumerable<IPriced> Children => _children;

    public decimal Total() => _children.Sum(c => c.Total()) * (1m - _discountRate);
}

public static class Program
{
    public static void Main()
    {
        var starter = new Bundle("Starter kit", 0.10m)
            .Add(new Product("Keyboard", 50m))
            .Add(new Product("Mouse", 20m));

        var cart = new Bundle("Cart", 0m)
            .Add(starter)
            .Add(new Product("Monitor", 200m));

        Console.WriteLine($"{cart.Name}: {cart.Total()}"); // 263.00
    }
}
```

## Variações
- **Onde o gerenciamento de filhos é declarado**: no componente, para que todo nó pareça igual (transparente, mas adicionar algo a uma folha não tem sentido e precisa lançar exceção), ou só no composite (seguro, já que o compilador recusa a operação, mas os clientes precisam saber quais nós podem ter filhos). O exemplo faz a escolha segura e expõe `Add` apenas em `Bundle`.
- **Folha com filhos vazios**: se o componente expõe `Children`, uma folha pode devolver uma sequência vazia, então a travessia não precisa de verificações de tipo.
- **Referências ao pai**: mantenha um vínculo com o pai em cada nó para facilitar subir ou remover. Atualize-o apenas dentro de `Add` e `Remove`, para que o vínculo e a lista de filhos nunca divirjam. Isso também impede que um nó seja compartilhado por dois pais.
- **Ordem dos filhos**: se a ordem importa (passos de um pipeline), use uma lista e projete a API de acesso para isso.
- **Cache**: um composite pode guardar em cache um resultado calculado (um total, um tamanho delimitador) e descartá-lo quando um filho muda. Isso exige um meio de os filhos avisarem o pai, por meio de vínculos com o pai ou de eventos.
- **Armazenamento**: uma lista, um array, um dicionário ou até campos nomeados por filho, quando cada composite tem um conjunto fixo de filhos.

## Riscos e alternativas em C#
- Profundidade de recursão: uma árvore muito profunda pode estourar a pilha. Percorra com uma pilha explícita ou com `yield return` quando a profundidade não for limitada.
- Ciclos: impeça que um nó seja adicionado a um dos seus próprios descendentes. O exemplo verifica apenas a auto-referência direta; verifique os ancestrais se os nós puderem ser reutilizados.
- Exponha os filhos como `IEnumerable<T>` ou `IReadOnlyList<T>`, nunca a `List<T>` interna, ou os chamadores contornam as suas invariantes.
- Para travessias que variam muito (imprimir, exportar, validar), mantenha os nós pequenos e adicione operações por um visitor ou por casamento de padrões simples em uma função, em vez de aumentar a interface do componente.
- Uma estrutura aninhada pontual, que nunca recebe novas operações, pode ser mais simples como dados puros mais uma função recursiva.

## Padrões relacionados
- [decorator.md](decorator.md): costuma ser combinado com o composite e compartilha a forma recursiva, mas acrescenta comportamento a um componente em vez de agregar vários.
- [flyweight.md](flyweight.md): permite compartilhar folhas, mas folhas compartilhadas não podem guardar referência ao pai.
- [iterator.md](../behavioral/iterator.md): percorre um composite.
- [visitor.md](../behavioral/visitor.md): mantém as operações sobre classes folha e composite em um único lugar.
- [chain-of-responsibility.md](../behavioral/chain-of-responsibility.md): o vínculo com o pai muitas vezes faz o papel da cadeia.
- [command.md](../behavioral/command.md): um comando macro é um composite de comandos.

## Verificação
- O código cliente chama `Total()` em um produto, em um pacote e em um pacote de pacotes sem verificar tipos.
- Um novo tipo de nó (por exemplo, um vale-presente) funciona nos carrinhos existentes sem editar o cliente.
- Os testes cobrem um grupo vazio, grupos aninhados e a regra que você impõe em tempo de execução (sem auto-contenção).
- A coleção interna de filhos não pode ser modificada de fora.
