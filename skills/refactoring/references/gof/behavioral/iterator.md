# Iterator

Gamma et al. (1995), cap. 5, p. 257. Também conhecido como: Cursor. Categoria: comportamental de objeto.

## Intenção
Dar acesso sequencial aos elementos de uma coleção sem expor como ela é armazenada.

## Quando compensa
- Clientes precisam ler o conteúdo de um agregado sem conhecer sua representação interna.
- Você precisa de vários percursos ao mesmo tempo sobre o mesmo agregado, ou de várias ordens de percurso (filtrado, invertido, em profundidade).
- Você quer uma única forma de percorrer diferentes tipos de agregados.
- Benefícios: variantes de percurso são fáceis de adicionar trocando o iterador, a interface do agregado continua pequena, e cada iterador guarda a sua própria posição, então os percursos não interferem uns nos outros.
- Não vale a pena para uma lista ou array simples, onde `foreach` já resolve. Escreva um iterador próprio apenas quando os dados não estiverem em memória (páginas, streams) ou quando a ordem não for a de armazenamento.

## Participantes em C#
- **Iterator** (`IEnumerator<T>`): interface para acessar e avançar pelos elementos. Já vem no .NET.
- **ConcreteIterator** (`StoredFileEnumerator` ou um método com `yield return`): mantém a posição atual.
- **Aggregate** (`IEnumerable<T>`): interface que cria um iterador por meio de `GetEnumerator`.
- **ConcreteAggregate** (`FileListing`): retorna o iterador apropriado.

## Exemplo (C#)
Um cliente de armazenamento em nuvem lista arquivos em páginas. Quem chama quer uma sequência simples e não se importa com tokens de página. `yield return` faz o compilador escrever o iterador, e a próxima página só é buscada quando quem chama precisa dela.

```csharp
using System;
using System.Collections;
using System.Collections.Generic;

public class FilePage
{
    public FilePage(IReadOnlyList<string> names, string? nextToken)
    {
        Names = names;
        NextToken = nextToken;
    }

    public IReadOnlyList<string> Names { get; }
    public string? NextToken { get; }
}

public interface IStorageApi
{
    FilePage ListPage(string? pageToken);
}

public class FileListing : IEnumerable<string>
{
    private readonly IStorageApi _api;

    public FileListing(IStorageApi api) => _api = api;

    public IEnumerator<string> GetEnumerator()
    {
        string? token = null;
        do
        {
            FilePage page = _api.ListPage(token);   // buscada sob demanda
            foreach (string name in page.Names)
                yield return name;
            token = page.NextToken;
        } while (token != null);
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    // Outro percurso sobre o mesmo agregado, como um iterador próprio.
    public IEnumerable<string> WithExtension(string extension)
    {
        foreach (string name in this)
            if (name.EndsWith(extension, StringComparison.OrdinalIgnoreCase))
                yield return name;
    }
}

public class FakeStorageApi : IStorageApi
{
    private readonly string[][] _pages =
    {
        new[] { "a.txt", "b.png" },
        new[] { "c.txt" },
    };

    public FilePage ListPage(string? pageToken)
    {
        int index = pageToken == null ? 0 : int.Parse(pageToken);
        bool hasNext = index + 1 < _pages.Length;
        return new FilePage(_pages[index], hasNext ? (index + 1).ToString() : null);
    }
}

public static class Program
{
    public static void Main()
    {
        var files = new FileListing(new FakeStorageApi());

        foreach (string name in files.WithExtension(".txt"))
            Console.WriteLine(name);

        // Dois percursos independentes ao mesmo tempo: cada enumerador tem o seu próprio estado.
        using var first = files.GetEnumerator();
        using var second = files.GetEnumerator();
        first.MoveNext();
        first.MoveNext();
        second.MoveNext();
        Console.WriteLine($"{first.Current} {second.Current}"); // b.png a.txt
    }
}
```

## Variações
- **Quem controla o laço.** Um iterador externo (o cliente chama `MoveNext`) é flexível: você pode percorrer duas coleções em paralelo ou parar cedo. Um iterador interno (a coleção chama seu delegate para cada elemento, como `List<T>.ForEach`) é mais curto de usar, mas não pode ser pausado nem pareado.
- **Quem é dono do algoritmo de percurso.** O iterador pode conter o algoritmo, o que torna os algoritmos reutilizáveis entre agregados, mas pode precisar acessar a parte interna do agregado. Ou o próprio agregado pode ser o dono do percurso e entregar um cursor que apenas marca uma posição. Um cursor é um snapshot leve da posição, próximo de um memento ([memento.md](memento.md)).
- **Robustez.** Alterar uma coleção durante o percurso pode pular ou repetir elementos. As coleções do .NET lançam `InvalidOperationException` ao serem modificadas. As alternativas são percorrer uma cópia ou projetar o agregado para ajustar os iteradores ativos.
- **Operações extras.** Além do mínimo (`MoveNext`, `Current`), um iterador pode oferecer `Reset`, `Previous`, pular ou espiar, se algum uso precisar.
- **Estruturas compostas.** Percorrer uma árvore com um iterador externo exige uma pilha de posições. Um método recursivo com `yield return`, ou um cursor sobre os vínculos entre os nós, são as formas usuais. Pré-ordem, pós-ordem e largura podem ser cada um um método separado.
- **Iterador nulo.** Um iterador sempre vazio (`Enumerable.Empty<T>()`) elimina casos especiais para as folhas.

## Riscos e alternativas em C#
- Em C#, prefira `IEnumerable<T>` com `yield return` a uma classe enumeradora escrita à mão. O compilador gera a máquina de estados.
- `yield` adia a execução: um bug ou uma exceção na fonte aparece na enumeração, e não na chamada. Valide os argumentos em um método externo que não seja iterador, quando isso importar.
- Enumerar duas vezes executa a fonte duas vezes (duas chamadas de rede, no exemplo acima). Materialize com `ToList()` quando precisar de várias passagens.
- `IEnumerator<T>` é `IDisposable`. `foreach` e `using` fazem o descarte. Um enumerador usado manualmente deve ser descartado, principalmente se segura uma conexão.
- Para fontes assíncronas, `IAsyncEnumerable<T>` com `await foreach` se encaixa melhor em APIs paginadas do que chamadas bloqueantes.
- LINQ é uma biblioteca de iteradores. Verifique se alguma consulta já faz o percurso que você pretende escrever.

## Padrões relacionados
- [Composite](../structural/composite.md): iteradores são frequentemente aplicados a estruturas recursivas, como composites.
- [Factory Method](../creational/factory-method.md): iteradores polimórficos dependem de um factory method (`GetEnumerator`) para criar o correto.
- [Memento](memento.md): um iterador pode capturar sua posição como um memento.

## Verificação
- O consumidor enumera com `foreach` e nunca toca nos detalhes de armazenamento (tokens de página, índices).
- Duas enumerações sobre o mesmo agregado não se perturbam.
- Um agregado vazio e um agregado com um único elemento funcionam.
- O trabalho é preguiçoso: parar cedo (`First`, `break`) não lê o restante.
