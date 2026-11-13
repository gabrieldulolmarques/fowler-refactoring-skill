# Singleton

Gamma et al. (1995), cap. 3, p. 127. Categoria: criacional de objeto.

## Intenção
Garantir que uma classe tenha exatamente uma instância e oferecer um único ponto de acesso bem conhecido a ela.

## Quando compensa
- Deve existir exatamente uma instância (um cache compartilhado, um pool de conexões, uma fonte única de configuração) e os clientes precisam alcançá-la a partir de um lugar conhecido.
- A instância única deve poder ser substituída por uma subclasse ou por outra implementação sem mudar o código cliente.
- Benefícios listados para o padrão: acesso controlado à instância, sem nomes globais extras, possibilidade de refinar o comportamento por herança e liberdade para, mais tarde, permitir mais de uma instância.
- Atenção: é o mais criticado dos padrões criacionais. Leia "Riscos e alternativas em C#" abaixo antes de usá-lo. Na maior parte do código C# moderno, um tempo de vida singleton em um contêiner de DI é a melhor resposta.
- Não vale a pena quando a única necessidade é "compartilhar um objeto": crie-o uma vez e passe-o a quem precisa.

## Participantes em C#
- **Singleton** (`FeatureFlags`): uma classe `sealed` com construtor privado, um campo estático privado que guarda a instância e uma propriedade estática `Instance` que a cria no primeiro uso.

A interface (`IFeatureFlags`) não faz parte do padrão original, mas é o que torna a instância substituível e testável.

## Exemplo (C#)
Um armazenamento de feature flags deve existir uma única vez no processo. `Lazy<T>` oferece criação preguiçosa e segurança para threads sem locks escritos à mão.

```csharp
using System;
using System.Collections.Generic;

public interface IFeatureFlags
{
    bool IsEnabled(string name);
}

public sealed class FeatureFlags : IFeatureFlags
{
    private static readonly Lazy<FeatureFlags> _instance = new(() => new FeatureFlags());

    public static FeatureFlags Instance => _instance.Value;

    private readonly HashSet<string> _enabled;

    private FeatureFlags()
    {
        // carregado uma única vez, no primeiro acesso
        _enabled = new HashSet<string> { "new-checkout" };
    }

    public bool IsEnabled(string name) => _enabled.Contains(name);
}

public static class Program
{
    public static void Main()
    {
        Console.WriteLine(FeatureFlags.Instance.IsEnabled("new-checkout"));
    }
}
```

A forma preferida mantém a decisão de "uma instância" no ponto de composição e passa o objeto adiante. O consumidor tem um construtor público comum e depende da interface:

```csharp
public class CheckoutService
{
    private readonly IFeatureFlags _flags;

    public CheckoutService(IFeatureFlags flags) => _flags = flags;

    public string PickFlow() => _flags.IsEnabled("new-checkout") ? "new" : "legacy";
}

public class FixedFlags : IFeatureFlags
{
    private readonly bool _value;
    public FixedFlags(bool value) => _value = value;
    public bool IsEnabled(string name) => _value;
}

public static class Composition
{
    public static void Run()
    {
        // uma instância compartilhada, criada uma vez e repassada
        IFeatureFlags flags = FeatureFlags.Instance;
        var checkout = new CheckoutService(flags);

        // um teste passa sua própria implementação
        var testCheckout = new CheckoutService(new FixedFlags(false));
        System.Console.WriteLine(checkout.PickFlow() + " " + testCheckout.PickFlow());

        // com um contêiner de DI, a mesma intenção cabe em uma linha, por exemplo:
        // services.AddSingleton<IFeatureFlags, FeatureFlags>();
    }
}
```

## Variações
- **Criação preguiçosa.** Crie a instância no primeiro acesso. Em C# use `Lazy<T>` (seguro para threads por padrão) ou um campo `static readonly`, que o runtime inicializa uma vez e com segurança.
- **Criação antecipada.** `public static readonly FeatureFlags Instance = new FeatureFlags();` é a forma segura para threads mais simples, ao custo de criar a instância quando o tipo é usado pela primeira vez.
- **Escolha de subclasse.** O código de `Instance` pode escolher a classe concreta a partir de configuração ou de uma variável de ambiente; isso fixa no código o conjunto de classes possíveis.
- **Registro de singletons.** `Instance` busca uma implementação pelo nome em um registro no qual as implementações se cadastram. Mais flexível, e aproxima o design de um localizador de serviços.
- **Número controlado de instâncias.** Só a operação de acesso precisa mudar se você precisar de duas no futuro, por exemplo, uma por tenant.

## Riscos e alternativas em C#
- **Estado global.** Um `Instance` estático é uma variável global disfarçada. Qualquer código pode lê-la ou alterá-la, então o comportamento depende de quem a tocou antes, e testes executados no mesmo processo vazam estado entre si.
- **Dependências ocultas.** Uma classe que chama `FeatureFlags.Instance` dentro dos seus métodos não mostra a dependência no construtor nem na assinatura. Leitores e ferramentas não a enxergam, e substituí-la exige editar a classe.
- **Testes.** Não é possível substituir por uma implementação falsa sem artifícios extras (métodos de reset, reflexão, setters só para teste), e testes em paralelo interferem entre si. Depender de uma interface recebida por parâmetro elimina tudo isso.
- **Prefira passar a instância.** Crie o objeto único na inicialização e entregue-o às classes que precisam, como parâmetro de construtor tipado por uma interface (segundo exemplo acima).
- **Prefira o tempo de vida singleton do contêiner.** Com injeção de dependência, `AddSingleton<IFeatureFlags, FeatureFlags>()` dá uma instância compartilhada para a aplicação, com construtor público, sem acesso estático e com o tempo de vida em um único lugar visível.
- **`Lazy<T>` quando o padrão for realmente necessário.** Quando um ponto de acesso estático é inevitável (ponto de entrada de uma biblioteca, código que não pode receber dependências), use `Lazy<T>` ou um campo `static readonly`. Evite o double-checked locking escrito à mão.
- **Outros riscos.** Um singleton que mantém estado mutável precisa de sincronização própria. Um que implementa `IDisposable` precisa de um dono claro. Um que depende de outro singleton cria uma ordem de inicialização oculta. Classes estáticas não podem implementar interfaces nem ser injetadas.
- **Não confunda "precisa de uma instância" com "precisa de acesso global".** A primeira é uma decisão de tempo de vida; a segunda quase sempre pode ser evitada.

## Padrões relacionados
- [Abstract Factory](abstract-factory.md): uma fábrica concreta costuma ser uma única instância compartilhada, embora também possa simplesmente ser passada como parâmetro.
- [Builder](builder.md): um builder pode ser compartilhado, mas geralmente é melhor como objeto transient.
- [Prototype](prototype.md): um gerenciador de protótipos costuma ser uma única instância compartilhada.

## Verificação
- O construtor é privado (ou o registro de DI é a única forma de obter a instância) e a criação é segura para threads.
- Os consumidores dependem de uma interface, e pelo menos um teste executa um consumidor com uma implementação falsa em vez do singleton real.
- Nada mutável é exposto sem sincronização, e nenhum teste depende da ordem de outros testes.
- Confirme de novo que "exatamente uma instância" é um requisito real, e não só conveniência de acesso; se for só conveniência, passe o objeto adiante.
