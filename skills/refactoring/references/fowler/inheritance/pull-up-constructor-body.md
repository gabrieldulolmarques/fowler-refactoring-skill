# Subir Corpo do Construtor (Pull Up Constructor Body)

Fowler (2018), cap. 12, p. 355. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smell: nenhum específico no livro (relacionado: Código Duplicado (Duplicated Code)). Duas ou mais subclasses atribuem os mesmos campos, ou
executam a mesma configuração, no início dos seus construtores. Um construtor não pode ser tratado
como um método comum: a parte da superclasse deve ser inicializada primeiro e o construtor da
subclasse a chama explicitamente, então o caminho usual "extrair, depois Subir Método" não
funciona diretamente para a inicialização compartilhada. Puxe o código para um construtor da superclasse e
passe o que ele precisa pela chamada.

Se parte do código compartilhado precisa de valores que só a subclasse terá definido até então, ela não pode ser
levada para o construtor da base. Trate essa parte separadamente, como no passo 4. Se o conjunto todo
ficar confuso, considere Substituir Construtor por Função de Fábrica (Replace Constructor with Factory Function)
([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)).

## Mecânica
1. Garanta que a superclasse tenha um construtor (crie um se necessário) e que todo construtor de subclasse
   o chame.
2. Em cada construtor de subclasse, use Deslocar Instruções (Slide Statements) ([slide-statements.md](../moving-features/slide-statements.md)) para reordenar
   as atribuições compartilhadas de modo que fiquem imediatamente após a chamada à base. Teste.
3. Mova as instruções compartilhadas para o construtor da superclasse, apague-as de cada subclasse,
   adicione um parâmetro de construtor da superclasse para cada valor que o código movido usa e passe esses
   valores a partir de cada chamada da subclasse. Essas edições só compilam juntas, então teste uma vez no final.
4. Se algum código comum não puder ir para o início (ele precisa de estado que a subclasse define primeiro),
   aplique Extrair Função nele ([extract-function.md](../first-set/extract-function.md)), depois Subir Método
   ([pull-up-method.md](pull-up-method.md)), e chame-o no final de cada construtor de subclasse.
   Se as cópias diferem apenas nos valores, transforme esses valores em parâmetros do método
   extraído antes de subi-lo (Mudar Declaração de Função,
   [change-function-declaration.md](../first-set/change-function-declaration.md)). Teste.

## Exemplo
Antes: dois tipos de item de mídia compartilham um título e um idioma, cada um atribuído no seu
próprio construtor.

```csharp
public abstract class MediaItem
{
}

public class Track : MediaItem
{
    private readonly string _title;
    private readonly string _language;
    private readonly int _bitrateKbps;

    public Track(string title, string language, int bitrateKbps)
    {
        _bitrateKbps = bitrateKbps;
        _title = title;
        _language = language;
    }
}

public class Podcast : MediaItem
{
    private readonly string _title;
    private readonly string _language;
    private readonly int _episodeNumber;

    public Podcast(string title, string language, int episodeNumber)
    {
        _title = title;
        _language = language;
        _episodeNumber = episodeNumber;
    }
}
```

Depois: os campos compartilhados e as suas atribuições vivem em `MediaItem`. `Track` primeiro deslocou
as suas atribuições para perto da chamada à base, e então ambas foram movidas para cima.

```csharp
public abstract class MediaItem
{
    protected readonly string Title;
    protected readonly string Language;

    protected MediaItem(string title, string language)
    {
        Title = title;
        Language = language;
    }
}

public class Track : MediaItem
{
    private readonly int _bitrateKbps;

    public Track(string title, string language, int bitrateKbps)
        : base(title, language)
    {
        _bitrateKbps = bitrateKbps;
    }
}

public class Podcast : MediaItem
{
    private readonly int _episodeNumber;

    public Podcast(string title, string language, int episodeNumber)
        : base(title, language)
    {
        _episodeNumber = episodeNumber;
    }
}
```

O comportamento comum que deve rodar depois que os dados da subclasse são definidos é extraído para
um método, subido e chamado como a última linha de cada construtor de subclasse. Antes, cada subclasse
terminava o seu construtor com uma instrução semelhante de montagem de rótulo:

```csharp
public abstract class MediaItem
{
    protected readonly string Title;

    protected MediaItem(string title)
    {
        Title = title;
    }
}

public class Track : MediaItem
{
    private readonly int _bitrateKbps;
    public string Label { get; private set; }

    public Track(string title, int bitrateKbps) : base(title)
    {
        _bitrateKbps = bitrateKbps;
        Label = "TRK " + Title + " " + _bitrateKbps;
    }
}

public class Podcast : MediaItem
{
    private readonly int _episodeNumber;
    public string Label { get; private set; }

    public Podcast(string title, int episodeNumber) : base(title)
    {
        _episodeNumber = episodeNumber;
        Label = "POD " + Title + " " + _episodeNumber;
    }
}
```

Depois: a etapa de montagem do rótulo é um método em `MediaItem` que lê um prefixo e um detalhe
fornecidos pela subclasse, e cada construtor o chama assim que o seu próprio campo é definido.

```csharp
public abstract class MediaItem
{
    protected readonly string Title;
    public string Label { get; private set; } = "";

    protected MediaItem(string title)
    {
        Title = title;
    }

    protected void Finish(string prefix, object detail)
    {
        Label = prefix + " " + Title + " " + detail;
    }
}

public class Track : MediaItem
{
    private readonly int _bitrateKbps;

    public Track(string title, int bitrateKbps) : base(title)
    {
        _bitrateKbps = bitrateKbps;
        Finish("TRK", _bitrateKbps);
    }
}

public class Podcast : MediaItem
{
    private readonly int _episodeNumber;

    public Podcast(string title, int episodeNumber) : base(title)
    {
        _episodeNumber = episodeNumber;
        Finish("POD", _episodeNumber);
    }
}
```

## Notas (C#)
- O construtor da superclasse é alcançado com o encadeamento de construtores `: base(...)`. O construtor
  da base roda antes do corpo da subclasse e antes das atribuições de campo da própria subclasse no
  corpo do construtor (os inicializadores de campo da subclasse rodam ainda mais cedo).
- Não chame um membro `virtual` a partir do construtor da base para terminar a construção: ele pode rodar
  em uma subclasse cujos campos ainda não foram definidos. É por isso que o código comum tardio vai para um
  método que cada subclasse chama no final do seu próprio construtor.
- Campos que subiram costumam ser `private readonly` mais uma propriedade `protected`/`public`, ou
  `protected readonly`, dependendo de quem precisa deles.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- As atribuições compartilhadas não aparecem mais em nenhum construtor de subclasse, cada subclasse passa
  os valores por `: base(...)`, e a ordem dos efeitos colaterais observáveis durante a construção não muda.
