# Substituir Subclasse por Delegação (Replace Subclass with Delegate)

Fowler (2018), cap. 12, p. 381. Antes / também: —. Inversa: —.
Remover Subclasse (Remove Subclass) e Colapsar Hierarquia (Collapse Hierarchy) vão no sentido oposto para casos simples.

## Quando usar
Smells: Troca de Informações Privilegiadas (Insider Trading), Herança Recusada (Refused Bequest), Intermediário (Middle Man).

- A herança dá apenas um eixo de variação. Se a mesma classe também precisa variar por um segundo
  critério, um dos dois precisa se tornar uma delegação.
- A variante precisa mudar durante a vida do objeto (um pedido comum se torna um pedido prioritário),
  e substituir o objeto não é prático porque muitos lugares guardam uma referência a ele.
- A subclasse e a superclasse estão tão emaranhadas que mudar a pai continua quebrando a
  filha, especialmente entre módulos ou equipes.

Quando não usar: se a herança se encaixa bem e nada do acima se aplica, mantenha-a. O resultado
tem lógica de despacho e uma referência de mão dupla, então a refatoração sozinha raramente torna o código
mais simples; o ganho é a liberdade que ela compra. Prefira a herança primeiro e passe para uma delegação
quando ela começar a doer.

## Mecânica
1. Se muitos chamadores constroem a subclasse, envolva primeiro a construção com Substituir Construtor
   por Função de Fábrica (Replace Constructor with Factory Function) ([replace-constructor-with-factory-function.md](../refactoring-apis/replace-constructor-with-factory-function.md)).
2. Crie uma classe delegada vazia. O seu construtor recebe os dados que só a subclasse usa e,
   normalmente, uma referência de volta ao hospedeiro (a instância da superclasse).
3. Adicione à superclasse um campo que guarde o delegado (nulo quando não houver nenhum).
4. Faça o código de criação (fábrica ou construtor) construir o delegado e armazená-lo nesse
   campo.
5. Escolha um método da subclasse e mova-o para o delegado com Mover Função (Move Function)
   ([move-function.md](../moving-features/move-function.md)). Alcance os dados do hospedeiro pela referência de volta; mova para o delegado os dados que só
   a subclasse usa. Deixe por ora um método encaminhador na subclasse.
   Teste.
6. Se o método da superclasse tem chamadores fora da hierarquia, dê ao método da superclasse
   lógica de despacho: use o delegado quando presente, caso contrário o comportamento original. Se o
   método da subclasse chamava a implementação da base, ou extraia o cálculo da base para
   um método próprio que o delegado possa chamar, ou transforme o método do delegado em uma extensão do
   resultado da base (o hospedeiro passa o seu resultado). Não chame o método virtual do próprio hospedeiro
   a partir do delegado: isso gera recursão infinita. Se o método existe apenas na subclasse,
   despache com um padrão sensato para o caso sem delegado. Teste.
7. Se o método não tem chamadores externos, apenas remova o método da subclasse (Remover Código Morto (Remove Dead Code),
   [remove-dead-code.md](../moving-features/remove-dead-code.md)). Teste.
8. Repita os passos 5 a 7 para cada membro da subclasse.
9. Quando várias subclasses se tornam delegados e os padrões ficam duplicados, aplique Extrair
   Superclasse (Extract Superclass) ([extract-superclass.md](extract-superclass.md)) nos delegados e crie sempre algum delegado,
   para que o despacho do hospedeiro não precise de verificação de nulo e os delegados mantenham o comportamento padrão.
   Nunca ramifique pelo tipo concreto do delegado.
10. Mude toda construção da subclasse para construir a superclasse. Teste.
11. Apague a subclasse agora vazia.

## Exemplo
Antes: assinaturas de estudante são uma subclasse.

```csharp
public class Subscription
{
    protected readonly decimal BasePrice;

    public Subscription(decimal basePrice) => BasePrice = basePrice;

    public virtual decimal MonthlyPrice => BasePrice;
    public virtual bool AllowsOfflineDownloads => BasePrice >= 10m;
}

public class StudentSubscription : Subscription
{
    private readonly decimal _discountRate;

    public StudentSubscription(decimal basePrice, decimal discountRate) : base(basePrice)
        => _discountRate = discountRate;

    public override decimal MonthlyPrice => decimal.Round(base.MonthlyPrice * (1 - _discountRate), 2);
    public override bool AllowsOfflineDownloads => true;
    public decimal SavedAmount => BasePrice - MonthlyPrice;
}
```

Depois: o comportamento de estudante vive em um delegado, então uma assinatura pode virar uma de
estudante em tempo de execução e a classe base fica livre para outro uso da herança.

```csharp
// fragment
public class Subscription
{
    private StudentDelegate? _student;

    internal decimal BasePrice { get; }

    private Subscription(decimal basePrice) => BasePrice = basePrice;

    public static Subscription Create(decimal basePrice) => new Subscription(basePrice);

    public static Subscription CreateStudent(decimal basePrice, decimal discountRate)
    {
        var subscription = new Subscription(basePrice);
        subscription.BecomeStudent(discountRate);
        return subscription;
    }

    public void BecomeStudent(decimal discountRate)
        => _student = new StudentDelegate(this, discountRate);

    public decimal MonthlyPrice
    {
        get
        {
            var result = BasePrice;
            return _student is null ? result : _student.ExtendPrice(result);
        }
    }

    public bool AllowsOfflineDownloads
        => _student is null ? BasePrice >= 10m : _student.AllowsOfflineDownloads;

    public decimal? SavedAmount => _student?.SavedAmount;
}

internal class StudentDelegate
{
    private readonly Subscription _host;
    private readonly decimal _discountRate;

    public StudentDelegate(Subscription host, decimal discountRate)
    {
        _host = host;
        _discountRate = discountRate;
    }

    public decimal ExtendPrice(decimal basePrice) => decimal.Round(basePrice * (1 - _discountRate), 2);
    public bool AllowsOfflineDownloads => true;
    public decimal SavedAmount => _host.BasePrice - _host.MonthlyPrice;
}
```

O comportamento não muda para os chamadores que passam por `Subscription.Create` e
`Subscription.CreateStudent`; a classe `StudentSubscription` sumiu.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os testes cobrem as duas variantes de todo método movido, incluindo o caso de chamada à base e uma troca
  de variante em tempo de execução se o delegado deve ser substituível.
- Nenhum chamador ainda constrói a subclasse removida nem verifica o tipo concreto do delegado.
