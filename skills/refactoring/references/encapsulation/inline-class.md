# Internalizar Classe (Inline Class)

Fowler (2018), cap. 7, p. 186. Antes / também: —. Inversa: Extrair Classe (Extract Class)
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
Antes: `PaymentTerms` guarda pouco e só é usada por `Invoice`.

```csharp
public class PaymentTerms
{
    public int NetDays { get; set; }
    public string Label { get; set; } = "";

    public string Describe() => $"{Label} (net {NetDays} days)";
}

public class Invoice
{
    public PaymentTerms Terms { get; } = new PaymentTerms();
    public DateTime IssuedOn { get; init; }

    public DateTime DueDate => IssuedOn.AddDays(Terms.NetDays);
    public string TermsSummary => Terms.Describe();
}

// cliente
invoice.Terms.NetDays = 30;
invoice.Terms.Label = "Standard";
```

Passos 2 e 4: adicione delegadores a `Invoice` e depois altere os clientes para usá-los.

```csharp
public int NetDays
{
    get => Terms.NetDays;
    set => Terms.NetDays = value;
}

public string TermsLabel
{
    get => Terms.Label;
    set => Terms.Label = value;
}

// cliente
invoice.NetDays = 30;
invoice.TermsLabel = "Standard";
```

Passos 5 a 8: mova os dados e o comportamento e depois apague `PaymentTerms`.

```csharp
public class Invoice
{
    public DateTime IssuedOn { get; init; }
    public int NetDays { get; set; }
    public string TermsLabel { get; set; } = "";

    public DateTime DueDate => IssuedOn.AddDays(NetDays);
    public string TermsSummary => $"{TermsLabel} (net {NetDays} days)";
}
```

O comportamento não muda. Só o código cliente que passava por `Terms` mudou de forma, e
isso aconteceu antes de a classe desaparecer.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
