# Internalizar Singleton (Inline Singleton)

Kerievsky (2004), cap. 6, p. 114. Direção: longe. Padrão: Singleton (GoF, p. 127).

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
Antes: `TaxRegistry` é um global que `InvoiceCalculator` lê. Testes que precisam de outra taxa precisam alterá-lo e depois restaurá-lo.

```csharp
public class TaxTable { public virtual decimal Rate => 0.2m; }

public static class TaxRegistry
{
    public static TaxTable Table { get; set; } = new();
}

public class InvoiceCalculator
{
    public decimal Total(decimal net) => net * (1 + TaxRegistry.Table.Rate);
}
```

Depois: `InvoiceCalculator` recebe o `TaxTable` que usa. `TaxRegistry` é apagado. Os chamadores passam a tabela, e um teste passa a sua própria.

```csharp
public class TaxTable { public virtual decimal Rate => 0.2m; }

public class InvoiceCalculator
{
    private readonly TaxTable _taxTable;
    public InvoiceCalculator(TaxTable taxTable) { _taxTable = taxTable; }

    public decimal Total(decimal net) => net * (1 + _taxTable.Rate);
}
```

Em passos, `InvoiceCalculator` primeiro ganha uma propriedade `Table` que devolve `TaxRegistry.Table`, os chamadores passam a usá-la, depois o campo é movido para dentro e `TaxRegistry` é removido.

## Notas (C#)
- Uma `static class` ou uma classe com uma propriedade `Instance` estática são ambas Singletons para este fim. A refatoração é a mesma.
- Com um contêiner de injeção de dependência, um "tempo de vida singleton" não é o padrão: o objeto continua sendo passado por parâmetro. Não o internalize nesses casos.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Uma busca pelo nome do Singleton não encontra nada, e nenhum teste precisa redefinir o estado compartilhado.
- Toda classe que usava o global agora mostra o objeto na assinatura do construtor ou do método.
