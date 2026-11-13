# Encapsular Composite com Builder (Encapsulate Composite with Builder)

Kerievsky (2004), cap. 6, p. 96. Padrão: Builder. Direção: até (Builder); longe (Composite).

## Quando usar
Smells: Obsessão por Primitivos (Primitive Obsession), Código Duplicado (Duplicated Code).

- Construir um Composite leva sempre os mesmos três passos: criar um nó, configurá-lo e anexá-lo ao pai certo. Pular o último passo, ou anexar ao pai errado, é um erro fácil, e o código fica repetitivo.
- O código cliente fica preso às classes do Composite. Quando a biblioteca de árvore subjacente muda, todo lugar que constrói uma árvore precisa mudar. Um Builder que recebe argumentos simples (strings, números) e não devolve nenhum tipo da biblioteca esconde isso. Depois você pode escrever outro Builder com a mesma interface para uma representação diferente.
- A intenção original do padrão é permitir que um mesmo processo de construção gere representações diferentes. Simplificar a construção e desacoplar o cliente são razões igualmente boas.
- Desvantagem: a interface de um Builder às vezes não é óbvia, porque esconde muito trabalho (posição atual, rastreamento do pai). Seus testes ou sua documentação podem ser a melhor forma de aprendê-la.
- Relacionado: o próprio Composite pode vir de [replace-implicit-tree-with-composite.md](../simplification/replace-implicit-tree-with-composite.md). A direção "longe de Composite" significa que os clientes deixam de tocar diretamente no Composite.

## Mecânica
Não há um conjunto único de mecânica: Builders para Composites podem ser projetados de muitas maneiras. Estes são os passos gerais. O livro sugere construir o Builder começando pelos testes.
1. Crie a classe builder. Faça-a capaz de produzir um Composite de um só nó e adicione um método para obter o resultado. Compile e teste.
2. Faça-a capaz de construir filhos. Isso geralmente significa alguns métodos para criar um nó e posicioná-lo (adicionar um filho do nó atual, adicionar um irmão, voltar um nível). Compile e teste.
3. Se o código que você está substituindo define atributos ou valores nos nós, deixe o builder defini-los também. Compile e teste.
4. Veja quão simples é de usar, e simplifique.
5. Troque o código que constrói o Composite para usar o builder. O cliente passa a ser o Director do padrão. Compile e teste.

## Exemplo
Antes: uma árvore de rotas montada à mão. Cada nó é criado, adicionado ao pai, e o pai atual é guardado em variáveis locais.

```csharp
using System.Collections.Generic;
using System.Linq;

public class RouteNode
{
    public string Segment { get; }
    public List<RouteNode> Children { get; } = new();
    public RouteNode(string segment) { Segment = segment; }

    public string Render(int depth = 0) =>
        new string(' ', depth * 2) + Segment + "\n" + string.Concat(Children.Select(c => c.Render(depth + 1)));
}

public static class Caller
{
    public static string BuildText()
    {
        var root = new RouteNode("api");
        var v1 = new RouteNode("v1");
        root.Children.Add(v1);
        var users = new RouteNode("users");
        v1.Children.Add(users);
        var orders = new RouteNode("orders");
        v1.Children.Add(orders);
        var health = new RouteNode("health");
        root.Children.Add(health);
        return root.Render();
    }
}
```

Depois: `RouteBuilder` guarda o caminho da raiz até o nó atual. Os clientes passam apenas nomes de segmento e leem o resultado no fim.

```csharp
using System;
using System.Collections.Generic;

public class RouteBuilder
{
    private readonly RouteNode _root;
    private readonly Stack<RouteNode> _path = new();

    public RouteBuilder(string rootSegment)
    {
        _root = new RouteNode(rootSegment);
        _path.Push(_root);
    }

    public RouteBuilder AddChild(string segment)
    {
        var node = new RouteNode(segment);
        _path.Peek().Children.Add(node);
        _path.Push(node);
        return this;
    }

    public RouteBuilder AddSibling(string segment)
    {
        Up();
        return AddChild(segment);
    }

    public RouteBuilder Up()
    {
        if (_path.Count == 1) throw new InvalidOperationException("Already at the root.");
        _path.Pop();
        return this;
    }

    public RouteNode Build() => _root;
}

public static class Caller
{
    public static string BuildText() =>
        new RouteBuilder("api")
            .AddChild("v1")
            .AddChild("users")
            .AddSibling("orders")
            .Up()
            .AddSibling("health")
            .Build()
            .Render();
}
```

A árvore é a mesma. `AddSibling("orders")` sobe de `users` e adiciona em `v1`. O `Up` seguinte deixa `orders` para `v1`, e `AddSibling("health")` sobe mais uma vez e adiciona em `api`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A saída do builder é igual à da árvore montada à mão para a mesma entrada (compare a forma renderizada ou serializada).
- Nenhum código cliente fora do builder referencia o construtor do nó do Composite nem a sua coleção de filhos.
