# Combinar Funções em Classe (Combine Functions into Class)

Fowler (2018), cap. 6, p. 144. Nome anterior / outro nome: —. Inversa: —. Alternativa:
Combinar Funções em Transformação (Combine Functions into Transform) ([combine-functions-into-transform.md](combine-functions-into-transform.md)).

## Quando usar
Smells: Lista Longa de Parâmetros (Long Parameter List), Dados Mutáveis (Mutable Data), Cirurgia com Espingarda (Shotgun Surgery).

- Várias funções recebem o mesmo registro (ou os mesmos poucos valores) e calculam coisas
  a partir dele. Uma classe torna explícito esse ambiente compartilhado e permite que as chamadas dispensem
  os argumentos repetidos.
- O mesmo valor derivado é calculado diretamente em vários clientes, ou existe um auxiliar mas
  ninguém o encontra porque é uma função livre longe dos dados.
- Os dados de origem podem mudar depois de lidos. Os métodos calculam valores derivados sob demanda,
  então permanecem consistentes com os dados. Uma transformação que copia valores derivados para um novo
  registro fica desatualizada quando a origem muda; prefira a classe nesse caso.
- Prefira uma classe a uma função aninhada em outra função: é mais fácil de testar, e
  é necessária quando mais de uma das funções precisa ficar visível para outro código.

Não use para uma única função (basta movê-la) nem quando as funções não compartilham dados.

## Mecânica
1. Garanta que os dados compartilhados sejam uma única estrutura. Se for um registro solto, dicionário ou tupla,
   envolva-o em uma classe ([encapsulate-record.md](../encapsulation/encapsulate-record.md)). Se for apenas um grupo de argumentos
   separados, agrupe-os primeiro ([introduce-parameter-object.md](introduce-parameter-object.md)).
2. Crie a nova instância onde os dados são obtidos pela primeira vez, para que os clientes guardem o objeto
   em vez dos dados brutos.
3. Mova uma função de cada vez para a classe ([move-function.md](../moving-features/move-function.md)). Os parâmetros que
   agora são membros da classe somem da assinatura. Atualize os chamadores e teste.
4. Renomeie cada função movida se o nome dela repetia o tipo dos dados ou fica ruim como
   método ou propriedade.
5. Substitua cada cálculo duplicado, escrito diretamente nos clientes, por uma chamada ao novo método.
6. Procure lógica nos clientes que trabalhe sobre os dados. Extraia-a
   ([extract-function.md](extract-function.md)) e mova-a também para a classe. Teste após cada uma.

## Exemplo

Antes: funções livres que recebem o mesmo registro mutável.

```csharp
public class CartData
{
    public string Customer { get; set; } = "";
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public bool IsMember { get; set; }
}

public static class CartPricing
{
    public static decimal Subtotal(CartData cart) =>
        cart.Quantity * cart.UnitPrice;

    public static decimal MemberDiscountRate(bool isMember) => isMember ? 0.10m : 0m;

    public static decimal Payable(CartData cart) =>
        Subtotal(cart) * (1 - MemberDiscountRate(cart.IsMember));
}

// clientes
// var data = LoadCart();
// decimal subtotal = data.Quantity * data.UnitPrice;         // fórmula duplicada
// decimal payable = CartPricing.Payable(data);
```

Depois: o registro se torna o estado de uma classe, e as funções se tornam membros.

```csharp
public class Cart
{
    private readonly CartData _data;

    public Cart(CartData data) => _data = data;

    public string Customer => _data.Customer;
    public int Quantity => _data.Quantity;
    public decimal UnitPrice => _data.UnitPrice;
    public bool IsMember => _data.IsMember;

    public decimal Subtotal => Quantity * UnitPrice;

    public decimal MemberDiscountRate => IsMember ? 0.10m : 0m;

    public decimal Payable => Subtotal * (1 - MemberDiscountRate);
}

// clientes
// var cart = new Cart(LoadCart());
// decimal subtotal = cart.Subtotal;
// decimal payable = cart.Payable;
```

Cada valor derivado é calculado sob demanda, então, se `Quantity` mudar depois, `Subtotal` e
`Payable` continuam coerentes com ele. Os chamadores não conseguem distinguir um valor armazenado de um derivado.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
