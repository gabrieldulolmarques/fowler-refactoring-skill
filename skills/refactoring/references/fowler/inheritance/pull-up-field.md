# Subir Campo (Pull Up Field)

Fowler (2018), cap. 12, p. 353. Antes / também: —. Inversa: Descer Campo (Push Down Field)
([push-down-field.md](push-down-field.md)).

## Quando usar
Remove declarações de dados duplicadas em subclasses irmãs. Nenhum smell do catálogo se liga
diretamente a ela.

- Comece lendo como as subclasses irmãs usam os seus campos. Se duas delas guardam os mesmos
  dados para o mesmo propósito, o campo é um candidato, qualquer que seja o nome de cada um.
- Uma vez na superclasse, a declaração duplicada some e o código que a usa
  pode acompanhar (veja [pull-up-method.md](pull-up-method.md)).
- Não use quando os campos apenas se parecem mas significam coisas diferentes, ou quando apenas algumas
  das subclasses precisam dos dados. Então o campo pertence ao lugar onde está, ou a uma nova
  classe intermediária.
- Em linguagens em que os campos aparecem na primeira atribuição, sem declaração na classe,
  o mesmo efeito vem de [pull-up-constructor-body.md](pull-up-constructor-body.md).

## Mecânica
1. Inspecione todo uso de cada campo candidato e confirme que todos desempenham o mesmo papel
   (mesmo significado, mesma unidade, mesmo tempo de vida).
2. Se os nomes diferem, renomeie-os para um só nome com [rename-field.md](../organizing-data/rename-field.md). Compile e teste.
3. Declare o campo na superclasse, com uma visibilidade que as subclasses possam alcançar
   (`protected`, ou privado com uma propriedade se você preferir encapsulá-lo).
4. Apague o campo das subclasses, um de cada vez se forem muitas.
5. Compile e rode os testes.

## Exemplo
Antes: dois tipos de assinatura guardam cada um o seu próprio `subscriberName`.

```csharp
public abstract class Subscription
{
    public abstract decimal MonthlyCost();
}

public class FamilyPlan : Subscription
{
    private string subscriberName;
    private int seats;
    private decimal pricePerSeat;

    public FamilyPlan(string subscriberName, int seats, decimal pricePerSeat)
    {
        this.subscriberName = subscriberName;
        this.seats = seats;
        this.pricePerSeat = pricePerSeat;
    }

    public string Describe() => $"Family plan for {subscriberName}";
    public override decimal MonthlyCost() => seats * pricePerSeat;
}

public class StudentPlan : Subscription
{
    private string subscriberName;
    private decimal fee;
    private decimal discount;

    public StudentPlan(string subscriberName, decimal fee, decimal discount)
    {
        this.subscriberName = subscriberName;
        this.fee = fee;
        this.discount = discount;
    }

    public string Describe() => $"Student plan for {subscriberName}";
    public override decimal MonthlyCost() => fee - discount;
}
```

Depois: o campo é declarado uma só vez em `Subscription`. Os construtores das subclasses ainda o
atribuem, o que [pull-up-constructor-body.md](pull-up-constructor-body.md) pode então arrumar. O
inicializador `= ""` evita o aviso CS8618 quando os tipos de referência anuláveis estão habilitados;
ele pode sair quando a atribuição passar para um construtor de `Subscription`.

```csharp
public abstract class Subscription
{
    protected string subscriberName = "";

    public abstract decimal MonthlyCost();
}

public class FamilyPlan : Subscription
{
    private int seats;
    private decimal pricePerSeat;

    public FamilyPlan(string subscriberName, int seats, decimal pricePerSeat)
    {
        this.subscriberName = subscriberName;
        this.seats = seats;
        this.pricePerSeat = pricePerSeat;
    }

    public string Describe() => $"Family plan for {subscriberName}";
    public override decimal MonthlyCost() => seats * pricePerSeat;
}

public class StudentPlan : Subscription
{
    private decimal fee;
    private decimal discount;

    public StudentPlan(string subscriberName, decimal fee, decimal discount)
    {
        this.subscriberName = subscriberName;
        this.fee = fee;
        this.discount = discount;
    }

    public string Describe() => $"Student plan for {subscriberName}";
    public override decimal MonthlyCost() => fee - discount;
}
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Todo construtor de subclasse ainda compila depois que o seu próprio campo é apagado, e a saída de
  `Describe()` e `MonthlyCost()` não muda.
