# Substituir Literal Mágico (Replace Magic Literal)

Fowler (2018), só na edição web (não está no livro impresso); resumo em https://refactoring.com/catalog/replaceMagicLiteral.html. Antes / também: Replace Magic Number with Symbolic Constant. Inversa: —.

## Quando usar
Um valor literal aparece em uma expressão e o seu significado precisa ser adivinhado: uma taxa de imposto, uma unidade de tempo, uma constante física, uma string de status, um limite de tamanho. O mesmo valor repetido em vários lugares é pior, porque uma mudança exige encontrar toda cópia e distinguir as que significam a mesma coisa das que só parecem iguais.

Não extraia todo literal. `0`, `1`, `""` ou `-1` em um papel óbvio (início de laço, verificação de vazio, "não encontrado") em geral são mais claros como estão. Quando o literal é na verdade um conjunto de alternativas relacionadas, um `enum` ou um tipo é um lugar melhor do que uma constante solta.

## Mecânica
1. Declare uma constante com um nome que diga o que o valor significa, não o que ele é (`StandardGravity`, não `NineEightOne`).
2. Encontre as ocorrências do literal. Para cada uma, decida se ela tem o mesmo significado que a constante; valores iguais com significados diferentes ganham suas próprias constantes ou ficam como estão.
3. Substitua uma ocorrência pela constante. Compile e teste.
4. Repita para as demais ocorrências daquele significado, testando ao longo do caminho.
5. Para conferir o resultado, mude temporariamente o valor da constante e veja se os testes percebem em todos os lugares onde deveriam. Nem sempre é possível, mas quando é, é uma verificação barata.

## Exemplo
Antes:

```csharp
public class TemperatureConverter
{
    public double ToKelvin(double celsius)
    {
        return celsius + 273.15;
    }

    public double ToCelsius(double kelvin)
    {
        return kelvin - 273.15;
    }
}
```

Depois:

```csharp
public class TemperatureConverter
{
    private const double KelvinOffset = 273.15;

    public double ToKelvin(double celsius)
    {
        return celsius + KelvinOffset;
    }

    public double ToCelsius(double kelvin)
    {
        return kelvin - KelvinOffset;
    }
}
```

O comportamento não muda, e a relação entre os dois métodos agora fica visível.

## Notas (C#)
- `const` se limita a tipos primitivos, `string` e `null`. Use-o para valores de tempo de compilação, e `static readonly` para o resto (calculado na inicialização, ou de um tipo que não pode ser `const`).
- Um `const` de outro assembly é embutido em tempo de compilação, então mudar seu valor exige recompilar os consumidores; prefira `static readonly` para valores públicos que possam mudar.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Busque no código o literal antigo para confirmar que nenhuma ocorrência com esse significado restou, e que ocorrências do mesmo valor com outro significado foram deixadas em paz.
