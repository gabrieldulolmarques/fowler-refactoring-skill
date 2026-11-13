# Internalizar Singleton (Inline Singleton)

Kerievsky (2004), cap. 6, p. 114. Padrão: Singleton. Direção: longe.

## Quando usar
Smells: Classe Preguiçosa (Lazy Class).

- O código precisa de um objeto, mas não precisa de um jeito global de alcançá-lo. O livro chama o hábito de criar Singletons demais de Singletonite (Singletonitis), e sua resposta para "quando um Singleton é desnecessário?" é: na maioria das vezes.
- Passar o objeto como parâmetro costuma ser mais simples do que lê-lo de um global. Um Singleton também é desnecessário quando existe por um pequeno ganho de velocidade ou memória, ou quando um código profundo em uma camada busca um recurso que não pertence àquela camada.
- Estado global prejudica os testes: cada teste que altera a instância compartilhada precisa salvá-la e restaurá-la. O livro cita uma equipe que gastou meia hora passando uma tabela compartilhada de taxas de câmbio como parâmetro explícito e terminou com um design mais limpo e testes estáveis.
- Alguns globais são aceitáveis. Se um Singleton ou um Registry (um objeto bem conhecido usado para encontrar outros objetos) realmente for o design certo, mantenha-o. Trate qualquer global como culpado até que se prove necessário.
- Benefícios: as colaborações ficam visíveis; não é preciso código para proteger uma única instância. Custo: quando o objeto precisa atravessar muitas camadas, passá-lo fica desajeitado.
- O movimento oposto é [limit-instantiation-with-singleton.md](../protection/limit-instantiation-with-singleton.md), para o caso raro em que uma única instância é uma necessidade real.

## Mecânica
São as mesmas de Internalizar Classe (Inline Class) ([inline-class.md](../../fowler/encapsulation/inline-class.md)). A *classe absorvedora* é a que assume o trabalho do Singleton.
1. Declare os membros públicos do Singleton na classe absorvedora e faça-os delegar ao Singleton. Remova `static` deles, a menos que a classe absorvedora seja ela mesma um Singleton.
2. Troque cada referência de cliente ao Singleton para apontar para a classe absorvedora. Compile e teste.
3. Mova os membros restantes do Singleton para a classe absorvedora, um de cada vez, com Mover Função (Move Function) ([move-function.md](../../fowler/moving-features/move-function.md)) e Mover Campo (Move Field) ([move-field.md](../../fowler/moving-features/move-field.md)), até não sobrar nada. Remova `static` como no passo 1. Compile e teste após cada um.
4. Apague o Singleton.

Quando a classe absorvedora é um cliente ou um colaborador que já mantém o objeto, o resultado final é que o objeto lhe é entregue (pelo construtor ou por parâmetro) em vez de ser procurado.

## Exemplo
Antes: `EndpointRegistry` é um global que `ReportClient` lê. Testes que precisam de outra URL base têm de alterá-la e depois devolvê-la ao valor original.

```csharp
public class EndpointConfig { public virtual string BaseUrl => "https://api.example.test"; }

public static class EndpointRegistry
{
    public static EndpointConfig Config { get; set; } = new();
}

public class ReportClient
{
    public string UrlFor(string path) => EndpointRegistry.Config.BaseUrl + path;
}
```

Depois: `ReportClient` recebe o `EndpointConfig` que usa. `EndpointRegistry` é excluída. Os chamadores passam a configuração, e um teste passa a sua própria.

```csharp
public class EndpointConfig { public virtual string BaseUrl => "https://api.example.test"; }

public class ReportClient
{
    private readonly EndpointConfig _config;
    public ReportClient(EndpointConfig config) { _config = config; }

    public string UrlFor(string path) => _config.BaseUrl + path;
}
```

Em passos: primeiro `ReportClient` ganha uma propriedade `Config` que devolve `EndpointRegistry.Config`, os chamadores passam a usá-la, depois o campo é movido para dentro e `EndpointRegistry` é removida.

## Notas (C#)
- Uma `static class` ou uma classe com uma propriedade estática `Instance` são Singletons para este fim. A refatoração é a mesma.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Uma busca pelo nome do Singleton não encontra nada, e nenhum teste precisa resetar estado compartilhado.
- Toda classe que usava o global agora recebe o objeto na assinatura do construtor ou do método.
