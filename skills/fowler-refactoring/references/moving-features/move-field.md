# Mover Campo (Move Field)

Fowler (2018), cap. 8, p. 207. Antes / também: —. Inversa: —.

## Quando usar
Smells: Cirurgia com Espingarda (Shotgun Surgery), Troca de Informações Privilegiadas (Insider Trading).

- Sinais de que o campo está no lugar errado: ele viaja com outro objeto em toda chamada, editar
  um objeto força a edição de um campo de outro, ou um valor é mantido em várias estruturas
  e precisa ser atualizado em cada uma.
- Faça isso assim que o descompasso estiver claro; um campo fora do lugar fica mais caro conforme o código cresce
  ao redor dele.
- Pré-condições: leituras e escritas passam por acessores (caso contrário, encapsule antes), e a
  origem consegue alcançar o destino. Com um registro simples, considere
  [encapsulate-record.md](../encapsulation/encapsulate-record.md) antes.
- Geralmente faz parte de uma mudança maior. Os chamadores podem passar para o novo dono depois, ou a movimentação
  pode precisar esperar até que o uso seja remodelado.

## Mecânica
1. Garanta que o campo de origem esteja encapsulado: todas as leituras e escritas passam por acessores
   ([encapsulate-variable.md](../first-set/encapsulate-variable.md)). Teste.
2. Adicione o campo, com acessores, à classe de destino. Faça o build e execute as verificações estáticas.
3. Garanta que a origem consiga alcançar o destino: por algo que já tem, por um
   novo método de busca ou, como último recurso, por um novo campo (talvez temporário).
4. Aponte os acessores da origem para o campo do destino. Teste.
   - Se vários objetos de origem compartilham um destino, faça primeiro o setter escrever tanto no campo antigo quanto
     no novo e adicione uma asserção ([introduce-assertion.md](../conditional-logic/introduce-assertion.md))
     de que eles concordam. Quando ela se sustentar na prática, mude os acessores por completo.
5. Remova o campo de origem. Teste.

### Atenção
- Ordem de construção: um construtor que define o campo antes de o objeto de destino existir
  vai quebrar assim que o setter apontar para o destino. Desfaça o redirecionamento, reordene com
  [slide-statements.md](slide-statements.md), teste e redirecione de novo.
- Quando vários objetos de origem apontam para um destino, eles podem hoje guardar valores diferentes para
  o campo. Verifique primeiro se todos concordam com o valor do destino; se não concordarem, mover
  o campo muda o comportamento e deixa de ser uma refatoração.
- Registros de dados simples não têm acessores para redirecionar. Introduza funções de acesso, encaminhe todo
  uso por elas e, para um campo imutável, escreva nas duas cópias ao definir enquanto as leituras migram
  uma a uma.

## Exemplo
Antes: a multa por atraso vive no membro, embora seja na verdade um termo da assinatura.

```csharp
public class Member
{
    private readonly Membership _membership;
    private decimal _lateFeePerDay;

    public Member(string name, decimal lateFeePerDay)
    {
        Name = name;
        _lateFeePerDay = lateFeePerDay;
        _membership = new Membership(DateTime.UtcNow.Date);
    }

    public string Name { get; }
    public decimal LateFeePerDay => _lateFeePerDay;

    public void Upgrade() => _lateFeePerDay += 0.25m;

    public decimal FeeFor(int daysLate) => daysLate * _lateFeePerDay;
}

public class Membership
{
    public Membership(DateTime joinedOn) => JoinedOn = joinedOn;
    public DateTime JoinedOn { get; }
}
```

Passo 1, encapsule o campo. O construtor agora passa pelo setter:

```csharp
public Member(string name, decimal lateFeePerDay)
{
    Name = name;
    SetLateFee(lateFeePerDay);
    _membership = new Membership(DateTime.UtcNow.Date);
}

public decimal LateFeePerDay => _lateFeePerDay;
private void SetLateFee(decimal value) => _lateFeePerDay = value;

public void Upgrade() => SetLateFee(LateFeePerDay + 0.25m);
public decimal FeeFor(int daysLate) => daysLate * LateFeePerDay;
```

Passo 2, adicione o campo e os acessores a `Membership`. O novo parâmetro é opcional por enquanto, de modo que
`Member` ainda compila sem alteração:

```csharp
public class Membership
{
    public Membership(DateTime joinedOn, decimal lateFeePerDay = 0m)
    {
        JoinedOn = joinedOn;
        LateFeePerDay = lateFeePerDay;
    }

    public DateTime JoinedOn { get; }
    public decimal LateFeePerDay { get; set; }
}
```

Passo 4, primeira tentativa: redirecione os acessores enquanto o construtor ainda está na ordem antiga.

```csharp
public decimal LateFeePerDay => _membership.LateFeePerDay;
private void SetLateFee(decimal value) => _membership.LateFeePerDay = value;
// o construtor chama SetLateFee antes de _membership ser atribuído:
// NullReferenceException na construção
```

Reverta os acessores e reordene o construtor para que `_membership` exista antes de o setter
rodar. Teste:

```csharp
public Member(string name, decimal lateFeePerDay)
{
    Name = name;
    _membership = new Membership(DateTime.UtcNow.Date);
    SetLateFee(lateFeePerDay);
}
```

Redirecione os acessores de novo. Teste:

```csharp
public decimal LateFeePerDay => _membership.LateFeePerDay;
private void SetLateFee(decimal value) => _membership.LateFeePerDay = value;
```

Passo 5: apague `_lateFeePerDay`. Teste.

Limpeza opcional, como um passo separado: o construtor pode entregar a multa inicial direto para
`Membership`, e o valor padrão temporário do novo parâmetro some. `SetLateFee` fica para
`Upgrade`:

```csharp
public Member(string name, decimal lateFeePerDay)
{
    Name = name;
    _membership = new Membership(DateTime.UtcNow.Date, lateFeePerDay);
}
```

Movendo para um objeto compartilhado: o percentual de imposto de um produto passa a ser o percentual da sua categoria.
Durante a transição, o produto ainda armazena o valor, mas assere que ele coincide:

```csharp
using System.Diagnostics;

public class Product
{
    private readonly Category _category;
    private readonly decimal _vatPercent;

    public Product(string sku, Category category, decimal vatPercent)
    {
        Debug.Assert(vatPercent == category.VatPercent);
        Sku = sku;
        _category = category;
        _vatPercent = vatPercent;
    }

    public string Sku { get; }
    public decimal VatPercent => _vatPercent;
}
```

Depois que a asserção se sustentar, remova o parâmetro do construtor e o campo e retorne
`_category.VatPercent`.

## Notas de C#
- Um campo persistido ou serializado só mantém seu nome armazenado se o mapeamento também for atualizado
  (coluna, nome da propriedade JSON, atributos do serializador). Movê-lo para outra classe muda
  o formato armazenado, então migre ou mapeie os dados.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- No caso do objeto compartilhado, consulte os dados armazenados em busca de linhas cujo valor difira do
  do destino, ou execute com a asserção habilitada (ou uma linha de log no lugar dela) e confirme que
  nada dispara antes de remover o campo antigo.
