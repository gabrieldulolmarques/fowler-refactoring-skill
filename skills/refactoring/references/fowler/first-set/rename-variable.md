# Renomear Variável (Rename Variable)

Fowler (2018), cap. 6, p. 137. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smell: Nome Misterioso (Mysterious Name). Quanto maior o alcance de um nome, mais ele importa:

- Uma variável local em uma lambda de uma linha ou em uma função curta pode continuar concisa; o contexto a explica.
- Um campo de longa vida, ou qualquer coisa usada em muitas funções ou arquivos, merece o nome mais
  cuidadoso.

Os nomes dão errado por alguns motivos: foram escolhidos com pressa, o entendimento do
problema mudou, ou o código agora faz outra coisa.

Não faça isto à mão para uma variável que pertence a uma API publicada, em que chamadores que você
não pode editar ainda usam o nome antigo.

## Mecânica
1. Se a variável é muito usada, aplique antes Encapsular Variável (Encapsulate Variable) ([encapsulate-variable.md](encapsulate-variable.md)), para que a renomeação toque em um só lugar.
2. Encontre toda referência e altere cada uma. Use a renomeação da IDE ou do compilador, não apenas busca de texto, e procure também o nome antigo onde o compilador não enxerga: reflexão, nomes serializados, chaves de configuração, templates de string.
3. Se a variável nunca é reatribuída, você pode fazer aos poucos: declare o novo nome, faça o nome antigo copiar o novo (para que o antigo seja fácil de restaurar se um teste falhar), mova as referências em pequenos lotes testando entre os lotes, depois apague o nome antigo.
4. Faça o build e teste.

Se a variável é visível para código fora da sua base de código, ela é publicada e esta
refatoração não se aplica como está.

## Exemplo

Um valor mutável muito usado. Antes:

```csharp
public static class ShippingSettings
{
    public static string dflMethod = "standard";

    public static string Describe(decimal fee) => $"{fee:0.00} via {dflMethod}";
}

// em outro lugar
// ShippingSettings.dflMethod = cart.PreferredMethod;
```

Passo 1, encapsule para que haja um único lugar onde renomear:

```csharp
public static class ShippingSettings
{
    private static string dflMethod = "standard";

    public static string DefaultMethod
    {
        get => dflMethod;
        set => dflMethod = value;
    }

    public static string Describe(decimal fee) => $"{fee:0.00} via {DefaultMethod}";
}

// em outro lugar
// ShippingSettings.DefaultMethod = cart.PreferredMethod;
```

Passo 2, renomeie o campo, agora privado. Mantenha a propriedade em vez de internalizá-la: o valor é muito
usado, então vale manter o encapsulamento.

```csharp
public static class ShippingSettings
{
    private static string defaultMethod = "standard";

    public static string DefaultMethod
    {
        get => defaultMethod;
        set => defaultMethod = value;
    }

    public static string Describe(decimal fee) => $"{fee:0.00} via {DefaultMethod}";
}
```

Renomeando uma constante aos poucos, por cópia:

```csharp
// trecho
// antes
public const decimal fst = 50m;

// durante: os dois existem, e os chamadores migram alguns de cada vez
public const decimal FreeShippingThreshold = 50m;
public const decimal fst = FreeShippingThreshold;

// depois: o nome antigo é apagado quando nada mais o usa
public const decimal FreeShippingThreshold = 50m;
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
