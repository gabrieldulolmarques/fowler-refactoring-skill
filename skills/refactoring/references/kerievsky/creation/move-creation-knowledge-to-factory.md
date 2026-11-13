# Mover Conhecimento de Criação para Factory (Move Creation Knowledge to Factory)

Kerievsky (2004), cap. 6, p. 68. Padrão: Factory. Direção: até.

## Quando usar
Smells: Solução Espalhada (Solution Sprawl).

- Os dados e o código necessários para construir um tipo de objeto estão espalhados por várias classes. O livro chama isso de espalhamento de criação (creation sprawl). Geralmente começa quando um cliente quer configurar um objeto mas não consegue alcançar o código que o cria; então ele entrega suas preferências a um objeto, que as entrega a outro, até que alguma classe distante finalmente as use.
- Uma Factory reúne a lógica de criação e as preferências em uma única classe. O cliente configura a factory uma vez, e a mesma instância da factory depois faz a criação onde for necessário.
- A definição do livro: qualquer classe que tenha um ou mais Creation Methods é uma Factory, estática ou não, devolvendo uma interface, uma classe abstrata ou uma classe concreta. Um Factory Method é outra coisa, um método polimórfico em uma hierarquia. Uma Abstract Factory é uma Factory que pode ser trocada em tempo de execução para construir uma família de objetos relacionados. Se a lógica de criação da Factory ficar complexa demais, ela pode evoluir para uma.
- Uma Factory pode ser uma classe ou uma interface implementada por uma classe existente. A forma de interface é útil quando outro código deve conversar com essa classe apenas pelo seu papel de criação.
- Desvantagem: uma Factory acrescenta uma classe. Se todo objeto do sistema é criado por uma factory, há classes demais. Não acrescente uma só para esconder a escolha entre duas classes concretas em um único lugar. Ela precisa eliminar o espalhamento ou permitir uma configuração que o `new` puro não consegue.

## Mecânica
Estes passos supõem que a Factory é uma classe. Uma interface precisa de pequenas mudanças.
1. O *instanciador* é a classe que colabora com outras para criar o *produto*. Garanta que ele crie o produto por meio de um Creation Method ([replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md)), alterando a classe do produto se necessário. Compile e teste.
2. Crie a classe factory, com nome derivado do que ela cria (`OrderFactory`). Compile.
3. Mova o Creation Method para a factory com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)). Se era estático, torne-o um método de instância agora. Compile.
4. Faça o instanciador criar a factory e chamá-la para obter o produto. Repita para cada instanciador que deixou de compilar. Compile e teste.
5. Procure dados e métodos nas outras classes que existam apenas para alimentar a criação. Mova-os para a factory com Mover Campo (Move Field) ([move-field.md](../../fowler/moving-features/move-field.md)) e Mover Função, o que também pode mudar quem cria a factory. Compile e teste (adaptação: após cada movimento, e não só no fim).

## Exemplo
Antes: `ApiSession` conhece as opções da requisição, passa-as para `RequestSender`, que apenas as copia para a requisição que cria. As duas classes carregam os mesmos dois campos.

```csharp
public class ApiRequest
{
    public string Path { get; }
    public ApiRequest(string path) { Path = path; }
    public int TimeoutSeconds { get; set; }
    public int MaxRetries { get; set; }
}

public class ApiSession
{
    private readonly int _timeoutSeconds;
    private readonly int _maxRetries;
    public ApiSession(int timeoutSeconds, int maxRetries) { _timeoutSeconds = timeoutSeconds; _maxRetries = maxRetries; }
    public ApiRequest Send(string path) => new RequestSender(_timeoutSeconds, _maxRetries).Prepare(path);
}

public class RequestSender
{
    private readonly int _timeoutSeconds;
    private readonly int _maxRetries;
    public RequestSender(int timeoutSeconds, int maxRetries) { _timeoutSeconds = timeoutSeconds; _maxRetries = maxRetries; }
    public ApiRequest Prepare(string path) => new ApiRequest(path) { TimeoutSeconds = _timeoutSeconds, MaxRetries = _maxRetries };
}
```

Depois: `RequestFactory` guarda as opções e monta a requisição. A sessão a configura uma vez. O sender não sabe mais o que são as opções.

```csharp
public class RequestFactory
{
    private readonly int _timeoutSeconds;
    private readonly int _maxRetries;
    public RequestFactory(int timeoutSeconds, int maxRetries) { _timeoutSeconds = timeoutSeconds; _maxRetries = maxRetries; }
    public ApiRequest CreateRequest(string path) => new(path) { TimeoutSeconds = _timeoutSeconds, MaxRetries = _maxRetries };
}

public class ApiSession
{
    private readonly RequestFactory _factory;
    public ApiSession(int timeoutSeconds, int maxRetries) { _factory = new RequestFactory(timeoutSeconds, maxRetries); }
    public ApiRequest Send(string path, RequestSender sender) => sender.Prepare(path, _factory);
}

public class RequestSender
{
    public ApiRequest Prepare(string path, RequestFactory factory) => factory.CreateRequest(path);
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As opções agora vivem em uma só classe. Uma busca pelos campos que antes eram copiados entre classes encontra apenas a factory.
- A factory remove um espalhamento real. Se ela apenas envolve um único `new`, desfaça.
