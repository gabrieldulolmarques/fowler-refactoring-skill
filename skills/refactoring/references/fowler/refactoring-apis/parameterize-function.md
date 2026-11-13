# Parametrizar Função (Parameterize Function)

Fowler (2018), cap. 11, p. 310. Nome anterior / outro nome: Parameterize Method. Inversa: —.

## Quando usar
Duas ou mais funções têm a mesma forma e diferem apenas em valores literais. Fundi-las em uma única função com parâmetros remove a duplicação, e
a função única pode então ser reutilizada com valores para os quais ninguém escreveu uma variante.

Não serve quando as funções diferem na estrutura e não nos valores: forçá-las em uma única
função leva a um amontoado de parâmetros e ramificações. Se um parâmetro apenas selecionaria qual
lógica executa, isso é um argumento de flag, não um valor (veja [remove-flag-argument.md](remove-flag-argument.md)).

## Mecânica
1. Escolha uma das funções parecidas como base. Para famílias do tipo faixa, o caso do meio
   costuma ser uma boa escolha, já que tende a usar todos os literais que os outros usam.
2. Adicione um parâmetro para cada literal que varia, usando [change-function-declaration.md](../first-set/change-function-declaration.md)
   (renomeie também a função se o nome antigo não servir mais). Compile.
3. Atualize todo chamador dessa função para passar o literal em que ele antes se apoiava. Teste.
4. No corpo, substitua cada literal pelo seu parâmetro, um de cada vez. Teste após cada um.
5. Para cada função parecida, substitua os seus chamadores por uma chamada à função parametrizada,
   passando os valores daquela função. Teste após cada um. Depois apague a função antiga.
6. Se a função parametrizada não consegue expressar uma variante, ajuste-a para essa variante
   (um valor sentinela, como um limite aberto, costuma funcionar) antes de passar para a próxima.

## Exemplo
Antes:

```csharp
public class MessagePreview
{
    public string SmsPreview(string body)
    {
        return body.Length <= 160 ? body : body.Substring(0, 157) + "...";
    }

    public string PushPreview(string body)
    {
        return body.Length <= 40 ? body : body.Substring(0, 37) + "...";
    }
}
```

Depois:

```csharp
public class MessagePreview
{
    public string Preview(string body, int maxLength)
    {
        return body.Length <= maxLength ? body : body.Substring(0, maxLength - 3) + "...";
    }
}

// chamadores
// preview.Preview(body, 160);  // era SmsPreview
// preview.Preview(body, 40);   // era PushPreview
```

## Verificação
- Compila e os testes passam após cada passo; um commit por refatoração.
