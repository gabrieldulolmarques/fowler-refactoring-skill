# Mover Campo (Move Field)

Fowler (2018), cap. 8, p. 207. Nome anterior / outro nome: —. Inversa: —.

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
Antes: o limite de tentativas fica em `Shipment`, embora na verdade seja um termo do plano de entrega.

```csharp
using System;

public class Shipment
{
    private readonly DeliveryPlan _plan;
    private int _maxAttempts;

    public Shipment(string trackingCode, int maxAttempts)
    {
        TrackingCode = trackingCode;
        _maxAttempts = maxAttempts;
        _plan = new DeliveryPlan(DateTime.UtcNow.Date);
    }

    public string TrackingCode { get; }
    public int MaxAttempts => _maxAttempts;

    public void Escalate() => _maxAttempts += 1;

    public bool CanRetry(int attemptsMade) => attemptsMade < _maxAttempts;
}

public class DeliveryPlan
{
    public DeliveryPlan(DateTime plannedFor) => PlannedFor = plannedFor;
    public DateTime PlannedFor { get; }
}
```

Passo 1, encapsule o campo. O construtor agora passa pelo setter:

```csharp
// trecho
public Shipment(string trackingCode, int maxAttempts)
{
    TrackingCode = trackingCode;
    SetMaxAttempts(maxAttempts);
    _plan = new DeliveryPlan(DateTime.UtcNow.Date);
}

public int MaxAttempts => _maxAttempts;
private void SetMaxAttempts(int value) => _maxAttempts = value;

public void Escalate() => SetMaxAttempts(MaxAttempts + 1);
public bool CanRetry(int attemptsMade) => attemptsMade < MaxAttempts;
```

Passo 2, adicione o campo e os acessores em `DeliveryPlan`. O novo parâmetro é opcional por enquanto, então `Shipment` continua compilando sem mudanças:

```csharp
using System;

public class DeliveryPlan
{
    public DeliveryPlan(DateTime plannedFor, int maxAttempts = 0)
    {
        PlannedFor = plannedFor;
        MaxAttempts = maxAttempts;
    }

    public DateTime PlannedFor { get; }
    public int MaxAttempts { get; set; }
}
```

Passo 4, primeira tentativa: redirecione os acessores enquanto o construtor ainda está na ordem antiga.

```csharp
// trecho
public int MaxAttempts => _plan.MaxAttempts;
private void SetMaxAttempts(int value) => _plan.MaxAttempts = value;
// o construtor chama SetMaxAttempts antes de _plan ser atribuído:
// NullReferenceException na construção
```

Reverta os acessores e reordene o construtor para que `_plan` exista antes de o setter rodar. Teste:

```csharp
// trecho
public Shipment(string trackingCode, int maxAttempts)
{
    TrackingCode = trackingCode;
    _plan = new DeliveryPlan(DateTime.UtcNow.Date);
    SetMaxAttempts(maxAttempts);
}
```

Redirecione os acessores de novo. Teste:

```csharp
// trecho
public int MaxAttempts => _plan.MaxAttempts;
private void SetMaxAttempts(int value) => _plan.MaxAttempts = value;
```

Passo 5: apague `_maxAttempts`. Teste.

Limpeza opcional, como passo separado: o construtor pode entregar o limite inicial diretamente a `DeliveryPlan`, e o valor padrão temporário do novo parâmetro some. `SetMaxAttempts` continua para `Escalate`:

```csharp
// trecho
public Shipment(string trackingCode, int maxAttempts)
{
    TrackingCode = trackingCode;
    _plan = new DeliveryPlan(DateTime.UtcNow.Date, maxAttempts);
}
```

Movendo para um objeto compartilhado: o percentual de seguro de uma encomenda passa a ser o percentual do seu nível de serviço. Durante a transição, a encomenda ainda guarda o valor, mas afirma que ele é igual ao do nível:

```csharp
using System.Diagnostics;

public class ServiceLevel
{
    public ServiceLevel(string name, decimal insurancePercent)
    {
        Name = name;
        InsurancePercent = insurancePercent;
    }

    public string Name { get; }
    public decimal InsurancePercent { get; }
}

public class Parcel
{
    private readonly ServiceLevel _level;
    private readonly decimal _insurancePercent;

    public Parcel(string trackingCode, ServiceLevel level, decimal insurancePercent)
    {
        Debug.Assert(insurancePercent == level.InsurancePercent);
        TrackingCode = trackingCode;
        _level = level;
        _insurancePercent = insurancePercent;
    }

    public string TrackingCode { get; }
    public decimal InsurancePercent => _insurancePercent;
}
```

Quando a asserção tiver se mantido, remova o parâmetro e o campo do construtor, e retorne `_level.InsurancePercent`.

## Notas (C#)
- Um campo persistido ou serializado mantém o nome armazenado só se o mapeamento também for atualizado (coluna, nome da propriedade JSON, atributos do serializador). Movê-lo para outra classe muda o formato armazenado, então migre ou mapeie os dados.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- No caso do objeto compartilhado, consulte os dados armazenados por linhas cujo valor difere do valor do alvo, ou execute com a asserção habilitada (ou com uma linha de log no lugar dela) e confirme que nada dispara antes de remover o campo antigo.
