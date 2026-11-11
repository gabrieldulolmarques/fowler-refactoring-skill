# Substituir Exceção por Verificação Prévia (Replace Exception with Precheck)

Fowler, catálogo online: https://refactoring.com/catalog/replaceExceptionWithPrecheck.html. Antes / também: Replace Exception with Test. Inversa: —.

## Quando usar
Existe um `try`/`catch` para tratar uma condição que não é excepcional: o chamador pode saber de antemão que ela pode acontecer, e o bloco catch apenas fornece um valor padrão ou segue o caminho alternativo. Exceções são para falhas inesperadas; usá-las como um desvio esconde o fluxo normal, custa mais em tempo de execução e pode engolir erros reais do mesmo tipo.

Substitua o tratador por um condicional que testa a condição primeiro e só então executa a operação quando for seguro.

Não use quando a condição não pode ser testada de forma confiável antes da chamada (por exemplo, outra thread pode mudá-la nesse intervalo, ou a única forma de saber é tentar a operação, como em muitas operações de arquivo ou de rede, ou a verificação prévia repetiria uma operação cara). Então mantenha a exceção, ou use um método `Try...` que verifica e age em um único passo. Mantenha-a também quando a exceção sinaliza uma falha real que não deve ser silenciosamente substituída por um valor padrão.

## Mecânica
1. Identifique a condição exata que faz a operação lançar a exceção, e o valor ou caminho que o bloco catch usa em resposta.
2. Adicione a verificação como um condicional antes da operação, com o comportamento do bloco catch no seu ramo, deixando o `try`/`catch` no lugar. Compile e teste.
3. Adicione uma asserção ou um log temporário dentro do bloco catch, rode os testes e confirme que ele nunca é alcançado. Se for, a verificação prévia não cobre todos os casos; corrija a condição primeiro.
4. Remova o `try`/`catch`, deixando a operação no ramo seguro. Compile e teste.
5. Remova a asserção ou o log temporário e arrume o condicional restante (por exemplo, com uma cláusula de guarda).

## Exemplo
Antes (`_quantities` é um campo `int[]` de um `Order`, uma entrada por linha):

```csharp
public int GetLineQuantity(int lineIndex)
{
    try
    {
        return _quantities[lineIndex];
    }
    catch (IndexOutOfRangeException)
    {
        return 0;
    }
}
```

Depois:

```csharp
public int GetLineQuantity(int lineIndex)
{
    if (lineIndex < 0 || lineIndex >= _quantities.Length)
        return 0;

    return _quantities[lineIndex];
}
```

## Notas de C#
- Prefira o padrão `TryParse` / `TryGetValue` do framework onde ele existir: ele realiza a verificação e a operação juntas, então não há intervalo entre o teste e o uso. Exemplo: `if (_prices.TryGetValue(sku, out var price)) return price; return 0m;` em vez de capturar `KeyNotFoundException`.
- Um `catch` estreito facilita identificar a condição. Um `catch (Exception)` amplo exige primeiro descobrir qual causa é a pretendida, já que muitas vezes esconde mais de uma.

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento não muda para nenhuma entrada, incluindo os valores de fronteira (primeiro, último e logo fora da faixa válida) que antes disparavam a exceção.
