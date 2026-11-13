# Internalizar Classe (Inline Class)

Fowler (2018), cap. 7, p. 186. Nome anterior / outro nome: —. Inversa: Extrair Classe (Extract Class)
([extract-class.md](extract-class.md)).

## Quando usar
Smells: Elemento Ocioso (Lazy Element), Generalidade Especulativa (Speculative Generality), Cirurgia com Espingarda (Shotgun Surgery).

- Uma classe tem tão pouco sobrando (muitas vezes depois que outras refatorações moveram seus membros para fora) que
  adiciona um nome e uma indireção, mas nenhum significado. Incorpore-a à classe que mais a usa.
- Duas classes dividem mal suas responsabilidades. Pode ser mais fácil fundi-las primeiro e
  depois aplicar Extrair Classe (Extract Class) ([extract-class.md](extract-class.md)) pela linha certa do que mover
  membros um por um.
- Não use quando a classe tiver vários clientes sem relação entre si que precisariam, cada um, dos mesmos
  membros copiados ou reexpostos, ou quando ela tiver uma responsabilidade real, mesmo que pequena.

## Mecânica
1. Escolha o alvo: a classe que mais usa a classe de origem.
2. No alvo, adicione um membro delegador para cada membro público da origem que os clientes
   usam. Cada um apenas encaminha para o objeto de origem.
3. Compile e teste.
4. Redirecione os clientes um de cada vez para que chamem os delegadores do alvo em vez de alcançar
   a origem. Compile e teste após cada alteração.
5. Internalize qualquer método da origem que só faça sentido como um todo (veja [inline-function.md](../first-set/inline-function.md))
   para que seu corpo viva no alvo.
6. Mova os campos e métodos da origem para o alvo um de cada vez, substituindo cada
   delegador pelo membro real. Compile e teste após cada movimentação.
7. Mova qualquer construção ou inicialização dos dados da origem para o construtor
   do alvo.
8. Quando a classe de origem estiver vazia e nada a referenciar, apague-a. Compile e teste.

## Exemplo

Antes: `TrialTerms` guarda pouca coisa e só é usada por `Subscription`.

```csharp
using System;

public class TrialTerms
{
    public int Days { get; set; }
    public string Label { get; set; } = "";

    public string Describe() => $"{Label} ({Days} days)";
}

public class Subscription
{
    public Subscription(DateTime startedOn) => StartedOn = startedOn;

    public TrialTerms Trial { get; } = new TrialTerms();
    public DateTime StartedOn { get; }

    public DateTime TrialEnd => StartedOn.AddDays(Trial.Days);
    public string TrialSummary => Trial.Describe();
}

public static class Client
{
    public static void Configure(Subscription subscription)
    {
        subscription.Trial.Days = 14;
        subscription.Trial.Label = "Standard";
    }
}
```

Passos 2 e 4: adicione delegações em `Subscription` e depois mude os clientes para usá-las.

```csharp
using System;

public class Subscription
{
    public Subscription(DateTime startedOn) => StartedOn = startedOn;

    public TrialTerms Trial { get; } = new TrialTerms();
    public DateTime StartedOn { get; }

    public int TrialDays
    {
        get => Trial.Days;
        set => Trial.Days = value;
    }

    public string TrialLabel
    {
        get => Trial.Label;
        set => Trial.Label = value;
    }

    public DateTime TrialEnd => StartedOn.AddDays(Trial.Days);
    public string TrialSummary => Trial.Describe();
}

public static class Client
{
    public static void Configure(Subscription subscription)
    {
        subscription.TrialDays = 14;
        subscription.TrialLabel = "Standard";
    }
}
```

Passos 5 a 8: mova os dados e o comportamento, depois apague `TrialTerms`.

```csharp
using System;

public class Subscription
{
    public Subscription(DateTime startedOn) => StartedOn = startedOn;

    public DateTime StartedOn { get; }
    public int TrialDays { get; set; }
    public string TrialLabel { get; set; } = "";

    public DateTime TrialEnd => StartedOn.AddDays(TrialDays);
    public string TrialSummary => $"{TrialLabel} ({TrialDays} days)";
}

public static class Client
{
    public static void Configure(Subscription subscription)
    {
        subscription.TrialDays = 14;
        subscription.TrialLabel = "Standard";
    }
}
```

O comportamento não muda. Só o código do cliente que chegava até `Trial` mudou de forma, e isso
aconteceu antes de a classe desaparecer.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
