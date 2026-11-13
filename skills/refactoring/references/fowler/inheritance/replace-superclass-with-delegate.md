# Substituir Superclasse por Delegação (Replace Superclass with Delegate)

Fowler (2018), cap. 12, p. 399. Nome anterior / outro nome: Replace Inheritance with Delegation. Inversa: —.

## Quando usar

Smells: Herança Recusada (Refused Bequest), Troca de Informações Privilegiadas (Insider Trading), Intermediário (Middle Man).

- A herança foi usada apenas para reutilizar código, e a subclasse expõe membros da superclasse que não se aplicam a ela (uma pilha que é uma lista e assim permite inserir no meio).
- "Toda instância da subclasse é uma instância válida da superclasse" é falso. Um caso típico é um tipo e a sua instância misturados: uma classe de descrição de produto reutilizada como base de um item físico que tem número de série.
- A subclasse quebra sempre que a superclasse muda, porque o acoplamento é forte.

Quando não usar: se todo membro da superclasse se aplica à subclasse e toda instância da subclasse é uma instância legítima da superclasse, a herança é simples e eficaz. A herança é uma boa opção padrão; troque quando ela começar a doer. O custo é um método encaminhador para cada membro que você mantém.

## Mecânica

1. Na subclasse, adicione um campo do tipo da superclasse e inicialize-o com uma nova instância (normalmente construída com os mesmos argumentos de construtor).
2. Para cada membro da superclasse, adicione um membro encaminhador na subclasse que chama o mesmo membro no campo. Compile e teste após cada grupo coerente (um getter e o seu setter andam juntos).
3. Quando todo membro da superclasse tiver um encaminhador, remova o vínculo de herança (descarte o `: Superclass` e a chamada ao construtor da base). Compile e teste.

**Além do livro:** o exemplo abaixo também apaga, um de cada vez, os encaminhadores dos membros que não se aplicam à subclasse, mudando qualquer chamador que o compilador apontar e testando após cada um. Com uma superclasse muito grande, como uma coleção de framework, repassar todo membro é impraticável. Repasse os que os chamadores usam, remova o vínculo e deixe o compilador apontar o resto, como faz o exemplo. Por fim, verifique o modelo. O delegado agora é um componente privado pertencente a uma instância da subclasse. Se as instâncias devem compartilhar o delegado, continue com Mudar Valor para Referência (Change Value to Reference) ([change-value-to-reference.md](../organizing-data/change-value-to-reference.md)). Mantenha no hospedeiro os campos que pertencem a ele, como o id.

## Exemplo

Antes: um histórico de audições reutiliza `List<Play>` por herança, então os chamadores também podem
inserir, ordenar e limpar a lista.

```csharp
using System.Collections.Generic;
using System.Linq;

public class Play
{
    public Play(string title, int seconds)
    {
        Title = title;
        Seconds = seconds;
    }

    public string Title { get; }
    public int Seconds { get; }
}

public class ListeningHistory : List<Play>
{
    public int TotalSeconds() => this.Sum(p => p.Seconds);
}

// chamador
public class Caller
{
    public void Run()
    {
        var history = new ListeningHistory();
        history.Add(new Play("Blue Hour", 212));
        history.Clear(); // não faz sentido para um histórico
    }
}
```

Depois dos passos 1 e 2 (ainda herdando, `new` oculta os membros herdados enquanto os dois coexistem):

```csharp
public class ListeningHistory : List<Play>
{
    private readonly List<Play> _plays = new();

    public new void Add(Play p) => _plays.Add(p);
    public new int Count => _plays.Count;
    public new IEnumerator<Play> GetEnumerator() => _plays.GetEnumerator();

    public int TotalSeconds() => _plays.Sum(p => p.Seconds);
}
```

`new` só oculta membros para os chamadores que usam o tipo `ListeningHistory`. Um chamador que alcança o
objeto por `IEnumerable<Play>` (LINQ, ou um `foreach` sobre uma variável de tipo interface) ainda atinge a
lista herdada, agora vazia, até o passo 3; então verifique se há tais chamadores antes de confiar nos
testes nesta etapa.

Depois do passo 3 e de apagar os encaminhadores que não se aplicam (vínculo removido; o compilador agora rejeita `Clear`):

```csharp
// fragment
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class ListeningHistory : IEnumerable<Play>
{
    private readonly List<Play> _plays = new();

    public void Add(Play p) => _plays.Add(p);
    public int Count => _plays.Count;
    public IEnumerator<Play> GetEnumerator() => _plays.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    public int TotalSeconds() => _plays.Sum(p => p.Seconds);
}
```

O comportamento é o mesmo para todo chamador restante; apenas os membros que não se aplicavam sumiram.

## Verificação

- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum chamador dependia de um membro que foi descartado, ou ele foi repassado de propósito.
- Tudo que tratava a subclasse como a superclasse (conversões, verificações `is`, parâmetros polimórficos,
  coleções do tipo base) foi encontrado e mudado.
