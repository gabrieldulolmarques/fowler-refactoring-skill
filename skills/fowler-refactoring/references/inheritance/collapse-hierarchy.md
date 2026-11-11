# Colapsar Hierarquia (Collapse Hierarchy)

Fowler (2018), cap. 12, p. 380. Antes / também: —. Inversa: —.

## Quando usar
Smells: Elemento Ocioso (Lazy Element), Generalidade Especulativa (Speculative Generality).

- Depois de subir e descer membros, uma classe e a sua pai podem acabar tão
  parecidas que a divisão não carrega significado. Una-as.
- Uma classe base com uma única subclasse, sem segunda subclasse planejada, é o caso usual.
- Não colapse quando as duas classes ainda modelam uma distinção real, ou quando outras
  subclasses dependem do nível intermediário.

## Mecânica
1. Decida qual classe sobrevive. Prefira o nome que fará mais sentido daqui para frente;
   se ambos forem igualmente bons, escolha qualquer um.
2. Mova todo membro da classe a ser removida para a sobrevivente, um de cada vez, usando as
   refatorações de subir / descer conforme necessário ([pull-up-method.md](pull-up-method.md),
   [pull-up-field.md](pull-up-field.md), [push-down-method.md](push-down-method.md), [push-down-field.md](push-down-field.md)). Compile e
   teste após cada movimento.
3. Atualize toda referência à classe removida (declarações, conversões, chamadas `new`,
   argumentos genéricos, verificações de tipo) para que aponte para a sobrevivente. Compile e teste.
4. Apague a classe agora vazia.
5. Compile e rode os testes.

## Exemplo
Antes: `RegularInvoice` não acrescenta nada que a base precise manter separado, e é a única
subclasse.

```csharp
public class Invoice
{
    protected decimal Subtotal;

    public Invoice(decimal subtotal) => Subtotal = subtotal;

    public virtual decimal Total() => Subtotal;
}

public class RegularInvoice : Invoice
{
    private readonly decimal _tax;

    public RegularInvoice(decimal subtotal, decimal tax) : base(subtotal) => _tax = tax;

    public override decimal Total() => Subtotal + _tax;
}

// chamador
Invoice invoice = new RegularInvoice(100m, 18m);
```

Depois: `Invoice` sobrevive e absorve o campo, o parâmetro do construtor e o comportamento.

```csharp
public class Invoice
{
    private readonly decimal _subtotal;
    private readonly decimal _tax;

    public Invoice(decimal subtotal, decimal tax)
    {
        _subtotal = subtotal;
        _tax = tax;
    }

    public decimal Total() => _subtotal + _tax;
}

// chamador
Invoice invoice = new Invoice(100m, 18m);
```

Mesmo comportamento: `Total()` retorna 118 para as mesmas entradas.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
