# Mover Conhecimento de Criação para Factory (Move Creation Knowledge to Factory)

Kerievsky (2004), cap. 6, p. 68. Direção: até. Padrão: Factory (fora do GoF).

## Quando usar
Smells: Solução Espalhada (Solution Sprawl).

- Os dados e o código necessários para construir um tipo de objeto estão espalhados por várias classes. O livro chama isso de espalhamento de criação (creation sprawl). Geralmente começa quando um cliente quer configurar um objeto mas não consegue alcançar o código que o cria; então ele entrega suas preferências a um objeto, que as entrega a outro, até que alguma classe distante finalmente as use.
- Uma Factory reúne a lógica de criação e as preferências em uma única classe. O cliente configura a factory uma vez, e a mesma instância da factory depois faz a criação onde for necessário.
- A definição do livro: qualquer classe que tenha um ou mais Creation Methods é uma Factory, estática ou não, devolvendo uma interface, uma classe abstrata ou uma classe concreta. Um Factory Method (GoF) é outra coisa, um método polimórfico em uma hierarquia. Uma Abstract Factory é uma Factory que pode ser trocada em tempo de execução para construir uma família de objetos relacionados. Se a lógica de criação da Factory ficar complexa demais, ela pode evoluir para uma.
- Uma Factory pode ser uma classe ou uma interface implementada por uma classe existente. A forma de interface é útil quando outro código deve conversar com essa classe apenas pelo seu papel de criação.
- Desvantagem: uma Factory acrescenta uma classe. Se todo objeto do sistema é criado por uma factory, há classes demais. Não acrescente uma só para esconder a escolha entre duas classes concretas em um único lugar. Ela precisa eliminar o espalhamento ou permitir uma configuração que o `new` puro não consegue.

## Mecânica
Estes passos supõem que a Factory é uma classe. Uma interface precisa de pequenas mudanças.
1. O *instanciador* é a classe que colabora com outras para criar o *produto*. Garanta que ele crie o produto por meio de um Creation Method ([replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md)), alterando a classe do produto se necessário. Compile e teste.
2. Crie a classe factory, com nome derivado do que ela cria (`OrderFactory`). Compile.
3. Mova o Creation Method para a factory com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)). Se era estático, torne-o um método de instância agora. Compile.
4. Faça o instanciador criar a factory e chamá-la para obter o produto. Repita para cada instanciador que deixou de compilar. Compile e teste.
5. Procure dados e métodos nas outras classes que existam apenas para alimentar a criação. Mova-os para a factory com Mover Campo (Move Field) ([move-field.md](../../fowler/moving-features/move-field.md)) e Mover Função, o que também pode mudar quem cria a factory. Compile e teste após cada movimento.

## Exemplo
Antes: `CheckoutPage` conhece as opções do pedido, passa-as para `CheckoutService`, que apenas as copia para o pedido que cria. As duas classes carregam os mesmos dois campos.

```csharp
public class Order
{
    public string Customer { get; }
    public Order(string customer) { Customer = customer; }
    public string? Note { get; set; }
    public bool Express { get; set; }
}

public class CheckoutPage
{
    private readonly bool _express;
    private readonly string _note;
    public CheckoutPage(bool express, string note) { _express = express; _note = note; }
    public Order Submit(string customer) => new CheckoutService(_express, _note).Place(customer);
}

public class CheckoutService
{
    private readonly bool _express;
    private readonly string _note;
    public CheckoutService(bool express, string note) { _express = express; _note = note; }
    public Order Place(string customer) => new Order(customer) { Note = _note, Express = _express };
}
```

Depois: `OrderFactory` guarda as opções e constrói o pedido. A página a configura uma vez. O serviço não sabe mais quais são as opções.

```csharp
public class OrderFactory
{
    private readonly bool _express;
    private readonly string _note;
    public OrderFactory(bool express, string note) { _express = express; _note = note; }
    public Order CreateOrder(string customer) => new(customer) { Note = _note, Express = _express };
}

public class CheckoutPage
{
    private readonly OrderFactory _factory;
    public CheckoutPage(bool express, string note) { _factory = new OrderFactory(express, note); }
    public Order Submit(string customer, CheckoutService service) => service.Place(customer, _factory);
}

public class CheckoutService
{
    public Order Place(string customer, OrderFactory factory) => factory.CreateOrder(customer);
}
```

## Notas (C#)
- Se outro código deve depender apenas do papel de criação, extraia uma interface (`IOrderFactory`) e deixe a classe implementá-la.
- Com injeção de dependência, a factory costuma ser registrada como serviço. A refatoração continua a mesma: mova o conhecimento primeiro, depois decida como a factory é fornecida.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As opções agora ficam em uma só classe. Uma busca pelos campos que antes eram copiados entre classes encontra apenas a factory.
- A factory elimina espalhamento real. Se ela apenas envolve um único `new`, desfaça.
