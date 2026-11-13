# Colapsar Hierarquia (Collapse Hierarchy)

Fowler (2018), cap. 12, p. 380. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smells: Elemento Ocioso (Lazy Element), Generalidade Especulativa (Speculative Generality).

- Depois de subir e descer membros, uma classe e a sua superclasse podem acabar tão
  parecidas que a divisão não carrega significado. Una-as.
- Uma classe base com uma única subclasse, sem segunda subclasse planejada, é o caso usual.
- Não colapse quando as duas classes ainda modelam uma distinção real, ou quando outras
  subclasses dependem do nível intermediário.

## Mecânica
1. Decida qual classe sobrevive. Prefira o nome que fará mais sentido daqui em diante;
   se ambos forem igualmente bons, escolha qualquer um.
2. Mova todo membro da classe a ser removida para a sobrevivente, um de cada vez, usando as
   refatorações de subir / descer conforme necessário ([pull-up-method.md](pull-up-method.md),
   [pull-up-field.md](pull-up-field.md), [push-down-method.md](push-down-method.md), [push-down-field.md](push-down-field.md)). Compile e
   teste após cada movimento.
3. Atualize toda referência à classe removida (declarações, conversões, chamadas `new`,
   argumentos genéricos, verificações de tipo) para que aponte para a sobrevivente. Compile e teste.
4. Apague a classe agora vazia.
5. Compile e rode os testes.

## Exemplo
Antes: `CuratedPlaylist` não acrescenta nada que a base precise manter separado, e é a única
subclasse.

```csharp
public class Playlist
{
    protected string Name;

    public Playlist(string name) => Name = name;

    public virtual string Summary() => Name;
}

public class CuratedPlaylist : Playlist
{
    private readonly string _curator;

    public CuratedPlaylist(string name, string curator) : base(name) => _curator = curator;

    public override string Summary() => Name + " by " + _curator;
}

// chamador
public class Caller
{
    public Playlist Build() => new CuratedPlaylist("Morning Focus", "Ana");
}
```

Depois: `Playlist` sobrevive e absorve o campo, o parâmetro do construtor e o comportamento.

```csharp
// fragment
public class Playlist
{
    private readonly string _name;
    private readonly string _curator;

    public Playlist(string name, string curator)
    {
        _name = name;
        _curator = curator;
    }

    public string Summary() => _name + " by " + _curator;
}

// chamador
public class Caller
{
    public Playlist Build() => new Playlist("Morning Focus", "Ana");
}
```

Mesmo comportamento: `Summary()` retorna "Morning Focus by Ana" para as mesmas entradas.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
