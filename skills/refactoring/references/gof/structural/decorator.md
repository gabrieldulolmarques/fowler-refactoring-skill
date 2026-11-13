# Decorator

Gamma et al. (1995), cap. 4, p. 175. Também conhecido como: Wrapper. Categoria: estrutural de objeto.

## Intenção
Acrescentar responsabilidades a um objeto individual em tempo de execução, envolvendo-o em outro objeto com a mesma interface. É uma alternativa flexível à herança para cada combinação de funcionalidades.

## Quando compensa
- Você quer acrescentar comportamento (novas tentativas, cache, log, compressão) a alguns objetos e não a outros, de forma transparente para quem chama, e possivelmente removê-lo depois.
- Usar herança exigiria uma classe por combinação de funcionalidades, ou a classe não pode ser herdada.
- Benefícios: as funcionalidades são peças pequenas e empilháveis. Você paga apenas pelas que acopla, e pode acoplar a mesma uma duas vezes.
- Custos: um objeto decorado não é o mesmo objeto do original (não dependa de identidade nem de verificação de tipo), e uma pilha de muitos objetos pequenos parecidos é mais difícil de ler e depurar.
- Dispense quando você precisa de apenas um comportamento extra em um único lugar (uma subclasse simples ou uma chamada direta bastam), ou quando o componente é tão pesado e tem tantos membros que cada envoltório teria de repassar dezenas deles.

## Participantes em C#
- **Component** (`IApiClient`): a interface compartilhada pelo objeto real e pelos envoltórios. Mantenha-a pequena.
- **ConcreteComponent** (`HttpApiClient`): o objeto que faz o trabalho real.
- **Decorator** (`RetryingClient`, `CachingClient`, `LoggingClient`): classes que implementam a interface do componente, guardam outro componente, repassam as chamadas a ele e acrescentam comportamento antes ou depois. Uma base abstrata `Decorator` que apenas repassa é opcional; com uma interface de um único método, não compensa tê-la.
- **Client** (código em `Main`): compõe a pilha e a usa pela interface do componente.

## Exemplo (C#)
Um cliente de API HTTP ganha novas tentativas e um cache de respostas, e ambos são opcionais. A pilha é montada em um único lugar.

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public interface IApiClient
{
    Task<string> GetAsync(string path);
}

public class HttpApiClient : IApiClient
{
    private int _calls;

    public Task<string> GetAsync(string path)
    {
        _calls++;
        if (_calls == 1)
            throw new InvalidOperationException("temporary failure");
        return Task.FromResult($"body of {path}");
    }
}

public class RetryingClient : IApiClient
{
    private readonly IApiClient _inner;
    private readonly int _maxAttempts;

    public RetryingClient(IApiClient inner, int maxAttempts)
    {
        _inner = inner;
        _maxAttempts = maxAttempts;
    }

    public async Task<string> GetAsync(string path)
    {
        for (int attempt = 1; ; attempt++)
        {
            try
            {
                return await _inner.GetAsync(path);
            }
            catch (InvalidOperationException) when (attempt < _maxAttempts)
            {
                await Task.Delay(10 * attempt);
            }
        }
    }
}

public class CachingClient : IApiClient
{
    private readonly IApiClient _inner;
    private readonly Dictionary<string, string> _cache = new();

    public CachingClient(IApiClient inner) => _inner = inner;

    public async Task<string> GetAsync(string path)
    {
        if (_cache.TryGetValue(path, out string? hit))
            return hit;
        string body = await _inner.GetAsync(path);
        _cache[path] = body;
        return body;
    }
}

public class LoggingClient : IApiClient
{
    private readonly IApiClient _inner;

    public LoggingClient(IApiClient inner) => _inner = inner;

    public async Task<string> GetAsync(string path)
    {
        Console.WriteLine($"GET {path}");
        string body = await _inner.GetAsync(path);
        Console.WriteLine($"GET {path} -> {body.Length} chars");
        return body;
    }
}

public static class Program
{
    public static async Task Main()
    {
        IApiClient client = new LoggingClient(new CachingClient(new RetryingClient(new HttpApiClient(), 3)));
        await client.GetAsync("/orders/7");
        await client.GetAsync("/orders/7"); // atendido pelo cache
    }
}
```

## Variações
- **A ordem importa**: no exemplo, o cache envolve as tentativas, então um acerto no cache nunca tenta de novo. Trocá-los muda o comportamento. Documente a ordem pretendida no ponto onde a pilha é montada.
- **Decorador único sem classe base**: com uma só responsabilidade a acrescentar, dispense o decorador abstrato e escreva o envoltório diretamente, como acima.
- **Decoradores com membros extras**: um decorador pode acrescentar uma operação própria (um método para limpar o cache). Quem usa essa operação precisa manter o decorador concreto, e então perde a transparência.
- **Componente leve**: mantenha a interface compartilhada restrita a comportamento, não a dados. Um componente pesado torna cada envoltório caro. Quando o componente é pesado, dê a ele um objeto auxiliar substituível (uma estratégia) para a parte que varia.
- **Estratégia em vez de envolver**: o próprio componente guarda um objeto de comportamento substituível. Isso muda o interior do objeto e permite que a estratégia tenha uma interface própria e estreita, mas o componente precisa conhecer o ponto de extensão.

## Riscos e alternativas em C#
- Para HTTP, o .NET já tem esse padrão: `DelegatingHandler` empilhado sobre `HttpClient`. Use-o em vez de escrever uma nova cadeia de decoradores quando usa `HttpClient`.
- Um decorador transversal sobre uma interface grande obriga a escrever cada membro à mão. Source generators, uma biblioteca de proxy dinâmico ou pipelines de middleware (delegates da forma `Func<Request, Func<Request, Task>, Task>`) reduzem essa repetição.
- Em um contêiner de DI, registre os decoradores envolvendo o registro do serviço interno, para que nenhum consumidor monte a pilha por conta própria.
- Descarte as cadeias corretamente: se o objeto interno é `IDisposable`, o decorador que o possui deve descartá-lo (ou deixar isso para o contêiner, mas apenas um lugar deve fazê-lo).
- Cache dentro de um decorador precisa de um limite de tamanho e de um tempo de vida. O dicionário acima cresce para sempre e não é seguro para threads, o que só serve para ilustrar.

## Padrões relacionados
- [adapter.md](adapter.md): muda a interface; um decorador mantém a interface e acrescenta responsabilidades.
- [composite.md](composite.md): a mesma forma recursiva, com propósito diferente. Um decorador pode ser visto como um composite com um único filho que acrescenta comportamento em vez de agregar. Muitas vezes são usados juntos.
- [strategy.md](../behavioral/strategy.md): muda o interior do objeto em vez de envolver sua casca. Prefira-o quando o componente é pesado.
- [proxy.md](proxy.md): semelhante na implementação, mas um proxy controla o acesso ao seu sujeito, enquanto um decorador acrescenta responsabilidades e pode ser empilhado.

## Verificação
- Cada decorador tem uma razão de existir e pode ser removido da pilha sem quebrar os outros.
- Os chamadores dependem apenas da interface do componente e nunca de um tipo decorador.
- Um teste por decorador usa um componente interno falso. Um teste verifica a ordem combinada (por exemplo, que um acerto no cache não faz nenhuma chamada interna).
- Descarte e exceções passam corretamente: uma exceção da chamada interna é tratada de propósito ou se propaga sem alterações.
