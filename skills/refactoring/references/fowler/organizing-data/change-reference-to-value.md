# Mudar Referência para Valor (Change Reference to Value)

Fowler (2018), cap. 9, p. 252. Antes / também: —. Inversa: Mudar Valor para Referência (Change Value to Reference)
([change-value-to-reference.md](change-value-to-reference.md)).

## Quando usar
Smell: Dados Mutáveis (Mutable Data). Um objeto aninhado em outro é alterado por atribuição às suas
propriedades, de modo que a mesma instância é atualizada no lugar. Se o objeto interno não tem
identidade própria (dois com o mesmo conteúdo são intercambiáveis), trate-o como um valor:
imutável, substituído por inteiro quando algo muda e igual quando seus campos são iguais.
Valores imutáveis podem ser compartilhados e lidos por várias threads com segurança, já que ninguém pode
modificá-los.

Não aplique quando vários donos precisam compartilhar um mesmo objeto e ver as mudanças uns dos outros. Esse
objeto é uma referência de verdade, e o movimento certo pode ser a refatoração inversa.

## Mecânica
1. Verifique que a classe é imutável ou pode se tornar imutável: nenhum código externo precisa modificar
   a mesma instância e observar a mudança em outro lugar.
2. Remova a mutabilidade um setter por vez, usando
   [remove-setting-method.md](../refactoring-apis/remove-setting-method.md). Primeiro mova os campos para o
   construtor, depois reescreva cada chamador de um setter para que ele construa uma nova instância e a atribua
   ao campo do dono. Teste após cada setter.
3. Adicione igualdade por valor sobre todos os campos, e o hash code correspondente. Escreva testes que
   comparem duas instâncias construídas independentemente com o mesmo conteúdo, instâncias que difiram em
   cada campo, `null` e um objeto de outro tipo.
4. Verifique os chamadores que comparavam as instâncias antigas por identidade, ou as usavam como chaves, e
   atualize-os para a nova igualdade.

## Exemplo
Antes: um pedido possui um endereço mutável, e suas propriedades atualizam esse endereço no lugar.

```csharp
public class PostalAddress
{
    public string Street { get; set; }
    public string City { get; set; }
}

public class Order
{
    private PostalAddress _shippingAddress = new PostalAddress();

    public string ShippingStreet
    {
        get => _shippingAddress.Street;
        set => _shippingAddress.Street = value;
    }

    public string ShippingCity
    {
        get => _shippingAddress.City;
        set => _shippingAddress.City = value;
    }
}
```

Passo 1, remova os setters um por vez. O construtor recebe os campos, e cada setter
de `Order` substitui o endereço inteiro:

```csharp
public class PostalAddress
{
    public PostalAddress(string street, string city)
    {
        Street = street;
        City = city;
    }

    public string Street { get; }
    public string City { get; }
}

public class Order
{
    private PostalAddress _shippingAddress = new PostalAddress(null, null);

    public string ShippingStreet
    {
        get => _shippingAddress.Street;
        set => _shippingAddress = new PostalAddress(value, _shippingAddress.City);
    }

    public string ShippingCity
    {
        get => _shippingAddress.City;
        set => _shippingAddress = new PostalAddress(_shippingAddress.Street, value);
    }
}
```

Passo 2, dê a ele igualdade por valor (aqui à mão; veja as Notas (C#) para a forma mais curta):

```csharp
using System;

public sealed class PostalAddress : IEquatable<PostalAddress>
{
    public PostalAddress(string street, string city)
    {
        Street = street;
        City = city;
    }

    public string Street { get; }
    public string City { get; }

    public bool Equals(PostalAddress other) =>
        other is not null && Street == other.Street && City == other.City;

    public override bool Equals(object obj) => Equals(obj as PostalAddress);

    public override int GetHashCode() => HashCode.Combine(Street, City);
}
```

O comportamento visto de fora de `Order` é o mesmo; `new PostalAddress("A", "B")` agora é igual a
outra instância construída com os mesmos argumentos.

## Notas (C#)
- Um `record`, um `readonly record struct` ou uma classe imutável com igualdade por valor
  (`Equals`/`GetHashCode`) servem. Com um `record PostalAddress(string Street, string City)`,
  a igualdade e o hash code são gerados, e o setter do dono pode ser
  `_shippingAddress = _shippingAddress with { City = value };`.
- Sempre que `Equals` for sobrescrito, sobrescreva `GetHashCode` com os mesmos campos, ou as coleções baseadas
  em hash se comportam mal. Considere também os operadores `==`/`!=` se os chamadores os usam.
- Mantenha os próprios campos do valor imutáveis (ou comparados por valor); caso contrário, o valor ainda pode
  ser alterado por dentro.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os testes de igualdade do passo 3 passam, incluindo `null` e outros tipos.
