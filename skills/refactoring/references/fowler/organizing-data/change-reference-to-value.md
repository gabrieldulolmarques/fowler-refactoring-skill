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
Antes: um dispositivo possui uma calibração mutável, e suas propriedades atualizam essa calibração no lugar.

```csharp
public class Calibration
{
    public double Offset { get; set; }
    public double Scale { get; set; } = 1;
}

public class Device
{
    private Calibration _calibration = new Calibration();

    public double CalibrationOffset
    {
        get => _calibration.Offset;
        set => _calibration.Offset = value;
    }

    public double CalibrationScale
    {
        get => _calibration.Scale;
        set => _calibration.Scale = value;
    }
}
```

Passo 1, remova os setters um de cada vez. O construtor recebe os campos, e cada setter de `Device` substitui a calibração inteira:

```csharp
public class Calibration
{
    public Calibration(double offset, double scale)
    {
        Offset = offset;
        Scale = scale;
    }

    public double Offset { get; }
    public double Scale { get; }
}

public class Device
{
    private Calibration _calibration = new Calibration(0, 1);

    public double CalibrationOffset
    {
        get => _calibration.Offset;
        set => _calibration = new Calibration(value, _calibration.Scale);
    }

    public double CalibrationScale
    {
        get => _calibration.Scale;
        set => _calibration = new Calibration(_calibration.Offset, value);
    }
}
```

Passo 2, dê a ela igualdade por valor (aqui à mão; veja as notas de C# para a forma mais curta):

```csharp
// fragment
using System;

public sealed class Calibration : IEquatable<Calibration>
{
    public Calibration(double offset, double scale)
    {
        Offset = offset;
        Scale = scale;
    }

    public double Offset { get; }
    public double Scale { get; }

    public bool Equals(Calibration other) =>
        other is not null && Offset == other.Offset && Scale == other.Scale;

    public override bool Equals(object obj) => Equals(obj as Calibration);

    public override int GetHashCode() => HashCode.Combine(Offset, Scale);
}
```

Visto de fora de `Device`, o comportamento é o mesmo; `new Calibration(0.5, 1)` agora é igual a outra instância criada com os mesmos argumentos.

## Notas (C#)
- Um `record` (C# 9+; no Unity ele precisa de um shim de `IsExternalInit`), um `readonly record struct` ou uma classe imutável com igualdade por valor (`Equals`/`GetHashCode`) servem. Com um `record Calibration(double Offset, double Scale)`, a igualdade e o código de hash são gerados, e o setter do dono pode ser `_calibration = _calibration with { Scale = value };`.
- Sempre que `Equals` for sobrescrito, sobrescreva `GetHashCode` com os mesmos campos, ou as coleções baseadas em hash se comportam mal. Considere também os operadores `==`/`!=` se os chamadores os usarem.
- Mantenha os próprios campos do valor imutáveis (ou comparados por valor); do contrário, o valor ainda pode ser alterado por dentro.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Os testes de igualdade do passo 3 passam, inclusive com `null` e outros tipos.
