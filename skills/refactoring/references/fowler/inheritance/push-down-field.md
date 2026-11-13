# Descer Campo (Push Down Field)

Fowler (2018), cap. 12, p. 361. Antes / também: —. Inversa: Subir Campo (Pull Up Field) ([pull-up-field.md](pull-up-field.md)).

## Quando usar
Smell: Herança Recusada (Refused Bequest). Um campo está em uma superclasse mas apenas uma subclasse, ou uma pequena parte delas, o usa. As outras subclasses carregam estado que nunca tocam, e quem lê a classe base é induzido a erro sobre o que toda instância tem.

Não vale a pena quando a maioria das subclasses usa o campo, ou quando código que trabalha pelo tipo base o lê. Nesse caso o campo pertence à classe base (veja [pull-up-field.md](pull-up-field.md)).

## Mecânica
1. Confirme quais subclasses usam o campo.
2. Procure todo uso do campo e verifique que nenhum código o alcança pelo tipo da superclasse. Inclua reflexão e serialização que possam nomeá-lo: um campo persistido ou serializado pelo seu nome deve manter esse nome na subclasse, ou o mapeamento deve ser atualizado.
3. Declare o campo em toda subclasse que o precisa.
4. Remova o campo da superclasse.
5. Compile e rode os testes. Qualquer erro mostra código que ainda lê o campo pelo tipo base: resolva isso antes de continuar.
6. Remova o campo de qualquer subclasse que o declarou mas não o usa.
7. Compile e rode os testes.

## Exemplo
Antes: `Radius` é declarado na classe base, mas apenas `Circle` o usa.

```csharp
public abstract class Shape
{
    public string Label { get; init; } = "";
    protected double Radius;
}

public class Square : Shape { }

public class Circle : Shape
{
    public double Area() => Math.PI * Radius * Radius;
    public void SetRadius(double value) => Radius = value;
}
```

Depois: o campo vive apenas onde é usado.

```csharp
public abstract class Shape
{
    public string Label { get; init; } = "";
}

public class Square : Shape { }

public class Circle : Shape
{
    private double _radius;
    public double Area() => Math.PI * _radius * _radius;
    public void SetRadius(double value) => _radius = value;
}
```

O comportamento é o mesmo.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
