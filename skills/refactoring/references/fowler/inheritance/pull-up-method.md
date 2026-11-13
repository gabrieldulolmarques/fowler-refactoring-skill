# Subir Método (Pull Up Method)

Fowler (2018), cap. 12, p. 350. Antes / também: —. Inversa: Descer Método (Push Down Method)
([push-down-method.md](push-down-method.md)).

## Quando usar
Smell: Código Duplicado (Duplicated Code). Duas ou mais subclasses têm métodos que fazem a mesma coisa. Cada cópia
é um lugar em que uma mudança futura pode ser aplicada a um irmão e esquecida em outro, e
as cópias são difíceis de encontrar depois.

- O caso fácil é uma cópia byte a byte. Quando os corpos apenas se parecem, compare-os linha a
  linha antes de mover: as diferenças muitas vezes revelam comportamento que nenhum teste cobre.
- Se os métodos diferem apenas por um valor ou um pequeno detalhe, primeiro aplique Parametrizar Função (Parameterize Function)
  ([parameterize-function.md](../refactoring-apis/parameterize-function.md)) em cada subclasse para que os corpos se tornem idênticos, depois suba.
- Se o corpo usa membros que existem apenas nas subclasses, suba esses membros primeiro
  ([pull-up-field.md](pull-up-field.md), ou esta refatoração de novo para métodos auxiliares).
- Se os métodos compartilham um fluxo geral mas diferem em alguns passos, a ferramenta certa é um método
  template na superclasse, com os passos variáveis deixados como membros sobrescrevíveis.

Não use quando o comportamento é genuinamente diferente por subclasse, ou quando a superclasse
não deveria conhecer o conceito (o método seria então uma Herança Recusada (Refused Bequest) para outros irmãos).

## Mecânica
1. Ponha os métodos candidatos lado a lado. Se eles alcançam o mesmo resultado mas os seus corpos
   diferem, edite-os passo a passo até que os corpos fiquem idênticos.
2. Verifique que todo membro que o corpo usa é visível a partir da superclasse. Se algum não for, mova-o
   para cima primeiro, ou declare-o na superclasse como abstrato.
3. Se os nomes ou assinaturas diferem entre as cópias, aplique Mudar Declaração de Função (Change Function Declaration)
   ([change-function-declaration.md](../first-set/change-function-declaration.md)) até que todas as cópias coincidam com
   a assinatura desejada na superclasse. Compile e teste.
4. Adicione o método à superclasse, com o corpo tirado de uma das cópias das subclasses.
5. Compile, para pegar qualquer coisa que a superclasse não consiga resolver.
6. Remova uma cópia de subclasse e rode os testes.
7. Remova as outras cópias da mesma forma, uma de cada vez, rodando os testes após cada uma.

## Exemplo
Duas subclasses constroem o mesmo texto de crédito com nomes diferentes.

Antes:

```csharp
public abstract class MediaItem
{
    public MediaItem(string title) => Title = title;

    public string Title { get; }
}

public class Track : MediaItem
{
    public Track(string title, string creator) : base(title) => Creator = creator;

    public string Creator { get; }

    public string Credit() => $"{Title} by {Creator}";
}

public class Podcast : MediaItem
{
    public Podcast(string title, string creator) : base(title) => Creator = creator;

    public string Creator { get; }

    public string Byline() => $"{Title} by {Creator}";
}
```

Passos 2 e 3: os dois corpos são iguais e usam `Creator`, que a superclasse não tem. Declare-o lá
como abstrato, e renomeie `Byline` para `Credit`.

```csharp
public abstract class MediaItem
{
    public MediaItem(string title) => Title = title;

    public string Title { get; }
    public abstract string Creator { get; }
}

public class Track : MediaItem
{
    public Track(string title, string creator) : base(title) => Creator = creator;

    public override string Creator { get; }

    public string Credit() => $"{Title} by {Creator}";
}

public class Podcast : MediaItem
{
    public Podcast(string title, string creator) : base(title) => Creator = creator;

    public override string Creator { get; }

    public string Credit() => $"{Title} by {Creator}";
}
```

Passos 4 a 7: adicione o método à superclasse, depois apague as cópias uma a uma, testando a cada vez.

Depois:

```csharp
public abstract class MediaItem
{
    public MediaItem(string title) => Title = title;

    public string Title { get; }
    public abstract string Creator { get; }

    public string Credit() => $"{Title} by {Creator}";
}

public class Track : MediaItem
{
    public Track(string title, string creator) : base(title) => Creator = creator;

    public override string Creator { get; }
}

public class Podcast : MediaItem
{
    public Podcast(string title, string creator) : base(title) => Creator = creator;

    public override string Creator { get; }
}
```

Chamadores como `new Track("Blue Hour", "Lena")` compilam sem mudança.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhuma subclasse ainda define uma cópia do método que subiu (a menos que o sobrescreva de propósito).
- Toda subclasse da superclasse, inclusive as de fora do par original, ainda se comporta corretamente com o
  método herdado.
