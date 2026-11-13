# Extrair Classe (Extract Class)

Fowler (2018), cap. 7, p. 182. Nome anterior / outro nome: —. Inversa: Internalizar Classe (Inline Class)
([inline-class.md](inline-class.md)).

## Quando usar
Smells: Classe Grande (Large Class), Alteração Divergente (Divergent Change), Agrupamentos de Dados (Data Clumps), Obsessão por Primitivos (Primitive Obsession), Campo Temporário (Temporary Field).

- Uma classe cresceu até ter muitos campos e métodos, e parte dela pode ser entendida isoladamente.
- Um subconjunto dos campos e métodos pertence junto: os campos mudam juntos ou dependem uns dos outros.
- Teste: remova mentalmente um campo ou método. Se outros membros perderem o sentido, eles pertencem à mesma classe extraída.
- Subtipagem ou variação afeta apenas alguns recursos da classe, ou recursos diferentes variam de maneiras diferentes.

**Além do livro:** não use quando as partes estiverem muito emaranhadas com o resto e não houver uma
responsabilidade clara para nomear, nem em uma classe pequena e coesa.

## Mecânica
1. Decida qual responsabilidade separar e dê um nome a ela.
2. Crie a nova classe, vazia. Se o nome da original não descrever mais o que sobrou, renomeie-a.
3. Dê à original uma instância da nova classe, criada em seu construtor, e guarde-a em um campo privado.
4. Mova os campos um de cada vez ([move-field.md](../moving-features/move-field.md)). Os membros da original agora delegam para a nova classe. Compile e teste após cada campo.
5. Mova os métodos um de cada vez ([move-function.md](../moving-features/move-function.md)), começando pelos de nível mais baixo (os que são chamados, e não os que chamam). Compile e teste após cada método.
6. Revise as duas interfaces públicas: remova métodos que não são mais necessários e renomeie membros para se adequarem ao novo contexto (a nova classe não precisa dos prefixos ou qualificadores antigos).
7. Decida se vai expor o novo objeto aos clientes. Se sim, considere torná-lo antes um objeto de valor ([change-reference-to-value.md](../organizing-data/change-reference-to-value.md)).

## Exemplo

Antes: uma classe de assinatura que também guarda os dados da franquia de uso e a sua regra de excedente.

```csharp
using System;

public class Subscription
{
    private string _planName;
    private int _includedUnits;
    private int _usedUnits;
    private decimal _overageRate;

    public Subscription(string planName, int includedUnits, int usedUnits, decimal overageRate)
    {
        _planName = planName;
        _includedUnits = includedUnits;
        _usedUnits = usedUnits;
        _overageRate = overageRate;
    }

    public string PlanName => _planName;
    public int IncludedUnits => _includedUnits;
    public int UsedUnits => _usedUnits;
    public decimal OverageRate => _overageRate;

    public int OverageUnits => Math.Max(0, _usedUnits - _includedUnits);
    public decimal OverageCharge => OverageUnits * _overageRate;
}
```

Depois: os dados e o comportamento da franquia vivem em `UsageAllowance`; `Subscription` mantém seus
membros públicos como delegações, então os clientes não mudam.

```csharp
using System;

public class UsageAllowance
{
    public UsageAllowance(int includedUnits, int usedUnits, decimal overageRate)
    {
        IncludedUnits = includedUnits;
        UsedUnits = usedUnits;
        OverageRate = overageRate;
    }

    public int IncludedUnits { get; }
    public int UsedUnits { get; }
    public decimal OverageRate { get; }

    public int OverageUnits => Math.Max(0, UsedUnits - IncludedUnits);
    public decimal OverageCharge => OverageUnits * OverageRate;
}

public class Subscription
{
    private readonly string _planName;
    private readonly UsageAllowance _allowance;

    public Subscription(string planName, int includedUnits, int usedUnits, decimal overageRate)
    {
        _planName = planName;
        _allowance = new UsageAllowance(includedUnits, usedUnits, overageRate);
    }

    public string PlanName => _planName;
    public int IncludedUnits => _allowance.IncludedUnits;
    public int UsedUnits => _allowance.UsedUnits;
    public decimal OverageRate => _allowance.OverageRate;

    public int OverageUnits => _allowance.OverageUnits;
    public decimal OverageCharge => _allowance.OverageCharge;
}
```

Um passo posterior pode expor `UsageAllowance` aos clientes e eliminar as delegações.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda: os membros públicos da classe original devolvem os mesmos valores de antes.
