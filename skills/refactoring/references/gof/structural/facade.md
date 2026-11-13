# Facade

Gamma et al. (1995), cap. 4, p. 185. Categoria: estrutural de objeto.

## Intenção
Dar a um conjunto de classes de um subsistema um único ponto de entrada simples, para que a maioria dos clientes não precise saber como as partes se encaixam.

## Quando compensa
- Um subsistema é formado por muitas classes pequenas que precisam ser chamadas na ordem certa, e a maioria dos chamadores quer um caso comum ("armazenar este arquivo") e não os detalhes.
- Os clientes dependem diretamente de muitas classes do subsistema, e você quer cortar essas dependências ou definir um ponto de entrada claro para cada camada.
- Benefícios: menos objetos que os clientes precisam conhecer, acoplamento mais fraco com o subsistema (você pode trocar suas partes) e as classes de nível mais baixo continuam públicas para os poucos clientes que precisam delas.
- Custos: a fachada pode crescer até virar uma classe-deus que guarda regras de negócio, e, se ocultar tudo, impede a personalização.
- Não vale a pena quando há uma única classe a chamar, ou quando a fachada apenas repassa cada chamada uma a uma.

## Participantes em C#
- **Facade** (`UploadService`): classe que sabe quais classes do subsistema tratam cada requisição e as chama em ordem. Não acrescenta regras novas.
- **Subsystem classes** (`IVirusScanner`, `IImageCompressor`, `IBlobStorage`, `IMetadataIndex`): fazem o trabalho real. Não conhecem a fachada.
- **Client** (`Main`): chama a fachada no caso comum.

## Exemplo (C#)
O envio de um arquivo envolve verificação de vírus, compressão, armazenamento e indexação. A fachada expõe um método para o caso comum e recebe suas partes do subsistema pelo construtor.

```csharp
using System;
using System.Threading.Tasks;

public interface IVirusScanner
{
    Task<bool> IsCleanAsync(byte[] content);
}

public interface IImageCompressor
{
    byte[] Compress(byte[] content);
}

public interface IBlobStorage
{
    Task<string> PutAsync(string name, byte[] content);
}

public interface IMetadataIndex
{
    Task RegisterAsync(string name, string url, int sizeInBytes);
}

public class UploadService
{
    private readonly IVirusScanner _scanner;
    private readonly IImageCompressor _compressor;
    private readonly IBlobStorage _storage;
    private readonly IMetadataIndex _index;

    public UploadService(IVirusScanner scanner, IImageCompressor compressor, IBlobStorage storage, IMetadataIndex index)
    {
        _scanner = scanner;
        _compressor = compressor;
        _storage = storage;
        _index = index;
    }

    public async Task<string> UploadImageAsync(string name, byte[] content)
    {
        if (!await _scanner.IsCleanAsync(content))
            throw new InvalidOperationException($"{name} failed the virus scan.");
        byte[] small = _compressor.Compress(content);
        string url = await _storage.PutAsync(name, small);
        await _index.RegisterAsync(name, url, small.Length);
        return url;
    }
}

// Pequenas implementações falsas para o exemplo rodar.
public class AlwaysCleanScanner : IVirusScanner
{
    public Task<bool> IsCleanAsync(byte[] content) => Task.FromResult(true);
}

public class HalvingCompressor : IImageCompressor
{
    public byte[] Compress(byte[] content) => new byte[content.Length / 2];
}

public class InMemoryStorage : IBlobStorage
{
    public Task<string> PutAsync(string name, byte[] content) => Task.FromResult("memory://" + name);
}

public class ConsoleIndex : IMetadataIndex
{
    public Task RegisterAsync(string name, string url, int sizeInBytes)
    {
        Console.WriteLine($"{name} -> {url} ({sizeInBytes} bytes)");
        return Task.CompletedTask;
    }
}

public static class Program
{
    public static async Task Main()
    {
        var uploads = new UploadService(new AlwaysCleanScanner(), new HalvingCompressor(), new InMemoryStorage(), new ConsoleIndex());
        string url = await uploads.UploadImageAsync("avatar.png", new byte[1024]);
        Console.WriteLine(url);
    }
}
```

## Variações
- **Fachada abstrata**: torne a fachada uma interface (`IUploadService`) para que os clientes não saibam qual implementação do subsistema fica por trás, e os testes possam trocá-la por uma versão falsa. Uma alternativa a ter várias classes de fachada é configurar uma única fachada com objetos diferentes do subsistema.
- **Classes públicas e privadas do subsistema**: a fachada faz parte da face pública, mas não é a única parte. Use `internal` para classes que só o subsistema precisa, e deixe públicas as que extensores e clientes avançados usam.
- **Parametrizar a fachada**: deixar os chamadores passarem o verificador ou o armazenamento dá flexibilidade, mas cada opção acrescentada afasta a fachada da meta de tornar o caso comum simples. Mantenha o caminho padrão curto e ofereça uma segunda sobrecarga, ou as partes cruas, para o caso raro.
- **Uma por camada do subsistema**: cada camada expõe uma fachada, e as camadas conversam entre si apenas por meio de fachadas.

## Riscos e alternativas em C#
- Mantenha decisões fora da fachada. Se ela começar a escolher o armazenamento pelo plano do cliente ou a decidir a política de novas tentativas, mova isso para uma classe própria e deixe a fachada apenas sequenciar as chamadas.
- Cuidado com uma fachada que espelha cada método do subsistema. Isso é apenas uma API com outro nome. Ofereça menos operações, moldadas pela tarefa.
- Normalmente uma instância basta. Registre-a com tempo de vida singleton no contêiner de DI, mas não a transforme em um global estático: o contêiner produz o mesmo efeito e a mantém substituível nos testes.
- Se as operações não têm estado compartilhado, uma classe estática de funções auxiliares é tentadora. Ela torna o subsistema impossível de substituir nos testes, então prefira uma instância injetada.

## Padrões relacionados
- [abstract-factory.md](../creational/abstract-factory.md): pode criar os objetos do subsistema sem citar suas classes concretas, ou ocultar classes específicas de plataforma como alternativa a uma fachada.
- [mediator.md](../behavioral/mediator.md): também abstrai classes existentes, mas centraliza a comunicação entre colegas que o conhecem, e pode acrescentar comportamento. Uma fachada apenas simplifica o acesso; o subsistema não sabe que ela existe.
- [singleton.md](../creational/singleton.md): uma fachada costuma ser necessária uma única vez.
- [adapter.md](adapter.md): um adaptador reutiliza uma interface existente, enquanto uma fachada define uma nova.

## Verificação
- Uma chamada típica do cliente precisa de um objeto e de um método, e o cliente não referencia mais a maioria das classes do subsistema.
- As classes do subsistema não têm referência à fachada.
- Remover a fachada não removeria nenhuma capacidade, já que os clientes avançados ainda podem usar as partes.
- A fachada tem testes com implementações falsas que verificam a ordem das chamadas e os caminhos de falha (por exemplo, que uma verificação de vírus reprovada não armazena nada).
