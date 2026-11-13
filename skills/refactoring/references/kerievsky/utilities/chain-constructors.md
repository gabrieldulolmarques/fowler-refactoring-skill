# Encadear Construtores (Chain Constructors)

Kerievsky (2004), cap. 11, p. 340. Direção: —. Padrão: —.

## Quando usar
Smells: Código Duplicado (Duplicated Code).

- Dois ou mais construtores repetem as mesmas atribuições. Quando alguém adiciona um campo e atualiza só um construtor, os outros deixam o campo sem valor, em silêncio.
- Faça os construtores mais específicos chamarem um mais geral, até chegar a um construtor abrangente que trate todos os casos. Ele geralmente recebe mais parâmetros.
- Se uma classe tem tantos construtores que é difícil de usar, considere [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md), que depende desta refatoração.

## Mecânica
1. Encontre dois construtores com código duplicado e verifique se um pode chamar o outro, para que as linhas duplicadas possam ser apagadas do chamador. Faça-o chamar. Compile e teste.
2. Repita para cada construtor da classe, incluindo os já alterados, até a duplicação ficar o mais baixa possível.
3. Revise os chamadores e reduza a visibilidade de qualquer construtor que não precise mais ser público. Compile e teste.

Prefira chamar o construtor abrangente com padrões explícitos em vez de encadear lateralmente entre construtores estreitos, para que exista um único lugar onde os campos são atribuídos.

## Exemplo
Antes: três construtores atribuem os campos cada um por conta própria, e dois repetem a mesma data de vencimento padrão.

```csharp
public class Payment
{
    private readonly decimal _amount;
    private readonly string _currency;
    private readonly DateOnly _dueDate;
    private readonly string? _reference;

    public Payment(decimal amount)
    {
        _amount = amount;
        _currency = "USD";
        _dueDate = DateOnly.FromDateTime(DateTime.Today).AddDays(30);
    }

    public Payment(decimal amount, string currency)
    {
        _amount = amount;
        _currency = currency;
        _dueDate = DateOnly.FromDateTime(DateTime.Today).AddDays(30);
    }

    public Payment(decimal amount, string currency, DateOnly dueDate, string? reference)
    {
        _amount = amount;
        _currency = currency;
        _dueDate = dueDate;
        _reference = reference;
    }
}
```

Depois: só o último construtor atribui campos; os outros passam os padrões para ele.

```csharp
public class Payment
{
    private readonly decimal _amount;
    private readonly string _currency;
    private readonly DateOnly _dueDate;
    private readonly string? _reference;

    public Payment(decimal amount)
        : this(amount, "USD")
    {
    }

    public Payment(decimal amount, string currency)
        : this(amount, currency, DateOnly.FromDateTime(DateTime.Today).AddDays(30), null)
    {
    }

    public Payment(decimal amount, string currency, DateOnly dueDate, string? reference)
    {
        _amount = amount;
        _currency = currency;
        _dueDate = dueDate;
        _reference = reference;
    }
}
```

## Notas (C#)
- C# encadeia com `: this(...)` antes do corpo do construtor, e com `: base(...)` para a superclasse. A chamada encadeada roda primeiro, então uma expressão padrão não pode usar membros da instância.
- Parâmetros opcionais costumam ser a alternativa mais simples: um só construtor, `Payment(decimal amount, string currency = "USD", DateOnly? dueDate = null, string? reference = null)`, com `dueDate ?? ...` dentro. Use encadeamento quando um padrão for calculado, quando dois padrões precisarem mudar juntos, ou quando a assinatura fizer parte de uma API pública (adicionar um parâmetro opcional muda os pontos de chamada em outros assemblies só depois que eles recompilarem, enquanto as sobrecargas continuam compatíveis em binário).
- Em C# 12 e versões posteriores, uma classe com construtor primário faz os demais construtores chamarem `this(...)` nele por regra.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada campo é atribuído em exatamente um construtor, e cada construtor público produz o mesmo objeto de antes para os mesmos argumentos.
