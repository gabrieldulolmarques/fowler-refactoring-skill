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
public decimal TotalWithTax(decimal subtotal)
{
    return subtotal * 1.18m;
}

public decimal TaxAmount(decimal subtotal)
{
    return subtotal * 0.18m;
}
```

Depois:

```csharp
private const decimal TaxRate = 0.18m;

public decimal TotalWithTax(decimal subtotal)
{
    return subtotal * (1 + TaxRate);
}

public decimal TaxAmount(decimal subtotal)
{
    return subtotal * TaxRate;
}
```

O comportamento não muda, e a relação entre os dois métodos agora é visível.

## Notas de C#
- `const` se limita a primitivos, `string` e `null`. Use-o para valores de tempo de compilação, `static readonly` para o resto (calculados na inicialização, ou de um tipo que não pode ser `const`).
- Um `const` de outro assembly é incorporado em tempo de compilação, então mudar o seu valor exige recompilar os consumidores; prefira `static readonly` para valores públicos que podem mudar.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- Procure no código o literal antigo para confirmar que nenhuma ocorrência daquele significado restou, e que ocorrências do mesmo valor com outro significado foram deixadas em paz.
