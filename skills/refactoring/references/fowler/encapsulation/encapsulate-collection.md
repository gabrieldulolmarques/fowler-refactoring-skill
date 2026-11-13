# Encapsular Coleção (Encapsulate Collection)

Fowler (2018), cap. 7, p. 170. Nome anterior / outro nome: —. Inversa: —.

## Quando usar
Smell: nenhum específico no livro (relacionado: Dados Mutáveis (Mutable Data)). A motivação é encapsular
dados mutáveis, para que a coleção não possa ser alterada de qualquer lugar.

- Uma classe tem uma propriedade que retorna sua coleção interna, então qualquer chamador pode adicionar, remover
  ou reordenar itens e o dono nunca fica sabendo.
- O dono tem regras sobre os membros da coleção (limites, totais, validação, notificações de mudança)
  que os chamadores podem contornar hoje.
- Um setter permite que os chamadores substituam a coleção inteira, e eles guardam uma referência a ela.

Uma propriedade sobre o campo protege quem é o dono da lista, não quem a edita.

Evite esconder as coleções por completo (`CountOfLines`, `LineAt(i)`): os chamadores perdem o LINQ. Retorne uma
coleção segura e escolha uma única proteção (cópia ou visão somente leitura) para todos os getters.

## Mecânica
1. Se o campo ainda não estiver atrás de uma propriedade ou de um acessor, aplique antes Encapsular Variável (Encapsulate Variable)
   ([encapsulate-variable.md](../first-set/encapsulate-variable.md)).
2. Adicione métodos no dono para adicionar e remover itens individuais. Decida o que a remoção de um item
   inexistente faz (ignorar, lançar exceção ou deixar o chamador escolher) e registre isso no método.
3. Se houver um setter para a coleção inteira, remova-o quando possível
   ([remove-setting-method.md](../refactoring-apis/remove-setting-method.md)). Se ele precisar ficar, faça-o copiar a coleção recebida
   para o campo em vez de guardar a referência do chamador.
4. Faça o build e execute os testes.
5. Encontre todos os usos da propriedade da coleção. Altere cada chamada que a modifica (`Add`,
   `Remove`, `Clear`, atribuição por indexador, `Sort` no lugar) para usar os novos métodos. Teste após
   cada alteração.
6. Procure qualquer `Add`/`Remove` restante no getter e então altere-o para retornar uma
   visão protegida: uma cópia ou um invólucro (wrapper) somente leitura. Com uma cópia, uma escrita perdida some
   em silêncio, e é por isso que a busca vem primeiro.
7. Execute os testes. Com um invólucro somente leitura, qualquer código que ainda tentava modificar a coleção
   agora falha de forma visível. Com uma cópia, a escrita se perde em silêncio, então só um teste que confira
   o conteúdo resultante a detecta.

## Exemplo

Antes:

```csharp
using System.Collections.Generic;
using System.Linq;

public class Coupon
{
    public Coupon(string code, decimal percentOff) { Code = code; PercentOff = percentOff; }
    public string Code { get; }
    public decimal PercentOff { get; }
}

public class Subscription
{
    public List<Coupon> Coupons { get; set; } = new();
}

public static class Client
{
    public static void Run(Subscription subscription, List<Coupon> loaded)
    {
        subscription.Coupons.Add(new Coupon("WELCOME10", 10m));
        subscription.Coupons = loaded;
        var totalOff = subscription.Coupons.Sum(c => c.PercentOff);
    }
}
```

Depois:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

public class Subscription
{
    private readonly List<Coupon> _coupons = new();

    public IReadOnlyList<Coupon> Coupons => _coupons.ToArray();

    public void AddCoupon(Coupon coupon) => _coupons.Add(coupon);

    public void RemoveCoupon(Coupon coupon)
    {
        if (!_coupons.Remove(coupon))
            throw new InvalidOperationException("The subscription does not have this coupon.");
    }

    public void ReplaceCoupons(IEnumerable<Coupon> coupons)
    {
        var copy = coupons.ToList();
        _coupons.Clear();
        _coupons.AddRange(copy);
    }
}

public static class Client
{
    public static void Run(Subscription subscription, List<Coupon> loaded)
    {
        subscription.AddCoupon(new Coupon("WELCOME10", 10m));
        subscription.ReplaceCoupons(loaded); // o setter foi removido
        var totalOff = subscription.Coupons.Sum(c => c.PercentOff);
    }
}
```

As leituras continuam funcionando com LINQ. As escritas agora passam por `Subscription`, então uma regra
como "no máximo 3 cupons por assinatura" tem um único lugar para morar.

## Notas (C#)
- Exponha `IReadOnlyList<T>` ou `IReadOnlyCollection<T>`, com métodos `Add`/`Remove` no dono.
- Uma interface somente leitura não impede o chamador de converter de volta para `List<T>` e modificá-la.
  Quando isso importa, devolva uma cópia (`ToArray()`, `ToList()`) ou um invólucro como `AsReadOnly()`.
- Uma cópia é um instantâneo: mudanças posteriores no dono não aparecem nela. Um invólucro é uma visão
  ao vivo. Escolha um e seja consistente. Para coleções grandes que são lidas com frequência, um invólucro
  evita o custo da cópia.
- Operações de mutação em uma coleção que você não possui ainda podem causar problemas: `List<T>.Sort()` e
  `Reverse()` alteram a lista no lugar, então copie antes de ordenar o que um getter devolveu.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Nenhum chamador modifica a coleção, exceto pelos métodos do dono.
