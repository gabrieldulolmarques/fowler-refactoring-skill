# Limitar Instanciação com Singleton (Limit Instantiation with Singleton)

Kerievsky (2004), cap. 9, p. 296. Direção: até. Padrão: Singleton (GoF, p. 127).

## Quando usar
Smells: —. O motivo do livro é o desempenho, não um smell.

- ATENÇÃO: geralmente isto é otimização prematura. Usar um Singleton por hábito, porque ele "deixa o código mais eficiente", é o que o livro chama de Singletonite (Singletonitis), e o remédio é [inline-singleton.md](../creation/inline-singleton.md). Código otimizado também é mais difícil de refatorar do que código que ainda não foi otimizado.
- Faça isso apenas quando as três condições forem verdadeiras: usuários reclamam do desempenho, um profiler mostra que criar os mesmos objetos repetidamente é um custo real, e os objetos não têm estado ou têm apenas estado que pode ser compartilhado.
- O caso do livro é um objeto State criado a cada transição. Depois da medição, tornar cada State sem estado um Singleton melhorou o uso de memória, que foi medido novamente após a mudança.
- Desvantagens: a única instância pode ser alcançada de qualquer lugar, o que muitas vezes aponta para uma falha de design, e não ajuda quando o objeto guarda um estado que não pode ser compartilhado.
- Se a medição posterior não mostrar ganho, desfaça. Objetos comuns são preferíveis a Singletons.

## Mecânica
Estes supõem um único construtor.

1. Escolha uma classe que é instanciada muitas vezes. Aplique [replace-constructors-with-creation-methods.md](../creation/replace-constructors-with-creation-methods.md) mesmo havendo apenas um construtor. O método de criação devolve a própria classe (ou seu tipo base). Compile e teste.
2. Adicione um campo estático privado desse tipo. Inicialize-o com uma instância, se puder. Se a construção precisar de argumentos que só um cliente tem, declare-o sem inicializar. Compile.
3. Faça o método de criação devolver o campo. Quando ele precisar ser criado de forma preguiçosa, faça isso dentro do método de criação, a partir dos argumentos recebidos. Compile e teste.
4. Meça de novo. Mantenha a mudança apenas se compensou.

## Exemplo
Antes: cada pedido cria sua própria política de envio, que não guarda estado.

```csharp
public abstract class ShippingPolicy
{
    public abstract decimal Cost(decimal weightKg);
}

public class StandardShipping : ShippingPolicy
{
    public override decimal Cost(decimal weightKg) => 4m + weightKg * 0.5m;
}

public class Order
{
    public ShippingPolicy Shipping { get; private set; } = new StandardShipping();
}
```

Depois: um método de criação entrega uma única instância compartilhada, e o construtor é privado para que ninguém possa contorná-lo.

```csharp
public class StandardShipping : ShippingPolicy
{
    private static readonly ShippingPolicy Instance = new StandardShipping();

    private StandardShipping() { }

    public static ShippingPolicy Create() => Instance;

    public override decimal Cost(decimal weightKg) => 4m + weightKg * 0.5m;
}

public class Order
{
    public ShippingPolicy Shipping { get; private set; } = StandardShipping.Create();
}
```

## Notas (C#)
- Um inicializador de campo `static readonly` é thread-safe e preguiçoso o suficiente na maioria dos casos: o CLR o executa uma vez. Quando a construção é cara ou precisa de um gatilho posterior, use `Lazy<T>`: `private static readonly Lazy<TaxTable> Instance = new(() => new TaxTable());`.
- Em uma aplicação que já usa um contêiner de injeção de dependência, um registro de tempo de vida singleton (`AddSingleton`) geralmente faz esse trabalho sem campo estático e sem acesso global, e a classe continua sendo uma classe comum que os testes podem construir. Prefira-o onde houver um contêiner.
- Uma instância compartilhada precisa ser segura para uso concorrente. Objetos imutáveis ou sem estado são.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os chamadores recebem a mesma instância sempre (`ReferenceEquals(a, b)`), e um perfil ou uma medição feita antes e depois mostra um ganho real.
