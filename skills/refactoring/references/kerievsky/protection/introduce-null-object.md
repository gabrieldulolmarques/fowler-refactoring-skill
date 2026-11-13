# Introduzir Null Object (Introduce Null Object)

Kerievsky (2004), cap. 9, p. 301. Padrão: Null Object. Direção: até.

## Quando usar
Smells: Complexidade Condicional (Conditional Complexity), Código Duplicado (Duplicated Code).

- A mesma verificação de nulo no mesmo campo aparece em vários lugares, cada um com o mesmo fallback (não fazer nada, ou devolver um padrão). Um código novo que esquece a verificação ainda pode falhar com um erro de nulo.
- Um Null Object é uma instância do mesmo tipo que não faz nada ou devolve padrões inofensivos, então os chamadores sempre podem chamá-lo. O campo o referencia até que um objeto real seja atribuído.
- Ele deve encolher o código ou mantê-lo do mesmo tamanho. Se o null object acrescentar mais linhas do que as verificações que remove, não o use.
- Desvantagens: ele complica um design que tem apenas uma ou duas verificações de nulo; programadores que não o conhecem ainda podem escrever verificações que nunca disparam; e um null object baseado em subclasse precisa sobrescrever todo método público adicionado depois à sua base. Implementar uma interface evita esse último risco.
- Relação com Fowler: [introduce-special-case.md](../../fowler/conditional-logic/introduce-special-case.md) cobre o caso geral. A mecânica de Kerievsky mira um caso mais restrito e comum: uma classe tem verificações de nulo em um campo apenas porque o campo é usado antes de receber pela primeira vez um valor real.

## Mecânica
Siga [introduce-special-case.md](../../fowler/conditional-logic/introduce-special-case.md) quando a lógica de nulo existir por qualquer outro motivo (por exemplo, uma busca que não encontra nada). Para o caso de uso precoce, a classe de origem é aquela que deve ser protegida contra nulos:

1. Crie o null object: faça uma nova classe implementar a interface da classe de origem e, se essa interface ainda não existir, extraia-a antes (Extrair Interface (Extract Interface), só na 1ª ed.). A alternativa é criar uma subclasse vazia da classe de origem (Extrair Subclasse (Extract Subclass), só na 1ª ed.). Compile.
2. Para uma verificação de nulo, sobrescreva o método invocado no null object com o comportamento de fallback. Compile. Repita para as outras verificações da classe de origem.
3. Em uma classe que tem verificações de nulo, inicialize o campo com um null object no momento mais cedo possível, normalmente na construção. Deixe as atribuições existentes de objetos reais como estão; a nova atribuição apenas vem antes. Compile.
4. Remova toda verificação de nulo nesse campo na classe. Compile e teste.
5. Repita os passos 3 e 4 para cada classe que tenha a verificação.

Se muitos null objects forem criados, veja se [limit-instantiation-with-singleton.md](../protection/limit-instantiation-with-singleton.md) vale a pena, depois de medir o desempenho.

## Exemplo
Antes: um portão de flags recebe sua loja de flags compartilhada só depois que a configuração é carregada, então cada uso verifica nulo. Veja o arquivo de Fowler para a forma geral; aqui está o caso de uso precoce.

```csharp
public interface IFlagStore
{
    void Refresh();
    void Kill(string flagName);
}

public class FeatureGate
{
    private IFlagStore? _store;

    public void AttachStore(IFlagStore store) => _store = store;

    public void Refresh()
    {
        if (_store != null)
            _store.Refresh();
    }

    public void KillSwitch(string flagName)
    {
        if (_store != null)
            _store.Kill(flagName);
    }
}
```

Depois: o campo começa como uma loja que não faz nada, e as verificações desaparecem.

```csharp
public sealed class NullFlagStore : IFlagStore
{
    public void Refresh() { }
    public void Kill(string flagName) { }
}

public class FeatureGate
{
    private IFlagStore _store = new NullFlagStore();

    public void AttachStore(IFlagStore store) => _store = store;

    public void Refresh() => _store.Refresh();

    public void KillSwitch(string flagName) => _store.Kill(flagName);
}
```

## Notas (C#)
- Com tipos de referência anuláveis ativados, o campo muda de `IFlagStore?` para `IFlagStore`, e o compilador então deixa de emitir alerta sobre ele.
- Um null object sem estado pode ser uma instância estática compartilhada (`NullFlagStore.Instance`).
## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhuma verificação de nulo no campo permanece, e um teste que chama os métodos antes de qualquer objeto real ser anexado passa sem exceção.
- Ninguém dependia de um null devolvido para significar "ausente"; procure chamadores que o testem.
