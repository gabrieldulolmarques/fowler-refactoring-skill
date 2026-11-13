# Substituir Construtores por Métodos de Criação (Replace Constructors with Creation Methods)

Kerievsky (2004), cap. 6, p. 57. Padrão: Creation Method. Direção: até.

## Quando usar
Smells: Código Duplicado (Duplicated Code), Obsessão por Primitivos (Primitive Obsession).

- Uma classe tem vários construtores, e os chamadores precisam ler listas de parâmetros ou corpos de construtores para escolher o certo. Uma chamada como `new Subscription("Acme", 20m, 6)` não diz que tipo de assinatura constrói.
- Dois tipos de instância precisam dos mesmos tipos de parâmetro, então o segundo construtor não pode ser escrito. Métodos com nome não têm esse limite.
- Construtores que ninguém chama tendem a sobreviver porque são difíceis de buscar. Um método de criação com nome é fácil de buscar, então código de criação morto fica mais fácil de achar e apagar.
- Um Creation Method é qualquer método estático ou de instância que devolve uma nova instância. Todo Factory Method é um, mas o inverso não vale (veja [introduce-polymorphic-creation-with-factory-method.md](introduce-polymorphic-creation-with-factory-method.md)).
- Relação com Fowler: [replace-constructor-with-factory-function.md](../../fowler/refactoring-apis/replace-constructor-with-factory-function.md) é a versão de construtor único do mesmo movimento (um construtor, uma factory com nome). Este arquivo serve para uma classe com muitos construtores: você escolhe quais tipos de instância merecem um nome, faz todos passarem por um único construtor geral, e esconde o resto.
- Desvantagem: a criação fica não padronizada, porque algumas classes usam `new` e outras usam um Creation Method. Se a classe tem construtores demais porque faz coisas demais, aplique antes Extrair Classe (Extract Class) ([extract-class.md](../../fowler/encapsulation/extract-class.md)). Se a maioria das instâncias usa só uma pequena parte de seus campos, considere dividi-la com subclasses. Uma classe que precisaria de dezenas de Creation Methods pode manter alguns construtores públicos para casos raros, ou receber parâmetros nos seus Creation Methods.
- Se os Creation Methods começarem a ofuscar o propósito real da classe, mova-os para uma factory separada (o livro chama isso de Extrair Factory (Extract Factory); veja [move-creation-knowledge-to-factory.md](move-creation-knowledge-to-factory.md)).

## Mecânica
1. Encontre o construtor geral, o completo, para o qual os outros delegam. Se não existir, crie-o com Encadear Construtores (Chain Constructors) ([chain-constructors.md](../utilities/chain-constructors.md)).
2. Escolha um cliente que chame um construtor para obter um tipo de instância. Aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) sobre essa chamada para obter um método estático público, e depois Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)) para colocá-lo na classe que possui o construtor. Dê a ele o nome do tipo de instância que devolve. Compile e teste.
3. Troque cada outro chamador desse construtor que quer o mesmo tipo de instância para chamar o Creation Method. Compile e teste.
4. Se o construtor escolhido delega a outro, faça o Creation Method chamar o delegado diretamente e internalize o construtor escolhido (como Internalizar Função (Inline Function), [inline-function.md](../../fowler/first-set/inline-function.md), aplicada a um construtor). Compile e teste.
5. Repita os passos 2 a 4 para cada construtor que quiser substituir.
6. Torne não público todo construtor que não tenha chamadores fora da classe. Compile.

## Exemplo
Antes: quatro construtores que diferem apenas nos valores padrão que preenchem. Dois deles recebem um número, então os chamadores precisam observar o tipo (`int` ou `decimal`) para obter o certo.

```csharp
public class Subscription
{
    private readonly string _customer;
    private readonly decimal _monthlyFee;
    private readonly int _months;
    private readonly decimal _discount;

    public Subscription(string customer, decimal monthlyFee) : this(customer, monthlyFee, 12, 0m) { }
    public Subscription(string customer, decimal monthlyFee, int months) : this(customer, monthlyFee, months, 0m) { }
    public Subscription(string customer, decimal monthlyFee, decimal discount) : this(customer, monthlyFee, 12, discount) { }
    public Subscription(string customer, decimal monthlyFee, int months, decimal discount)
    {
        _customer = customer; _monthlyFee = monthlyFee; _months = months; _discount = discount;
    }

    public decimal Total => _monthlyFee * _months * (1 - _discount);
}

var a = new Subscription("Acme", 20m, 6);
var b = new Subscription("Acme", 20m, 0.1m);
```

Depois: resta apenas o construtor geral, privado. Cada tipo de assinatura tem um nome.

```csharp
public class Subscription
{
    private readonly string _customer;
    private readonly decimal _monthlyFee;
    private readonly int _months;
    private readonly decimal _discount;

    private Subscription(string customer, decimal monthlyFee, int months, decimal discount)
    {
        _customer = customer; _monthlyFee = monthlyFee; _months = months; _discount = discount;
    }

    public static Subscription Annual(string customer, decimal monthlyFee) => new(customer, monthlyFee, 12, 0m);
    public static Subscription ForMonths(string customer, decimal monthlyFee, int months) => new(customer, monthlyFee, months, 0m);
    public static Subscription AnnualWithDiscount(string customer, decimal monthlyFee, decimal discount) => new(customer, monthlyFee, 12, discount);

    public decimal Total => _monthlyFee * _months * (1 - _discount);
}

var a = Subscription.ForMonths("Acme", 20m, 6);
var b = Subscription.AnnualWithDiscount("Acme", 20m, 0.1m);
```

## Notas (C#)
- Parâmetros opcionais ou inicializadores de objeto podem substituir alguns construtores encadeados, mas não dão nome ao tipo de instância. Use-os quando as variantes diferem apenas por um valor opcional, e Creation Methods quando as variantes significam coisas diferentes.
- Um `record` com construtor privado mais métodos estáticos funciona do mesmo jeito.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Uma busca pelo construtor não encontra chamadores fora da classe, e nenhum Creation Method fica sem uso.
- Cada nome de Creation Method diz o que difere do padrão (meses, desconto), não como os argumentos estão organizados.
