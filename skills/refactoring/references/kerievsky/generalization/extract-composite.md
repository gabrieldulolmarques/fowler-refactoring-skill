# Extrair Composite (Extract Composite)

Kerievsky (2004), cap. 8, p. 214. Padrão: Composite. Direção: até.

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Várias subclasses de uma mesma hierarquia mantêm, cada uma, uma coleção de filhos vindos dessa mesma hierarquia, e cada uma repete o código que adiciona, remove e totaliza esses filhos.
- Mover esse código para uma superclasse comum reduz o tratamento duplicado de filhos, e o nome da superclasse avisa o próximo desenvolvedor que o tratamento de filhos pode ser herdado em vez de reescrito.
- Isso é Extrair Superclasse (Extract Superclass) ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md)) voltado apenas para a parte de tratamento de filhos. Feito isso, se restar comportamento compartilhado que não tem nada a ver com filhos, continue com Extrair Superclasse.

## Mecânica
1. Crie o composite: uma nova classe na hierarquia, com nome que diga o que ela contém (por exemplo `CompositeItem`). Compile.
2. Torne cada classe que mantém código duplicado de filhos (um contêiner de filhos) subclasse do composite. Compile.
3. Pegue um método de processamento de filhos que esteja duplicado, total ou parcialmente, entre os contêineres.
   - Se o nome dele difere entre os contêineres, uniformize-o com Mudar Declaração de Função (Change Function Declaration) ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)).
   - Totalmente duplicado: mova o campo de filhos que ele usa para o composite com Subir Campo (Pull Up Field) ([pull-up-field.md](../../fowler/inheritance/pull-up-field.md)), renomeando-o se o nome antigo servir a apenas um contêiner. Depois mova o método com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). Se ele depender de código do construtor nos contêineres, suba esse código para o construtor do composite com Subir Corpo do Construtor (Pull Up Constructor Body) ([pull-up-constructor-body.md](../../fowler/inheritance/pull-up-constructor-body.md)).
   - Parcialmente duplicado: primeiro tente tornar os corpos idênticos com Substituir Algoritmo (Substitute Algorithm) ([substitute-algorithm.md](../../fowler/encapsulation/substitute-algorithm.md)) e trate o método como totalmente duplicado. Caso contrário, extraia a parte comum com Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) e suba-a. Se o método tem os mesmos passos com implementações diferentes, use Formar Template Method (Form Template Method) ([form-template-method.md](form-template-method.md)).
   Compile e teste após cada passo.
4. Repita o passo 3 para cada outro método duplicado de processamento de filhos.
5. Verifique cada cliente de um contêiner: se ele puder falar com o contêiner pelo tipo do composite, troque para isso. Compile e teste.

## Exemplo
Antes: `Box` e `Pallet` mantêm, cada um, a sua própria lista de itens filhos, com o mesmo `Add` e um `Weight` quase idêntico.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class Item
{
    public abstract decimal Weight();
}

public class Crate : Item
{
    private readonly decimal _weight;
    public Crate(decimal weight) => _weight = weight;
    public override decimal Weight() => _weight;
}

public class Box : Item
{
    private readonly List<Item> _items = new();
    public void Add(Item item) => _items.Add(item);
    public override decimal Weight() => 0.5m + _items.Sum(i => i.Weight());
}

public class Pallet : Item
{
    private readonly List<Item> _contents = new();
    public void Add(Item item) => _contents.Add(item);
    public override decimal Weight() => 20m + _contents.Sum(c => c.Weight());
}
```

Depois: `CompositeItem` é dono dos filhos, do `Add` e da soma. Cada contêiner acrescenta apenas o seu próprio peso de tara.

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class Item
{
    public abstract decimal Weight();
}

public class Crate : Item
{
    private readonly decimal _weight;
    public Crate(decimal weight) => _weight = weight;
    public override decimal Weight() => _weight;
}

public abstract class CompositeItem : Item
{
    private readonly List<Item> _children = new();
    public void Add(Item item) => _children.Add(item);
    protected decimal ChildrenWeight() => _children.Sum(c => c.Weight());
}

public class Box : CompositeItem
{
    public override decimal Weight() => 0.5m + ChildrenWeight();
}

public class Pallet : CompositeItem
{
    public override decimal Weight() => 20m + ChildrenWeight();
}
```

## Notas (C#)
- Exponha os filhos como `IReadOnlyList<Item>` se subclasses ou clientes precisarem lê-los; mantenha a própria lista privada, como em Encapsular Coleção (Encapsulate Collection) ([encapsulate-collection.md](../../fowler/encapsulation/encapsulate-collection.md)).
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os totais de contêineres aninhados (uma caixa dentro de um palete) batem com os resultados antigos, e nenhum contêiner ainda declara seu próprio campo de filhos.
