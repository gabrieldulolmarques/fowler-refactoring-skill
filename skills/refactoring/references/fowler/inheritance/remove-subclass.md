# Remover Subclasse (Remove Subclass)

Fowler (2018), cap. 12, p. 369. Antes / também: antes Replace Subclass with Fields.
Inversa: Substituir Código de Tipo por Subclasses (Replace Type Code with Subclasses) ([replace-type-code-with-subclasses.md](replace-type-code-with-subclasses.md)).

## Quando usar
Smell: nenhum específico no livro (relacionados: Elemento Ocioso (Lazy Element), Generalidade Especulativa (Speculative Generality)).

- Uma subclasse foi adicionada para uma variação que nunca cresceu: ela sobrescreve um ou dois membros para retornar uma
  constante, e nada mais depende do seu tipo. A classe custa atenção dos leitores e
  não devolve nada.
- O comportamento que justificava a subclasse foi para outro lugar ou foi apagado, deixando um toco.
- Normalmente aplicada a um grupo inteiro de subclasses irmãs. Prepare todas primeiro
  (fábrica, testes de tipo), depois incorpore-as uma de cada vez.
- Antes de apagar, olhe os clientes em busca de comportamento que dependa da subclasse. Se ele
  pertenceria à subclasse, ela ainda pode valer a pena ser mantida.
- Não use quando as subclasses carregam comportamento polimórfico real ou estrutura de dados
  diferente. Essa variação é para o que a herança serve.

## Mecânica
1. Encapsule a construção: aplique Substituir Construtor por Função de Fábrica (Replace Constructor with Factory Function)
   ([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)) a cada construtor de subclasse. Se os
   chamadores escolhem a subclasse a partir de um valor de dados (um código, um campo de registro), mova essa lógica
   de seleção para a fábrica. Compile e teste.
2. Encontre todo lugar que testa o tipo de um objeto contra uma subclasse (`is`, `as`,
   `GetType()`). Extraia cada teste para uma função ([extract-function.md](../first-set/extract-function.md)), mova-a para
   a superclasse ([move-function.md](../moving-features/move-function.md)) e faça os chamadores usá-la. Compile e teste após
   cada mudança.
3. Adicione à superclasse um campo que represente aquilo em que as subclasses diferem, e defina-o no
   construtor com o caso padrão. Exponha-o pelo mesmo membro que as subclasses
   sobrescrevem.
4. Pegue uma subclasse. Mude a fábrica para que ela retorne a superclasse com o campo definido com
   o valor daquela subclasse, e mude os testes de tipo movidos para lerem o campo. Compile e teste.
5. Apague essa subclasse. Compile e teste.
6. Repita os passos 4 e 5 para cada subclasse restante.
7. Opcionalmente, torne o caso padrão simétrico aos outros (defina o campo explicitamente na
   fábrica) se isso não acrescentar complexidade.

## Exemplo
Antes: duas subclasses que apenas retornam uma constante, criadas a partir de registros armazenados.

```csharp
using System.Collections.Generic;
using System.Linq;

public class StoredPlaylist
{
    public StoredPlaylist(string name, string kind)
    {
        Name = name;
        Kind = kind;
    }

    public string Name { get; }
    public string Kind { get; }
}

public class Playlist
{
    public Playlist(string name) => Name = name;

    public string Name { get; }
    public virtual string Kind => "standard";
}

public class SmartPlaylist : Playlist
{
    public SmartPlaylist(string name) : base(name) { }
    public override string Kind => "smart";
}

public class CollaborativePlaylist : Playlist
{
    public CollaborativePlaylist(string name) : base(name) { }
    public override string Kind => "collaborative";
}

public class Library
{
    public int CountSmart(List<StoredPlaylist> records)
    {
        var playlists = new List<Playlist>();
        foreach (var record in records)
        {
            switch (record.Kind)
            {
                case "S": playlists.Add(new SmartPlaylist(record.Name)); break;
                case "C": playlists.Add(new CollaborativePlaylist(record.Name)); break;
                default: playlists.Add(new Playlist(record.Name)); break;
            }
        }
        return playlists.Count(p => p is SmartPlaylist);
    }
}
```

Passos 1 e 2: encapsule a criação em uma fábrica e o teste de tipo em um membro da superclasse.

```csharp
// fragment
public class Playlist
{
    // ...
    public bool IsSmart => this is SmartPlaylist;

    public static Playlist Create(StoredPlaylist record) => record.Kind switch
    {
        "S" => new SmartPlaylist(record.Name),
        "C" => new CollaborativePlaylist(record.Name),
        _ => new Playlist(record.Name),
    };
}

public class Library
{
    public int CountSmart(List<StoredPlaylist> records)
    {
        var playlists = records.Select(Playlist.Create).ToList();
        return playlists.Count(p => p.IsSmart);
    }
}
```

Passos 3 a 7: adicione o campo, incorpore cada subclasse na fábrica, depois apague as subclasses.

```csharp
// fragment
public class Playlist
{
    private Playlist(string name, string kind)
    {
        Name = name;
        Kind = kind;
    }

    public string Name { get; }
    public string Kind { get; }
    public bool IsSmart => Kind == "smart";

    public static Playlist Create(StoredPlaylist record) => record.Kind switch
    {
        "S" => new Playlist(record.Name, "smart"),
        "C" => new Playlist(record.Name, "collaborative"),
        _ => new Playlist(record.Name, "standard"),
    };
}
```

O comportamento não muda: `Kind` retorna os mesmos valores, e o código do cliente só mudou nos dois
primeiros passos, antes de qualquer subclasse desaparecer.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
