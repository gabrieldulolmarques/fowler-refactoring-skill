# Strategy

Gamma et al. (1995), cap. 5, p. 315. Também conhecido como: Policy. Categoria: comportamental de objeto.

## Intenção
Colocar cada algoritmo de uma família em seu próprio objeto, atrás de uma interface comum, para que o código que usa o algoritmo possa trocar entre eles e o algoritmo possa mudar sem tocar nesse código.

## Quando compensa
- Várias classes diferem apenas na forma como fazem uma mesma coisa, ou uma classe escolhe entre comportamentos com uma cadeia de condicionais.
- Você precisa de variantes do mesmo algoritmo, como uma versão rápida que usa mais memória e uma versão lenta que usa menos.
- Um algoritmo precisa de dados ou estruturas auxiliares que quem chama não deveria ver.
- Benefícios: famílias de algoritmos intercambiáveis; uma alternativa à herança do contexto; os condicionais desaparecem; a escolha pode ser feita em tempo de execução.
- Passivos: quem chama precisa conhecer as estratégias bem o suficiente para escolher uma; a interface comum pode passar dados que algumas estratégias ignoram; há mais objetos.
- Evite quando há um único algoritmo, ou quando a variação nunca importa para quem chama. Um `switch` com dois ramos que nunca crescem está bem.

## Participantes em C#
- **Strategy** (`IRetryPolicy`): interface (ou tipo delegate) que todos os algoritmos implementam.
- **ConcreteStrategy** (`NoRetry`, `FixedDelay`, `ExponentialBackoff`): um algoritmo cada.
- **Context** (`ApiCaller`): guarda uma estratégia, repassa a decisão a ela e entrega os dados de que ela precisa.
- **Client** (`Program`): escolhe a estratégia e a entrega ao contexto, geralmente uma única vez.

## Exemplo (C#)
Um cliente de API HTTP decide quanto tempo esperar entre novas tentativas de uma chamada que falhou. A política de retentativa é uma estratégia: quem chama faz o laço e executa a operação, e a política responde "espere este tempo, ou pare".

```csharp
using System;
using System.Threading.Tasks;

public interface IRetryPolicy
{
    // Delay before retry number `attempt` (1 for the first retry), or null to stop.
    TimeSpan? NextDelay(int attempt);
}

public sealed class NoRetry : IRetryPolicy
{
    public TimeSpan? NextDelay(int attempt) => null;
}

public sealed class FixedDelay : IRetryPolicy
{
    private readonly TimeSpan _delay;
    private readonly int _maxRetries;

    public FixedDelay(TimeSpan delay, int maxRetries)
    {
        _delay = delay;
        _maxRetries = maxRetries;
    }

    public TimeSpan? NextDelay(int attempt) => attempt <= _maxRetries ? _delay : null;
}

public sealed class ExponentialBackoff : IRetryPolicy
{
    private readonly TimeSpan _initial;
    private readonly TimeSpan _cap;
    private readonly int _maxRetries;

    public ExponentialBackoff(TimeSpan initial, TimeSpan cap, int maxRetries)
    {
        _initial = initial;
        _cap = cap;
        _maxRetries = maxRetries;
    }

    public TimeSpan? NextDelay(int attempt)
    {
        if (attempt > _maxRetries) return null;
        var ms = _initial.TotalMilliseconds * Math.Pow(2, attempt - 1);
        return TimeSpan.FromMilliseconds(Math.Min(ms, _cap.TotalMilliseconds));
    }
}

public class ApiCaller
{
    private readonly IRetryPolicy _policy;

    public ApiCaller(IRetryPolicy policy) => _policy = policy;

    public async Task<T> CallAsync<T>(Func<Task<T>> operation)
    {
        for (int attempt = 1; ; attempt++)
        {
            try
            {
                return await operation();
            }
            catch (TimeoutException)
            {
                var delay = _policy.NextDelay(attempt);
                if (delay is null) throw;      // policy says stop
                await Task.Delay(delay.Value);
            }
        }
    }
}

public static class Program
{
    public static async Task Main()
    {
        var calls = 0;
        Task<string> Flaky()
        {
            calls++;
            if (calls < 3) throw new TimeoutException();
            return Task.FromResult("ok");
        }

        var caller = new ApiCaller(new ExponentialBackoff(
            TimeSpan.FromMilliseconds(10), TimeSpan.FromSeconds(1), maxRetries: 5));

        Console.WriteLine(await caller.CallAsync(Flaky));   // ok, after two waits
    }
}
```

## Variações
- **Como os dados chegam à estratégia.** Passe o que ela precisa como argumentos (o exemplo passa o número da tentativa): o par continua desacoplado, mas o contexto pode passar valores que algumas estratégias ignoram. Ou passe o próprio contexto, ou deixe a estratégia guardar uma referência a ele: a estratégia pode pedir exatamente o que precisa, mas o contexto precisa expor mais de si mesmo e os dois ficam acoplados.
- **Seleção em tempo de compilação com genéricos.** Quando a estratégia é fixa na compilação e nunca muda, um parâmetro genérico com restrição de interface (`ApiCaller<TPolicy> where TPolicy : IRetryPolicy`) a vincula estaticamente e, com structs, pode evitar uma chamada virtual.
- **Estratégia opcional.** Deixe o contexto ter um padrão quando nenhuma for fornecida, para que a maioria dos clientes nunca veja o padrão. No exemplo, uma política ausente poderia significar `NoRetry`.
- **Sem estado e compartilhadas.** Estratégias sem campos podem ser compartilhadas por vários contextos. Tudo o que varia por chamada fica no contexto e viaja nos argumentos.

## Riscos e alternativas em C#
- Quando a interface tem um único método, um delegate é a estratégia: `Func<int, TimeSpan?>` substitui `IRetryPolicy`, e uma lambda substitui cada classe. Mantenha a interface quando as estratégias têm configuração, nome, vários métodos ou precisam ser registradas em um contêiner.
- Com injeção de dependência, registre as implementações e injete a desejada (ou um `IEnumerable<IRetryPolicy>` mais um seletor). A escolha da estratégia vira configuração.
- Uma estratégia que mantém estado entre chamadas (um contador, uma janela de circuit breaker) não é segura para compartilhar entre chamadores ou threads. Ou mantenha-a por contexto, ou proteja o estado.
- Estratégias que dependem de aleatoriedade ou de tempo (jitter, `DateTime.Now`) são difíceis de testar. Receba um relógio ou uma fonte aleatória como dependência.
- Uma interface de estratégia moldada para o algoritmo mais complexo força os simples a aceitar parâmetros que nunca usam. Revise a interface quando uma nova estratégia precisar de dados que ela não carrega.

## Padrões relacionados
- [Flyweight](../structural/flyweight.md): objetos de estratégia sem estado são bons flyweights.
- [Template Method](template-method.md): varia parte de um algoritmo por herança, enquanto Strategy varia o algoritmo inteiro por delegação.
- [State](state.md): mesma estrutura, mas um estado é substituído pelo próprio objeto à medida que ele avança em sua vida, e uma estratégia é escolhida de fora.

## Verificação
- O contexto não contém nenhuma ramificação sobre qual algoritmo está em uso, e não cita nenhuma estratégia concreta.
- Adicionar uma variante significa adicionar uma classe (ou uma lambda) e nenhuma mudança no contexto.
- Cada estratégia pode ser testada sozinha, sem o contexto.
- A interface da estratégia carrega apenas os dados que todas as estratégias realmente precisam, ou o dado extra se justifica.
