# Retornar Valor Modificado (Return Modified Value)

Fowler (2018), só na edição web (não está no livro impresso); resumo em https://refactoring.com/catalog/returnModifiedValue.html. Antes / também: —. Inversa: —.

## Quando usar
Smell: nenhum específico (só na edição web; relacionados: Dados Mutáveis (Mutable Data), Função Longa (Long Function)).
- Uma função lê algumas entradas, calcula um valor e o armazena em uma variável declarada fora dela (um campo, uma variável local capturada pelo chamador, um acumulador compartilhado), sem retornar nada.
- Quem lê o código chamador não consegue saber que a chamada produz um valor, nem qual variável ela alimenta.
- Você quer extrair, mover ou reordenar esse código e a escrita oculta torna isso arriscado.

Pule quando a função atualiza várias variáveis de uma vez (retorne um pequeno registro, ou divida a função primeiro) ou quando alterar estado compartilhado é o objetivo inteiro da operação.

## Mecânica
1. Faça a função retornar a variável que ela modifica e, no ponto de chamada, atribua o valor retornado a essa variável. Compile e teste.
2. Dentro da função, declare uma variável local para o valor que ela retorna, começando de onde o chamador começava, e atualize a local em vez da variável externa. A inicialização no chamador agora é ignorada; mudá-la temporariamente é um jeito rápido de confirmar isso. Compile e teste.
   - Se a função acumula sobre um valor deixado por chamadas anteriores, inicie a local no valor identidade (`0` para uma soma, uma lista vazia) e faça o chamador combinar o resultado com a sua variável.
3. Junte a declaração com o cálculo onde der, e torne a variável que recebe o valor somente leitura se nada mais a altera. Compile e teste.
4. Renomeie a variável dentro da função para refletir o novo papel (muitas vezes `result`), e remova a variável externa se nada mais precisar dela. Compile e teste.

## Exemplo
Antes:

```csharp
using System.Collections.Generic;

public class DeliveryReport
{
    private int _delivered;

    private void CountDelivered(IReadOnlyList<DeliveryAttempt> attempts)
    {
        foreach (var attempt in attempts)
        {
            if (attempt.Succeeded)
                _delivered += 1;
        }
    }

    public int Summarize(IReadOnlyList<DeliveryAttempt> attempts)
    {
        _delivered = 0;
        CountDelivered(attempts);
        return _delivered;
    }
}

public class DeliveryAttempt
{
    public DeliveryAttempt(bool succeeded, int errorCode)
    {
        Succeeded = succeeded;
        ErrorCode = errorCode;
    }

    public bool Succeeded { get; }
    public int ErrorCode { get; }
}
```

Depois:

```csharp
using System.Collections.Generic;

public class DeliveryReport
{
    private int CountDelivered(IReadOnlyList<DeliveryAttempt> attempts)
    {
        var result = 0;
        foreach (var attempt in attempts)
        {
            if (attempt.Succeeded)
                result += 1;
        }
        return result;
    }

    public int Summarize(IReadOnlyList<DeliveryAttempt> attempts)
    {
        return CountDelivered(attempts);
    }
}
```

O comportamento é o mesmo, inclusive nas chamadas repetidas (o "antes" zera o campo no início de `Summarize`), com o campo removido e o fluxo de dados visível na chamada.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
