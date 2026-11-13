# Mover Acumulação para Visitor (Move Accumulation to Visitor)

Kerievsky (2004), cap. 10, p. 320. Direção: até, rumo a (Visitor); longe (Iterator). Padrão: Visitor (GoF, p. 331).

## Quando usar
Smells: Método Longo (Long Method), Comandos Switch (Switch Statements).

- Um método reúne informações de várias classes que guardam dados diferentes e expõem interfaces diferentes (classes heterogêneas), geralmente por meio de testes de tipo e conversões (casts).
- Um Visitor faz isso por double dispatch: cada classe tem um método `Accept(visitor)` que chama de volta o método do visitor para a sua própria classe, passando a si mesma. O visitor então lê o que precisa sem conversões.
- Vários algoritmos diferentes sobre a mesma estrutura podem ser, cada um, o seu próprio visitor, e um visitor pode atravessar hierarquias de classes.
- O aviso do livro: na maioria das vezes você não precisa de um Visitor, mas quando precisa, precisa de verdade. Considere soluções mais simples primeiro. Se as classes podem compartilhar uma interface comum (veja Unificar Interfaces (Unify Interfaces) ([unify-interfaces.md](../utilities/unify-interfaces.md))), um Visitor é mais do que você precisa. Compare primeiro com [move-accumulation-to-collecting-parameter.md](move-accumulation-to-collecting-parameter.md).
- Desvantagens: toda nova classe visitável precisa de um método `Accept`, e de um método de visita em cada visitor, e as classes visitadas podem ter de expor mais dos seus dados.

## Mecânica
O livro traz três conjuntos, conforme onde fica o código de acumulação. O método de acumulação reúne dados das *fontes de acumulação* (as classes visitadas).

**Método de acumulação externo** (o código fica numa classe que não é uma das fontes, o *hospedeiro*)
1. Se o hospedeiro já tem trabalho demais, mova o método para um novo hospedeiro primeiro, com Substituir Função por Comando (Replace Function with Command) ([replace-function-with-command.md](../../fowler/refactoring-apis/replace-function-with-command.md)).
2. Transforme as variáveis locais usadas na lógica de acumulação em campos do hospedeiro. Compile e teste.
3. Para cada classe-fonte, aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) à sua parte da lógica, em um método que recebe essa fonte como argumento, chamado `Accept`. Compile e teste.
4. Extraia o corpo de cada `Accept` para um método `VisitSourceName(source)`, em que `SourceName` é o nome da fonte.
5. Mova cada método `Accept` para a sua classe-fonte com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)); ele agora recebe o hospedeiro como argumento. Compile e teste.
6. Internalize as chamadas a `Accept` no método de acumulação com Internalizar Função (Inline Function) ([inline-function.md](../../fowler/first-set/inline-function.md)). Compile e teste.
7. Aplique Unificar Interfaces ([unify-interfaces.md](../utilities/unify-interfaces.md)) à classe base ou interface das fontes, para que `Accept` possa ser chamado polimorficamente.
8. Reescreva o método de acumulação para chamar `Accept` em cada fonte. Compile e teste.
9. Extraia uma interface do hospedeiro declarando os métodos de visita (Extrair Interface (Extract Interface) (só na 1ª ed.)), e altere cada `Accept` para receber essa interface. Compile e teste. O hospedeiro agora é um visitor.

**Método de acumulação interno** (o método é implementado pelas próprias classes-fonte, em uma hierarquia)
1. Crie uma nova classe visitor. Compile.
2. Para cada classe-fonte, acrescente ao visitor um método `VisitSourceName(source)` que devolve `void`. Compile.
3. Em cada classe-fonte, extraia o corpo do método de acumulação para um método `Accept` com a mesma assinatura em todas, de modo que os métodos de acumulação fiquem idênticos. Compile e teste.
4. Suba o método de acumulação, agora idêntico, para a classe base com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)). Compile e teste.
5. Acrescente um parâmetro visitor a cada `Accept` com Mudar Declaração de Função (Change Function Declaration) ([change-function-declaration.md](../../fowler/first-set/change-function-declaration.md)); o método de acumulação passa um novo visitor. Compile.
6. Para cada fonte, mova o código de acumulação de `Accept` para o método de visita correspondente no visitor, deixando `Accept` como `visitor.VisitX(this)`. Compile e teste.

