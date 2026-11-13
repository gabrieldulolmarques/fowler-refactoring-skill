# Encapsular Composite com Builder (Encapsulate Composite with Builder)

Kerievsky (2004), cap. 6, p. 96. Direção: até (Builder); longe (Composite). Padrão: Builder (GoF, p. 97).

## Quando usar
Smells: Obsessão por Primitivos (Primitive Obsession), Código Duplicado (Duplicated Code).

- Construir um Composite leva sempre os mesmos três passos: criar um nó, configurá-lo e anexá-lo ao pai certo. Pular o último passo, ou anexar ao pai errado, é um erro fácil, e o código fica repetitivo.
- O código cliente fica preso às classes do Composite. Quando a biblioteca de árvore subjacente muda, todo lugar que constrói uma árvore precisa mudar. Um Builder que recebe argumentos simples (strings, números) e não devolve nenhum tipo da biblioteca esconde isso. Depois você pode escrever outro Builder com a mesma interface para uma representação diferente.
- A intenção do GoF é permitir que um mesmo processo de construção gere representações diferentes. Simplificar a construção e desacoplar o cliente são razões igualmente boas.
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
Antes: uma árvore de menu montada à mão. Cada nó é criado, adicionado ao pai, e o pai atual é rastreado em variáveis locais.

```csharp
public class MenuItem
{
    public string Title { get; }
    public List<MenuItem> Children { get; } = new();
    public MenuItem(string title) { Title = title; }

    public string Render(int depth = 0) =>
        new string(' ', depth * 2) + Title + "\n" + string.Concat(Children.Select(c => c.Render(depth + 1)));
}

var root = new MenuItem("File");
var open = new MenuItem("Open");
root.Children.Add(open);
var recent = new MenuItem("Recent");
open.Children.Add(recent);
var exit = new MenuItem("Exit");
root.Children.Add(exit);
var text = root.Render();
```

Depois: `MenuBuilder` mantém o caminho da raiz até o nó atual. Os clientes passam apenas títulos e leem o resultado no final.

```csharp
public class MenuBuilder
{
    private readonly MenuItem _root;
    private readonly Stack<MenuItem> _path = new();

    public MenuBuilder(string rootTitle)
    {
        _root = new MenuItem(rootTitle);
        _path.Push(_root);
    }

    public MenuBuilder AddChild(string title)
    {
        var item = new MenuItem(title);
        _path.Peek().Children.Add(item);
        _path.Push(item);
        return this;
    }

    public MenuBuilder AddSibling(string title)
    {
        Up();
        return AddChild(title);
    }

    public MenuBuilder Up()
    {
        if (_path.Count == 1) throw new InvalidOperationException("Already at the root.");
        _path.Pop();
        return this;
    }

    public MenuItem Build() => _root;
}

var text = new MenuBuilder("File")
    .AddChild("Open")
    .AddChild("Recent")
    .Up()
    .AddSibling("Exit")
    .Build()
    .Render();
```

A árvore é a mesma. `Up` depois de `Recent` volta para `Open`, e `AddSibling("Exit")` então sobe mais uma vez e adiciona sob `File`.

## Notas (C#)
- Devolver `this` em cada método permite encadeamento. Se você quiser impedir que os chamadores usem uma árvore pela metade, faça `Build` devolver um resultado imutável, ou faça o builder de uso único.
- Se os clientes não deveriam conhecer o tipo do nó, dê ao builder uma interface e devolva uma interface a partir de `Build`.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- A saída do builder é igual à árvore antiga montada à mão para a mesma entrada (compare a forma renderizada ou serializada).
- Nenhum código cliente fora do builder referencia o construtor de nó do Composite ou sua coleção de filhos.
