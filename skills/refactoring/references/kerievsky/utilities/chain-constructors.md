# Encadear Construtores (Chain Constructors)

Kerievsky (2004), cap. 11, p. 340. Padrão: —. Direção: —.

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Dois ou mais construtores repetem as mesmas atribuições. Quando alguém adiciona um campo e atualiza só um construtor, os outros deixam o campo sem valor, em silêncio.
- Faça os construtores mais específicos chamarem um mais geral, até chegar a um construtor abrangente que trate todos os casos. Ele geralmente recebe mais parâmetros.
- Se uma classe tem tantos construtores que é difícil de usar, considere [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md), que depende desta refatoração.

## Mecânica
1. Encontre dois construtores com código duplicado e verifique se um pode chamar o outro, para que as linhas duplicadas possam ser apagadas do chamador. Faça-o chamar. Compile e teste.
2. Repita para cada construtor da classe, incluindo os já alterados, até a duplicação ficar o mais baixa possível.
3. Revise os chamadores e reduza a visibilidade de qualquer construtor que não precise mais ser público. Compile e teste.

## Exemplo
Antes: três construtores atribuem os campos cada um por conta própria, e dois repetem a mesma data de retenção padrão.

```csharp
using System;

public enum StorageTier { Hot, Cool, Archive }

public class UploadRequest
{
    private readonly string _path;
    private readonly string _contentType;
    private readonly StorageTier _tier;
    private readonly DateTime _retainUntil;
    private readonly string? _notifyUrl;

    public UploadRequest(string path)
    {
        _path = path;
        _contentType = "application/octet-stream";
        _tier = StorageTier.Hot;
        _retainUntil = DateTime.UtcNow.AddDays(30);
    }

    public UploadRequest(string path, string contentType)
    {
        _path = path;
        _contentType = contentType;
        _tier = StorageTier.Hot;
        _retainUntil = DateTime.UtcNow.AddDays(30);
    }

    public UploadRequest(string path, string contentType, StorageTier tier, DateTime retainUntil, string? notifyUrl)
    {
        _path = path;
        _contentType = contentType;
        _tier = tier;
        _retainUntil = retainUntil;
        _notifyUrl = notifyUrl;
    }
}
```

Depois: só o último construtor atribui campos; cada um dos outros chama um mais geral, passando valores padrão.

```csharp
public class UploadRequest
{
    private readonly string _path;
    private readonly string _contentType;
    private readonly StorageTier _tier;
    private readonly DateTime _retainUntil;
    private readonly string? _notifyUrl;

    public UploadRequest(string path)
        : this(path, "application/octet-stream")
    {
    }

    public UploadRequest(string path, string contentType)
        : this(path, contentType, StorageTier.Hot, DateTime.UtcNow.AddDays(30), null)
    {
    }

    public UploadRequest(string path, string contentType, StorageTier tier, DateTime retainUntil, string? notifyUrl)
    {
        _path = path;
        _contentType = contentType;
        _tier = tier;
        _retainUntil = retainUntil;
        _notifyUrl = notifyUrl;
    }
}
```

## Notas (C#)
- O C# encadeia com `: this(...)` antes do corpo do construtor, e `: base(...)` para a superclasse. A chamada encadeada executa primeiro, então uma expressão de valor padrão não pode usar membros da instância.
- Parâmetros opcionais costumam ser a alternativa mais simples: um só construtor, `UploadRequest(string path, string contentType = "application/octet-stream", StorageTier tier = StorageTier.Hot, DateTime? retainUntil = null, string? notifyUrl = null)`, com `retainUntil ?? ...` dentro. Use o encadeamento quando um valor padrão for calculado, quando dois valores padrão precisarem mudar juntos, ou quando a assinatura fizer parte de uma API pública (acrescentar um parâmetro opcional muda os pontos de chamada em outros assemblies só depois que eles são recompilados, enquanto sobrecargas continuam compatíveis em binário).
- No C# 12 em diante, uma classe com construtor primário faz com que os outros construtores tenham de chamar `this(...)` nele, pela regra da linguagem.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada campo é atribuído em exatamente um construtor, e cada construtor público produz o mesmo objeto de antes para os mesmos argumentos.
