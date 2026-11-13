# Encapsular Classes com Factory (Encapsulate Classes with Factory)

Kerievsky (2004), cap. 6, p. 80. Padrão: Factory. Direção: até.

## Quando usar
Smells: Exposição Indecente (Indecent Exposure).

- Várias classes ficam em um mesmo pacote ou assembly, compartilham uma interface ou classe base, e os clientes não precisam saber que as classes concretas existem. Hoje os clientes chamam os construtores diretamente.
- Escondê-las permite aplicar "programar para uma interface" de forma estrita: os clientes só enxergam o tipo compartilhado. Também reduz o número de classes públicas que um recém-chegado precisa aprender, e reúne os tipos de instância disponíveis em um conjunto de Creation Methods bem nomeados.
- Isso reduz erros. No caso do livro, os programadores às vezes escolhiam a subclasse errada, ou a certa com tipos de argumento errados. Um único lugar com métodos nomeados eliminou isso.
- Custo: cada nova subclasse, e cada mudança no construtor de uma subclasse, exige um Creation Method novo ou alterado na factory. Se as subclasses são adicionadas com frequência, evite esta refatoração ou encapsule apenas as comuns e mantenha as demais públicas.
- Se você distribui código compilado que os clientes não podem modificar, eles também não podem adicionar seus próprios tipos de instância. Leve isso em conta.
- A factory pode acabar sendo ao mesmo tempo uma factory e uma classe base com comportamento. Se isso obscurecer o propósito da classe, separe a factory (Extrair Factory (Extract Factory) em [replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md)).
- Relacionado: [replace-constructors-with-creation-methods.md](replace-constructors-with-creation-methods.md) começa com uma classe e os próprios construtores. Este arquivo faz uma família inteira de subclasses ficar privada atrás do tipo base.

## Mecânica
Use quando as classes compartilham uma interface pública ou superclasse e vivem no mesmo pacote ou assembly.
1. Encontre um cliente que chame um construtor de subclasse para obter um tipo de instância. Aplique Extrair Função (Extract Function) ([extract-function.md](../../fowler/first-set/extract-function.md)) sobre a chamada para obter um método estático público, e depois Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)) para a superclasse (adaptação: para uma interface, uma classe estática ao lado dela faz esse papel). Compile e teste.
2. Troque todos os outros chamadores desse construtor que querem o mesmo tipo de instância para usar o Creation Method. Compile e teste.
3. Repita os passos 1 e 2 para os outros tipos de instância que o construtor pode produzir.
4. Torne o construtor da subclasse não público (`internal` ou `private`). Compile.
5. Repita para cada subclasse que você quiser esconder.

## Exemplo
Antes: as três políticas de retentativa são públicas, e os chamadores escolhem uma delas com `new`.

```csharp
using System;

public abstract class RetryPolicy { public abstract TimeSpan Delay(int attempt); }
public class NoRetry : RetryPolicy { public override TimeSpan Delay(int attempt) => TimeSpan.Zero; }
public class FixedRetry : RetryPolicy { public override TimeSpan Delay(int attempt) => TimeSpan.FromSeconds(2); }
public class ExponentialRetry : RetryPolicy { public override TimeSpan Delay(int attempt) => TimeSpan.FromSeconds(Math.Pow(2, attempt)); }

public static class Caller
{
    public static RetryPolicy Pick() => new ExponentialRetry();
}
```

Depois: as subclasses são classes aninhadas e privadas de `RetryPolicy`, que agora serve como factory. Os chamadores enxergam apenas o tipo base.

```csharp
using System;

public abstract class RetryPolicy
{
    public static RetryPolicy None() => new NoRetry();
    public static RetryPolicy Fixed() => new FixedRetry();
    public static RetryPolicy Exponential() => new ExponentialRetry();

    public abstract TimeSpan Delay(int attempt);

    private sealed class NoRetry : RetryPolicy { public override TimeSpan Delay(int attempt) => TimeSpan.Zero; }
    private sealed class FixedRetry : RetryPolicy { public override TimeSpan Delay(int attempt) => TimeSpan.FromSeconds(2); }
    private sealed class ExponentialRetry : RetryPolicy { public override TimeSpan Delay(int attempt) => TimeSpan.FromSeconds(Math.Pow(2, attempt)); }
}

public static class Caller
{
    public static RetryPolicy Pick() => RetryPolicy.Exponential();
}
```

O mesmo formato aparece nos invólucros (wrappers) da biblioteca padrão que tornam uma coleção somente leitura: as classes proxy ficam escondidas, e métodos estáticos as devolvem como o tipo de interface comum. O livro chama isso de variação de classe interna.

## Notas (C#)
- Classes aninhadas `private` são a forma mais estrita. Quando as subclasses estão em arquivos separados, torne-as `internal` com construtores `internal`, e coloque os Creation Methods em uma classe pública no mesmo assembly.
- Testes que precisam de um tipo concreto podem usar `InternalsVisibleTo`, ou testar pela factory.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum código fora do assembly (ou fora da classe base, para tipos aninhados) se refere às classes concretas.
- Cada Creation Method devolve o tipo compartilhado, não o concreto.
