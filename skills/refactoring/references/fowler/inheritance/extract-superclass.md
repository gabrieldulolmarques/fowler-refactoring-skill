# Extrair Superclasse (Extract Superclass)

Fowler (2018), cap. 12, p. 375. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smells: Classe Grande (Large Class), Classes Alternativas com Interfaces Diferentes (Alternative Classes with Different Interfaces).

- Duas ou mais classes carregam os mesmos campos ou métodos, ou fazem o mesmo trabalho com nomes
  diferentes, e são conceitualmente tipos de uma mesma coisa.
- A semelhança normalmente aparece conforme o código evolui; não é necessária nenhuma classificação
  prévia do domínio.
- Há duas formas de remover a sobreposição: uma classe base compartilhada, ou um auxiliar para o qual as classes
  delegam (Extrair Classe (Extract Class), [extract-class.md](../encapsulation/extract-class.md)). Uma classe base é
  normalmente a primeira tentativa mais barata. Se a hierarquia se mostrar errada, Substituir Superclasse por
  Delegação (Replace Superclass with Delegate) ([replace-superclass-with-delegate.md](replace-superclass-with-delegate.md)) move
  o código para delegação.
- Não use quando as classes apenas se parecem, mas uma não é um tipo da outra.

## Mecânica
1. Adicione uma classe base vazia e faça cada uma das classes originais derivar dela. Se os
   construtores precisarem encadear para o construtor da base, ajuste as suas assinaturas com Mudar
   Declaração de Função (Change Function Declaration) ([change-function-declaration.md](../first-set/change-function-declaration.md)).
2. Compile e teste.
3. Mova os membros compartilhados para a classe base, um de cada vez: corpos de construtor com Subir
   Corpo do Construtor (Pull Up Constructor Body) ([pull-up-constructor-body.md](pull-up-constructor-body.md)), métodos
   com Subir Método (Pull Up Method) ([pull-up-method.md](pull-up-method.md)) e campos com Subir Campo (Pull Up Field)
   ([pull-up-field.md](pull-up-field.md)). Compile e teste após cada movimento.
4. Quando membros fazem a mesma coisa com nomes diferentes, dê a eles um só nome com Mudar
   Declaração de Função, depois suba-os.
5. Inspecione o que resta em cada subclasse em busca de quase-duplicatas. Isole a parte comum com
   Extrair Função (Extract Function) ([extract-function.md](../first-set/extract-function.md)) e suba essa função.
6. Revise os chamadores das classes originais. Qualquer chamador que usa apenas os membros compartilhados
   agora pode depender da classe base.

## Exemplo
Duas classes têm, cada uma, um título e informam uma duração em minutos arredondada para cima, mas
nomeiam e calculam essa duração de formas diferentes.

Antes:

```csharp
using System.Collections.Generic;
using System.Linq;

public class Episode
{
    private readonly string _title;
    private readonly List<int> _segmentSeconds;

    public Episode(string title, List<int> segmentSeconds)
    {
        _title = title;
        _segmentSeconds = segmentSeconds;
    }

    public string Title => _title;
    public int TotalSeconds => _segmentSeconds.Sum();
    public string MinutesLabel => $"{(TotalSeconds + 59) / 60} min";
}

public class Clip
{
    private readonly string _title;
    private readonly int _seconds;

    public Clip(string title, int seconds)
    {
        _title = title;
        _seconds = seconds;
    }

    public string Title => _title;
    public int Seconds => _seconds;
    public string DurationLabel => $"{(Seconds + 59) / 60} min";
}
```

Passos: adicione `MediaItem` como classe base das duas, suba o título pelo construtor, renomeie
`Seconds` para `TotalSeconds` e `DurationLabel` para `MinutesLabel` em `Clip`, depois suba
`MinutesLabel`.

Depois:

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class MediaItem
{
    protected MediaItem(string title)
    {
        Title = title;
    }

    public string Title { get; }
    public abstract int TotalSeconds { get; }
    public string MinutesLabel => $"{(TotalSeconds + 59) / 60} min";
}

public class Episode : MediaItem
{
    private readonly List<int> _segmentSeconds;

    public Episode(string title, List<int> segmentSeconds) : base(title)
    {
        _segmentSeconds = segmentSeconds;
    }

    public override int TotalSeconds => _segmentSeconds.Sum();
}

public class Clip : MediaItem
{
    private readonly int _seconds;

    public Clip(string title, int seconds) : base(title)
    {
        _seconds = seconds;
    }

    public override int TotalSeconds => _seconds;
}
```

Uma fila de reprodução que só precisa de títulos e durações agora pode aceitar um `MediaItem`.

## Notas (C#)
- Torne a superclasse `abstract` quando ela não se destina a ser instanciada; membros que as
  subclasses devem fornecer se tornam `abstract`.
- Se apenas as assinaturas são compartilhadas e não há estado ou comportamento comum, extraia uma
  interface em vez de uma classe base.
- C# tem herança simples: uma classe que já tem uma classe base não pode receber uma segunda.
  Considere o caminho da interface ou da delegação nesse caso.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: cada classe original retorna os mesmos valores de antes, e qualquer
  membro renomeado não tem mais chamadores com o nome antigo.
