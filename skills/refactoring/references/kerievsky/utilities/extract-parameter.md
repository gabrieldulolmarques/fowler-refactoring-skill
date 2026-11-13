# Extrair Parâmetro (Extract Parameter)

Kerievsky (2004), cap. 11, p. 346. Direção: —. Padrão: —.

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
Antes: o exportador cria o próprio formatador CSV, então um formato diferente exige editar a classe.

```csharp
public interface IFormatter { string Format(string name, decimal total); }

public class CsvFormatter : IFormatter
{
    public string Format(string name, decimal total) => $"{name},{total:F2}";
}

public class OrderExporter
{
    private readonly IFormatter _formatter;

    public OrderExporter() => _formatter = new CsvFormatter();

    public string Export(string name, decimal total) => _formatter.Format(name, total);
}
```

Depois: o formatador vem do cliente. O comportamento antigo passa a viver no ponto de chamada que constrói o exportador.

```csharp
public class OrderExporter
{
    private readonly IFormatter _formatter;

    public OrderExporter(IFormatter formatter) => _formatter = formatter;

    public string Export(string name, decimal total) => _formatter.Format(name, total);
}

public static class Caller
{
    public static OrderExporter Make() => new(new CsvFormatter());
}
```

## Notas (C#)
- Parâmetros de construtor de tipo interface são exatamente o que um contêiner de injeção de dependência preenche; feito isso, a classe está pronta para ser registrada.
- Se muitos chamadores precisarem do comportamento antigo, mantenha um segundo construtor que forneça o padrão e encaminhe para o novo ([chain-constructors.md](chain-constructors.md)), e remova-o quando os chamadores tiverem migrado.
- Valide na fronteira: um parâmetro `null` deve falhar com `ArgumentNullException.ThrowIfNull(formatter)` quando, de outra forma, o null apareceria bem mais tarde.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum código da classe cria mais o valor, e um teste agora pode passar um fake do tipo.
