# Proxy

Gamma et al. (1995), cap. 4, p. 207. Também conhecido como: Surrogate. Categoria: estrutural de objeto.

## Intenção
Colocar na frente de outro objeto um substituto com a mesma interface, para controlar o acesso a ele: adiar sua criação, verificar permissões, alcançá-lo através de uma fronteira ou fazer contabilidade a cada uso.

## Quando compensa
- Um **proxy virtual** adia uma criação cara até o primeiro uso real. Um **proxy de proteção** verifica se quem chama pode executar a operação. Um **proxy remoto** representa um objeto que vive em outro lugar (um cliente HTTP ou RPC gerado é um exemplo). Uma **referência inteligente** acrescenta trabalho no acesso: contagem, bloqueio, carregamento no primeiro toque, log.
- Os chamadores continuam usando a interface do sujeito e não sabem que há um proxy.
- Copy-on-write é outro uso: as cópias compartilham um mesmo sujeito até que alguém o altere.
- Custo: mais uma camada, e às vezes um custo ou uma falha oculta (uma chamada de rede que parece local).
- Não vale a pena quando os chamadores podem criar o objeto de forma preguiçosa com `Lazy<T>`, ou quando uma verificação simples em um único lugar basta.

## Participantes em C#
- **Subject** (`IAssistantTool`): a interface compartilhada pelo objeto real e pelo proxy.
- **RealSubject** (`SearchTool`): o objeto real, possivelmente caro de criar.
- **Proxy** (`AuthorizedToolProxy`, `LazyToolProxy`): implementa a interface do sujeito, guarda uma referência ou os meios de obter o sujeito real (um delegate de fábrica), e decide se e quando repassa cada chamada.

## Exemplo (C#)
Um assistente de chat com IA chama ferramentas. Uma ferramenta de busca é cara para inicializar, então um proxy virtual a cria no primeiro uso. Outra ferramenta é restrita, então um proxy de proteção verifica os escopos de quem chama antes de repassar.

```csharp
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

public interface IAssistantTool
{
    string Name { get; }
    Task<string> RunAsync(string input);
}

public class SearchTool : IAssistantTool
{
    public string Name => "search";

    public SearchTool()
    {
        Console.WriteLine("loading search index...");
    }

    public Task<string> RunAsync(string input) => Task.FromResult($"3 results for '{input}'");
}

public class FileDeleteTool : IAssistantTool
{
    public string Name => "delete_file";

    public Task<string> RunAsync(string input) => Task.FromResult($"deleted {input}");
}

// Proxy virtual: cria a ferramenta real no primeiro uso.
public class LazyToolProxy : IAssistantTool
{
    private readonly Lazy<IAssistantTool> _real;

    public LazyToolProxy(string name, Func<IAssistantTool> factory)
    {
        Name = name;
        _real = new Lazy<IAssistantTool>(factory);
    }

    public string Name { get; }

    public Task<string> RunAsync(string input) => _real.Value.RunAsync(input);
}

// Proxy de proteção: verifica os escopos de quem chama antes de repassar.
public class AuthorizedToolProxy : IAssistantTool
{
    private readonly IAssistantTool _real;
    private readonly ICollection<string> _scopes;
    private readonly string _requiredScope;

    public AuthorizedToolProxy(IAssistantTool real, ICollection<string> callerScopes, string requiredScope)
    {
        _real = real;
        _scopes = callerScopes;
        _requiredScope = requiredScope;
    }

    public string Name => _real.Name;

    public Task<string> RunAsync(string input)
    {
        if (!_scopes.Contains(_requiredScope))
            return Task.FromResult($"refused: {Name} needs scope '{_requiredScope}'");
        return _real.RunAsync(input);
    }
}

public static class Program
{
    public static async Task Main()
    {
        var scopes = new List<string> { "read" };
        var tools = new List<IAssistantTool>
        {
            new LazyToolProxy("search", () => new SearchTool()),
            new AuthorizedToolProxy(new FileDeleteTool(), scopes, "write")
        };

        Console.WriteLine("assistant ready");
        foreach (IAssistantTool tool in tools)
            Console.WriteLine(await tool.RunAsync("quarterly report"));
    }
}
```

## Variações
- **Proxy que conhece apenas a interface**: quando o proxy alcança o sujeito somente pela interface, uma única classe de proxy serve a todos os sujeitos (o proxy de proteção acima). Um proxy virtual precisa construir o sujeito, então recebe um delegate de fábrica ou um tipo concreto.
- **Referência antes da criação**: enquanto o sujeito não existe, o proxy guarda uma referência indireta a ele (um identificador, um nome de arquivo, uma URL) e pode guardar em cache fatos baratos (um tamanho) para responder sem carregar.
- **Repasse automático**: em C# é possível construir proxies sem escrever cada método de repasse, usando um gerador de proxy em tempo de execução (`DispatchProxy` ou uma biblioteca), em que um único handler vê todas as chamadas. Isso serve a verificações transversais, ao custo de velocidade e de menos verificação em tempo de compilação.
- **Copy-on-write**: as cópias compartilham um sujeito. O proxy só copia na primeira escrita.

## Riscos e alternativas em C#
- `Lazy<T>` cobre a maioria dos proxies virtuais sem uma classe nova. Use uma classe de proxy apenas quando os chamadores precisam da interface do sujeito e não podem saber da preguiça.
- Torne os proxies remotos honestos: a interface deve ser assíncrona (`Task`) e os chamadores devem esperar falhas e timeouts. Uma chamada remota disfarçada de local esconde o custo.
- Um proxy de proteção não é a única linha de defesa. Aplique as mesmas verificações no servidor para tudo o que o cliente possa contornar.
- `DispatchProxy` e ferramentas semelhantes usam reflexão, então são mais lentos e não funcionam bem com compilação antecipada (AOT) nem com trimming.
- Não deixe o proxy acumular deveres sem relação entre si. Várias responsabilidades (controle de acesso, cache, log) ficam mais limpas como invólucros (wrappers) separados; veja o decorator.
- Compare identidades com cuidado: o proxy e o sujeito são objetos diferentes.

## Padrões relacionados
- [adapter.md](adapter.md): dá ao objeto adaptado uma interface diferente. Um proxy mantém a mesma (um proxy de proteção pode recusar algumas operações, então pode ser efetivamente um subconjunto).
- [decorator.md](decorator.md): pode ser construído da mesma forma, mas um decorador acrescenta responsabilidades e se empilha, enquanto um proxy controla o acesso ao seu sujeito. Um proxy de proteção pode parecer exatamente um decorador. Um proxy remoto ou virtual pode guardar, no início, apenas uma referência indireta.

## Verificação
- O código cliente usa apenas a interface do sujeito e não muda quando um proxy é colocado ou retirado.
- Com um proxy virtual, criar o proxy não faz nenhum trabalho caro, e a primeira chamada dispara a criação exatamente uma vez (também sob chamadas concorrentes).
- Testes mostram que uma chamada recusada nunca chega ao sujeito real.
- Os caminhos de falha e de timeout de um proxy remoto são testados, não apenas a chamada bem-sucedida.
