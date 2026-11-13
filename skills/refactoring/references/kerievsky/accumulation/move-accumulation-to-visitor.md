# Mover Acumulação para Visitor (Move Accumulation to Visitor)

Kerievsky (2004), cap. 10, p. 320. Padrão: Visitor. Direção: até, rumo a (Visitor); longe (Iterator).

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
Antes: um construtor de resumo percorre registros de exportação de tipos diferentes e testa o tipo de cada um, lendo dados diferentes de cada um.

```csharp
using System.Collections.Generic;

public abstract class ExportRecord { }

public class SaleRecord : ExportRecord
{
    public int Quantity { get; }
    public decimal UnitPrice { get; }

    public SaleRecord(int quantity, decimal unitPrice)
    {
        Quantity = quantity;
        UnitPrice = unitPrice;
    }
}

public class RefundRecord : ExportRecord
{
    public decimal Amount { get; }

    public RefundRecord(decimal amount) => Amount = amount;
}

public class AdjustmentRecord : ExportRecord
{
    public decimal Percent { get; }

    public AdjustmentRecord(decimal percent) => Percent = percent;
}

public class SummaryBuilder
{
    public decimal Net(IEnumerable<ExportRecord> records)
    {
        decimal sales = 0m, refunds = 0m, percent = 0m;
        foreach (var record in records)
        {
            if (record is SaleRecord s) sales += s.Quantity * s.UnitPrice;
            else if (record is RefundRecord r) refunds += r.Amount;
            else if (record is AdjustmentRecord a) percent += a.Percent;
        }
        return sales * (1m - percent / 100m) - refunds;
    }
}
```

Depois (método de acumulação externo): o construtor de resumo é o visitor; cada registro aceita o visitor e chama de volta o método do seu próprio tipo.

```csharp
public interface IRecordVisitor
{
    void VisitSale(SaleRecord record);
    void VisitRefund(RefundRecord record);
    void VisitAdjustment(AdjustmentRecord record);
}

public abstract class ExportRecord
{
    public abstract void Accept(IRecordVisitor visitor);
}

public class SaleRecord : ExportRecord
{
    public int Quantity { get; }
    public decimal UnitPrice { get; }

    public SaleRecord(int quantity, decimal unitPrice)
    {
        Quantity = quantity;
        UnitPrice = unitPrice;
    }

    public override void Accept(IRecordVisitor visitor) => visitor.VisitSale(this);
}

public class RefundRecord : ExportRecord
{
    public decimal Amount { get; }

    public RefundRecord(decimal amount) => Amount = amount;

    public override void Accept(IRecordVisitor visitor) => visitor.VisitRefund(this);
}

public class AdjustmentRecord : ExportRecord
{
    public decimal Percent { get; }

    public AdjustmentRecord(decimal percent) => Percent = percent;

    public override void Accept(IRecordVisitor visitor) => visitor.VisitAdjustment(this);
}

public class SummaryBuilder : IRecordVisitor
{
    private decimal _sales, _refunds, _percent;

    public void VisitSale(SaleRecord record) => _sales += record.Quantity * record.UnitPrice;
    public void VisitRefund(RefundRecord record) => _refunds += record.Amount;
    public void VisitAdjustment(AdjustmentRecord record) => _percent += record.Percent;

    public decimal Net(IEnumerable<ExportRecord> records)
    {
        _sales = _refunds = _percent = 0m;
        foreach (var record in records)
            record.Accept(this);
        return _sales * (1m - _percent / 100m) - _refunds;
    }
}
```

## Notas (C#)
- Em C# 9 em diante, uma expressão `switch` com padrões de tipo muitas vezes resolve o mesmo problema com bem menos código. Use um Visitor apenas quando vários algoritmos precisarem da mesma estrutura, ou quando o conjunto de tipos precisar ser aberto para extensão por outros assemblies.
- Um `IRecordVisitor<TResult>` genérico, com valores de retorno, evita campos mutáveis, ao custo de uma interface mais elaborada.
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os resultados são iguais ao método antigo para cada tipo de origem, incluindo uma coleção que mistura tipos e uma coleção com um caso desconhecido ou vazio.
- Adicionar uma nova classe de origem não compila até que cada visitor a trate.
