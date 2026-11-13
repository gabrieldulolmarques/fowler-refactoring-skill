# Extrair Parâmetro (Extract Parameter)

Kerievsky (2004), cap. 11, p. 346. Padrão: —. Direção: —.

## Quando usar
Smells: — (um passo de baixo nível; o livro precisou dele logo depois de transformar herança em delegação).

- Um campo é atribuído a partir de um objeto criado dentro da classe (em um construtor ou método), e você prefere deixar o cliente decidir qual objeto recebe.
- Divida a atribuição em duas: o cliente fornece o lado direito, a classe mantém o lado esquerdo.
- O livro usou em [move-embellishment-to-decorator.md](../simplification/move-embellishment-to-decorator.md), depois de Substituir Superclasse por Delegação (Replace Superclass with Delegate) ([replace-superclass-with-delegate.md](../../fowler/inheritance/replace-superclass-with-delegate.md)): a classe que delega criava o próprio delegado, mas um cliente precisava fornecê-lo.

## Mecânica
1. A atribuição precisa estar em um construtor ou método. Se não estiver (um inicializador de campo, por exemplo), mova-a primeiro para dentro de um.
2. Adicione um parâmetro para o valor ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)), tipado como o tipo do campo. Em cada ponto de chamada, passe a expressão que antes estava na atribuição, e troque a atribuição para usar o parâmetro. Compile e teste.
3. Se os argumentos antigos do método não forem mais usados, remova-os também com Mudar Declaração de Função (Change Function Declaration). Compile e teste.

## Exemplo
Antes: o uploader cria seu próprio armazenamento da camada cool, então enviar para outra camada exige editar a classe.

```csharp
public interface IBlobStore { string Put(string key, byte[] data, string contentType); }

public class CoolBlobStore : IBlobStore
{
    public string Put(string key, byte[] data, string contentType) => $"cool/{key}";
}

public class Uploader
{
    private readonly IBlobStore _store;

    public Uploader() => _store = new CoolBlobStore();

    public string Upload(string key, byte[] data) => _store.Put(key, data, "application/octet-stream");
}
```

Depois: o armazenamento vem do cliente. O comportamento antigo fica no ponto de chamada que monta o uploader.

```csharp
public class Uploader
{
    private readonly IBlobStore _store;

    public Uploader(IBlobStore store) => _store = store;

    public string Upload(string key, byte[] data) => _store.Put(key, data, "application/octet-stream");
}

public static class Caller
{
    public static Uploader Make() => new(new CoolBlobStore());
}
```

## Notas (C#)
- Valide na fronteira: um parâmetro `null` deve falhar com `ArgumentNullException.ThrowIfNull(store)` quando, sem isso, o nulo apareceria bem mais tarde.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum código da classe cria mais o valor, e um teste agora pode passar um fake do tipo.
