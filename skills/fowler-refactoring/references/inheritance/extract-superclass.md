# Extrair Superclasse (Extract Superclass)

Fowler (2018), cap. 12, p. 375. Antes / também: —. Inversa: —.

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
Duas classes têm cada uma um identificador e informam um total que soma a mesma taxa de imposto, mas elas
o nomeiam e calculam de formas diferentes.

Antes:

```csharp
using System.Collections.Generic;
using System.Linq;

public class Invoice
{
    private readonly string _number;
    private readonly List<decimal> _lineAmounts;

    public Invoice(string number, List<decimal> lineAmounts)
    {
        _number = number;
        _lineAmounts = lineAmounts;
    }

    public string Number => _number;
    public decimal Subtotal => _lineAmounts.Sum();
    public decimal TotalWithTax => Subtotal * 1.2m;
}

public class Refund
{
    private readonly string _number;
    private readonly decimal _amount;

    public Refund(string number, decimal amount)
    {
        _number = number;
        _amount = amount;
    }

    public string Number => _number;
    public decimal Amount => _amount;
    public decimal GrossAmount => Amount * 1.2m;
}
```

Passos: adicione `Document` como classe base de ambas, suba o número pelo construtor,
renomeie `Amount` para `Subtotal` e `GrossAmount` para `TotalWithTax` em `Refund`, depois suba
`TotalWithTax`.

Depois:

```csharp
using System.Collections.Generic;
using System.Linq;

public abstract class Document
{
    protected Document(string number)
    {
        Number = number;
    }

    public string Number { get; }
    public abstract decimal Subtotal { get; }
    public decimal TotalWithTax => Subtotal * 1.2m;
}

public class Invoice : Document
{
    private readonly List<decimal> _lineAmounts;

    public Invoice(string number, List<decimal> lineAmounts) : base(number)
    {
        _lineAmounts = lineAmounts;
    }

    public override decimal Subtotal => _lineAmounts.Sum();
}

public class Refund : Document
{
    private readonly decimal _amount;

    public Refund(string number, decimal amount) : base(number)
    {
        _amount = amount;
    }

    public override decimal Subtotal => _amount;
}
```

Uma exportação de livro-razão que só precisa de números e totais agora pode aceitar um `Document`.

## Notas (C#)
- Torne a superclasse `abstract` quando ela não se destina a ser instanciada; membros que
  as subclasses devem fornecer se tornam `abstract`.
- Se apenas as assinaturas são compartilhadas e não há estado ou comportamento comum, extraia uma
  interface em vez de uma classe base.
- C# tem herança simples: uma classe que já tem uma classe base não pode receber uma segunda.
  Considere o caminho da interface ou da delegação nesse caso.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: cada classe original retorna os mesmos valores de antes, e qualquer
  membro renomeado não tem chamadores restantes sob o nome antigo.