**Substituição por visitor** (nenhuma das duas formas existe ainda, mas um visitor seria melhor)
1. Crie uma classe visitor concreta. Se for o segundo, extraia uma superclasse ou interface para ele (Extrair Superclasse (Extract Superclass) ([extract-superclass.md](../../fowler/inheritance/extract-superclass.md))) e use esse tipo nas assinaturas de `Accept`.
2. Para cada classe-fonte, acrescente um método de visita ao visitor e um método `Accept` na fonte que o chama com `this`. Isso dá o esqueleto.
3. Dê ao visitor uma forma de ler o seu resultado acumulado, inicialmente vazio.
4. No método de acumulação, crie o visitor, chame `Accept` em cada fonte e use o resultado do visitor no lugar do antigo. Os testes agora falham.
5. Preencha cada método de visita movendo o código do método de acumulação. Dê aos métodos de visita acesso ao que precisam, mova variáveis usadas por vários métodos de visita para campos do visitor, e passe as entradas pelo construtor do visitor. Compile e teste se os resultados batem.
6. Remova o código antigo do método de acumulação. Compile e teste.
7. O que sobra percorre os objetos e passa o visitor. Se alguns deles não tiverem `Accept`, dê a eles um `Accept` que não faz nada, para que o laço não precise de verificação de tipo.
8. Extraia esse laço para um método que recebe o visitor e mova-o para onde outros clientes possam alcançá-lo. Compile e teste.

## Exemplo
Antes: uma calculadora percorre cobranças de tipos diferentes e testa o tipo de cada uma, lendo dados diferentes de cada uma.

```csharp
public abstract class Charge { }

public class ProductCharge : Charge
{
    public int Qty { get; init; }
    public decimal UnitPrice { get; init; }
}

public class ShippingCharge : Charge
{
    public decimal Weight { get; init; }
    public decimal RatePerKg { get; init; }
}

public class DiscountCharge : Charge
{
    public decimal Percent { get; init; }
}

public class TotalCalculator
{
    public decimal Total(IEnumerable<Charge> charges)
    {
        decimal subtotal = 0m, shipping = 0m, percent = 0m;
        foreach (var charge in charges)
        {
            if (charge is ProductCharge p) subtotal += p.Qty * p.UnitPrice;
            else if (charge is ShippingCharge s) shipping += s.Weight * s.RatePerKg;
            else if (charge is DiscountCharge d) percent += d.Percent;
        }
        return subtotal * (1m - percent / 100m) + shipping;
    }
}
```

Depois (método de acumulação externo): a calculadora é o visitor; cada cobrança aceita o visitor e chama de volta o método do seu próprio tipo.

```csharp
public interface IChargeVisitor
{
    void VisitProduct(ProductCharge charge);
    void VisitShipping(ShippingCharge charge);
    void VisitDiscount(DiscountCharge charge);
}

public abstract class Charge
{
    public abstract void Accept(IChargeVisitor visitor);
}

public class ProductCharge : Charge
{
    public int Qty { get; init; }
    public decimal UnitPrice { get; init; }
    public override void Accept(IChargeVisitor visitor) => visitor.VisitProduct(this);
}

public class ShippingCharge : Charge
{
    public decimal Weight { get; init; }
    public decimal RatePerKg { get; init; }
    public override void Accept(IChargeVisitor visitor) => visitor.VisitShipping(this);
}

public class DiscountCharge : Charge
{
    public decimal Percent { get; init; }
    public override void Accept(IChargeVisitor visitor) => visitor.VisitDiscount(this);
}

public class TotalCalculator : IChargeVisitor
{
    private decimal _subtotal, _shipping, _percent;

    public void VisitProduct(ProductCharge charge) => _subtotal += charge.Qty * charge.UnitPrice;
    public void VisitShipping(ShippingCharge charge) => _shipping += charge.Weight * charge.RatePerKg;
    public void VisitDiscount(DiscountCharge charge) => _percent += charge.Percent;

    public decimal Total(IEnumerable<Charge> charges)
    {
        _subtotal = _shipping = _percent = 0m;
        foreach (var charge in charges)
            charge.Accept(this);
        return _subtotal * (1m - _percent / 100m) + _shipping;
    }
}
```

## Notas (C#)
- A partir do C# 9, uma expressão `switch` com padrões de tipo costuma resolver o mesmo problema com muito menos código. Use um Visitor apenas quando vários algoritmos precisarem da mesma estrutura, ou quando o conjunto de tipos precisar ser aberto para extensão por outros assemblies.
- O visitor guarda estado entre as visitas, então uma instância de visitor não é thread-safe e deve ser criada por uso (o exemplo zera os campos no início de `Total`; criar uma nova calculadora por chamada é mais seguro).
- Um `IChargeVisitor<TResult>` genérico, com valores de retorno, evita campos mutáveis, ao custo de uma interface mais elaborada.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os resultados são iguais aos do método antigo para cada tipo de fonte, inclusive uma coleção que mistura tipos, e uma coleção com um caso desconhecido ou vazio.
- Acrescentar uma nova classe-fonte falha na compilação até que cada visitor a trate.
