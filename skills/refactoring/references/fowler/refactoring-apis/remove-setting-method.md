# Remover Método de Escrita (Remove Setting Method)

Fowler (2018), cap. 11, p. 331. Antes / também: —. Inversa: —.

## Quando usar
Smells: Dados Mutáveis (Mutable Data), Classe de Dados (Data Class).

- Um setter diz "este valor pode mudar". Se um valor deve permanecer fixo durante a vida do objeto (um id, uma data de criação, um número de conta), o setter diz aos chamadores algo falso e os deixa quebrar a regra.
- Caso típico 1: o construtor é o único código que ainda chama o setter, porque a classe faz até a sua própria inicialização passar pelo membro.
- Caso típico 2: os objetos são montados logo após a construção por uma sequência de atribuições, e nada altera esses valores depois.
- Não use quando os chamadores realmente atualizam um objeto compartilhado e de vida longa por meio do setter e não podem ser reescritos para criar um novo objeto. Nesse caso o valor é genuinamente mutável: mantenha o setter.

## Mecânica
1. Se o construtor ainda não recebe o valor, adicione-o como parâmetro (veja [change-function-declaration.md](../first-set/change-function-declaration.md)) e chame o setter com ele de dentro do construtor (`Id = id;`). Ao remover vários setters, adicione todos os seus valores de uma vez.
2. Encontre toda chamada ao setter fora do construtor. Substitua cada uma pelo valor passado ao construtor no ponto de criação. Compile e teste após cada uma.
3. Se uma chamada não puder ser substituída pela criação de um novo objeto (ela atualiza um objeto que outro código compartilha), pare e desfaça: o valor não é realmente fixo.
4. Aplique Internalizar Função ao setter (veja [inline-function.md](../first-set/inline-function.md)), depois apague-o e torne o membro somente leitura se a linguagem permitir.
5. Compile e rode os testes.

## Exemplo
Antes: `Id` é atribuído uma vez na criação, mas qualquer um pode reatribuí-lo depois.

```csharp
public class Recipient
{
    public string Id { get; set; } = "";
    public string Email { get; set; } = "";
}

public static class Program
{
    public static void Main()
    {
        var recipient = new Recipient();
        recipient.Email = "ada@example.com";
        recipient.Id = "R-1001";
        System.Console.WriteLine($"{recipient.Id} {recipient.Email}");
    }
}
```

Depois: o id chega pelo construtor e não tem setter. `Email` ainda pode mudar, então mantém o setter.

```csharp
public class Recipient
{
    public Recipient(string id)
    {
        Id = id;
    }

    public string Id { get; }
    public string Email { get; set; } = "";
}

public static class Program
{
    public static void Main()
    {
        var recipient = new Recipient("R-1001");
        recipient.Email = "ada@example.com";
        System.Console.WriteLine($"{recipient.Id} {recipient.Email}");
    }
}
```

## Notas (C#)
- Use `{ get; }` para um valor definido apenas no construtor, ou `{ get; init; }` (C# 9+; no Unity precisa de um shim de `IsExternalInit`) quando os chamadores ainda podem defini-lo em um inicializador de objeto (`new Recipient { Id = "R-1001" }`), mas não depois.
- `init` (com a mesma ressalva do shim) é um primeiro passo mais leve quando muitos pontos de criação usam inicializadores: bloqueia a atribuição posterior sem forçar uma mudança no construtor de imediato. Prefira `{ get; }` com um construtor quando o valor for obrigatório, para que o compilador rejeite objetos montados sem ele.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
