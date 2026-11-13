# Extrair Adapter (Extract Adapter)

Kerievsky (2004), cap. 8, p. 258. Padrão: Adapter. Direção: até.

## Quando usar
Smells: Solução Espalhada (Solution Sprawl).

- Uma classe adapta várias versões de um componente, biblioteca ou API, então carrega campos, construtores, métodos e condicionais específicos de cada versão. Comentários como "apague quando deixarmos a versão 1" ficam para sempre, porque ninguém se arrisca a remover código que algo desconhecido ainda pode usar.
- Um adaptador por versão, todos atrás de uma interface comum, mantém cada classe responsável por uma versão. O nome da classe pode até trazer a versão. O programa escolhe o adaptador certo a partir da configuração ou de informações de tempo de execução.
- Adaptadores também protegem você de APIs que mudam rápido e que você não controla.
- Não faça isso antes de as múltiplas versões realmente causarem condicionais ou problemas de manutenção.
- Um adaptador pode esconder um comportamento que o cliente precisa, porque o cliente só enxerga a interface do adaptador. Se for o caso, amplie a interface.
- Um adaptador envolve um único objeto. Se você precisa envolver um subsistema inteiro atrás de uma visão mais simples, isso é um Facade, que é outro padrão.

## Mecânica
Há várias formas de fazer isso. Se uma classe usa condicionais para tratar versões, normalmente você obtém um adaptador por versão aplicando repetidamente Substituir Condicional por Polimorfismo (Replace Conditional with Polymorphism) ([replace-conditional-with-polymorphism.md](../../fowler/conditional-logic/replace-conditional-with-polymorphism.md)). Os passos abaixo cobrem o outro caso comum: uma classe adaptadora existente, com campos e métodos específicos de versão.

1. Identifique o adaptador sobrecarregado, a classe que adapta versões demais.
2. Crie um novo adaptador para uma versão, por Extrair Subclasse (Extract Subclass) (só na 1ª ed.; veja [replace-type-code-with-subclasses.md](../../fowler/inheritance/replace-type-code-with-subclasses.md)) ou por Extrair Classe (Extract Class) ([extract-class.md](../../fowler/encapsulation/extract-class.md)). Mova ou copie para ele cada campo e método usado apenas por essa versão. Talvez seja preciso ampliar a visibilidade de alguns membros do adaptador sobrecarregado e inicializar alguns campos pelo construtor da nova classe, o que muda o código que a constrói. Compile e teste.
3. Repita o passo 2 para cada versão, até que o adaptador sobrecarregado não contenha mais código específico de versão.
4. Remova a duplicação entre os novos adaptadores com Subir Método (Pull Up Method) ([pull-up-method.md](../../fowler/inheritance/pull-up-method.md)) e Formar Template Method (Form Template Method) ([form-template-method.md](form-template-method.md)). Compile e teste.

## Exemplo
Antes: `ExchangeRates` adapta duas versões de um serviço de cotações. Tem dois construtores, um campo anulável por versão e um desvio no único método.

```csharp
using System;

// Versão antiga do serviço externo.
public class LegacyRateService
{
    public decimal Rate(string pair) => pair == "USD/BRL" ? 5m : 1m;
}

// Nova versão do serviço externo.
public record RateQuote(decimal Value, DateTime At);
public class RateServiceV2
{
    public RateQuote Quote(string from, string to) =>
        new(from == "USD" && to == "BRL" ? 5m : 1m, DateTime.UtcNow);
}

public class ExchangeRates
{
    private readonly LegacyRateService? _legacy;
    private readonly RateServiceV2? _v2;

    public ExchangeRates(LegacyRateService legacy) => _legacy = legacy;
    public ExchangeRates(RateServiceV2 v2) => _v2 = v2;

    public decimal Convert(decimal amount, string from, string to)
    {
        var rate = _legacy != null
            ? _legacy.Rate($"{from}/{to}")
            : _v2!.Quote(from, to).Value;
        return Math.Round(amount * rate, 2);
    }
}
```

Depois: um adaptador por versão, atrás de uma interface comum. O arredondamento compartilhado fica em uma classe base (o passo de Formar Template Method), e cada adaptador implementa apenas como obter uma cotação.

```csharp
using System;

public class LegacyRateService
{
    public decimal Rate(string pair) => pair == "USD/BRL" ? 5m : 1m;
}

public record RateQuote(decimal Value, DateTime At);
public class RateServiceV2
{
    public RateQuote Quote(string from, string to) =>
        new(from == "USD" && to == "BRL" ? 5m : 1m, DateTime.UtcNow);
}

public interface IExchangeRates
{
    decimal Convert(decimal amount, string from, string to);
}

public abstract class ExchangeRates : IExchangeRates
{
    public decimal Convert(decimal amount, string from, string to) =>
        Math.Round(amount * RateFor(from, to), 2);

    protected abstract decimal RateFor(string from, string to);
}

public class LegacyExchangeRates : ExchangeRates
{
    private readonly LegacyRateService _service;
    public LegacyExchangeRates(LegacyRateService service) => _service = service;
    protected override decimal RateFor(string from, string to) => _service.Rate($"{from}/{to}");
}

public class V2ExchangeRates : ExchangeRates
{
    private readonly RateServiceV2 _service;
    public V2ExchangeRates(RateServiceV2 service) => _service = service;
    protected override decimal RateFor(string from, string to) => _service.Quote(from, to).Value;
}
```

Os clientes dependem de `IExchangeRates`; o código de inicialização (ou a configuração) escolhe `LegacyExchangeRates` ou `V2ExchangeRates`. Quando a versão 1 for aposentada, apague uma classe e nada mais.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Cada adaptador tem um teste contra a sua própria versão (ou um fake dela), e a classe antiga sobrecarregada não tem mais campos nem desvios de versão antes de você apagá-la.
