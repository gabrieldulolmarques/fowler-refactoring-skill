# Extrair Função (Extract Function)

Fowler (2018), cap. 6, p. 106. Antes / também: Extract Method. Inversa: Internalizar Função (Inline Function)
([inline-function.md](inline-function.md)).

## Quando usar

Smells: Função Longa (Long Function), Código Duplicado (Duplicated Code), Comentários (Comments), Dados Mutáveis (Mutable Data), Alteração Divergente (Divergent Change), Inveja de
Recursos (Feature Envy), Cadeias de Mensagens (Message Chains), Classe de Dados (Data Class).

- Ler um trecho obriga você a descobrir o que ele faz. Uma função com nome de finalidade
  permite que o leitor pule a implementação.
- Há um comentário acima de um bloco para descrevê-lo. Esse comentário geralmente já contém as palavras
  para o nome da função.
- A mesma lógica, ou uma parecida, aparece em vários lugares (Código Duplicado).
- Dados Mutáveis: código que escreve em estado compartilhado está misturado em um corpo mais longo. Extraí-lo
  isola a atualização, para que possa ser encontrada, protegida ou substituída.
- Alteração Divergente: uma função atende a dois motivos diferentes de mudança. Extraia cada parte para que
  possam ser separadas ou movidas para longe uma da outra.
- Inveja de Recursos e Cadeias de Mensagens: o trecho trabalha principalmente com os dados de outro objeto.
  Extraia-o primeiro, depois mova-o para esse objeto.
- Classe de Dados: os chamadores manipulam os campos de um registro. Extraia esse comportamento e depois mova-o para
  a classe.
- O tamanho não é o critério. Uma única linha merece a própria função quando o nome diz mais que
  o código. Quando o melhor nome que você encontra só repete o código, deixe-o inline.
- Não evite a extração por medo do custo da chamada. Meça primeiro.

## Mecânica

1. Escolha um nome que declare a finalidade do trecho, não a implementação. Se nenhum vier,
   reconsidere extrair. O nome pode ser refinado depois.
2. Crie a nova função e copie o trecho para dentro dela. Deixe o original no lugar por enquanto.
   Se a linguagem tiver funções aninhadas, você pode declarar a nova dentro da função de
   origem (veja as notas de C# sobre funções locais).
3. Classifique as variáveis que o trecho toca e que pertencem à função de origem (parâmetros e
   temporárias), conforme o que o trecho faz com elas:
   - Apenas lidas, ou um objeto/coleção que você modifica pela referência: passe-as como
     argumentos; nenhum retorno é necessário.
   - Declaradas fora, mas usadas apenas pelo trecho: mova a declaração para dentro da nova
     função. Se a declaração estiver longe do trecho, Deslocar Instruções (Slide Statements)
     ([slide-statements.md](../moving-features/slide-statements.md)) a traz primeiro para perto do uso.
   - Escritas pelo trecho e necessárias depois dele: se houver exatamente uma, faça a nova
     função devolvê-la, como uma consulta.
   - Vários valores escritos: não extraia ainda. Simplifique primeiro com Dividir Variável (Split Variable)
     ([split-variable.md](../organizing-data/split-variable.md)) ou Substituir Variável Temporária por Consulta (Replace Temp with Query) ([replace-temp-with-query.md](../encapsulation/replace-temp-with-query.md)),
     ou escolha outro trecho. Como último recurso, devolva uma tupla ou um record pequeno.
   - Um parâmetro que o trecho reatribui: aplique Dividir Variável primeiro, para que ele vire uma
     temporária.
4. Compile. Isso revela qualquer variável que você tenha deixado passar.
5. Substitua o trecho original por uma chamada. Se a função devolve um valor, atribua-o à
   variável que o trecho costumava definir.
6. Execute os testes.
7. Procure o mesmo código, ou um parecido, em outros lugares e substitua-o por uma chamada
   ([replace-inline-code-with-function-call.md](../moving-features/replace-inline-code-with-function-call.md)).
8. Ajuste final opcional: com a chamada em contexto, confira o nome de novo e arrume os nomes
   locais da função extraída.

## Exemplo

Antes: um método mistura um cálculo, uma mutação e uma saída.

```csharp
using System;
using System.Collections.Generic;

public class CartLine
{
    public string Sku { get; set; } = "";
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
}

public class Cart
{
    public List<CartLine> Lines { get; } = new();
    public bool IsMember { get; set; }
}

public class Warehouse
{
    public Dictionary<string, int> Stock { get; } = new();
}

public class CheckoutService
{
    public void Checkout(Cart cart, Warehouse warehouse)
    {
        decimal subtotal = 0;
        foreach (var line in cart.Lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal discount = cart.IsMember && subtotal > 100m ? subtotal * 0.1m : 0m;
        decimal payable = subtotal - discount;

        foreach (var line in cart.Lines)
        {
            warehouse.Stock[line.Sku] -= line.Quantity;
        }

        Console.WriteLine($"itens: {cart.Lines.Count}");
        Console.WriteLine($"pagar: {payable:F2}");
    }
}
```

Depois: cada trecho tem um nome para a sua finalidade. O trecho de preço escreve uma variável
de que o resto do método precisa, então a nova função a devolve. O trecho de estoque altera o
depósito pelo objeto que recebe, então não devolve nada.

```csharp
public class CheckoutService
{
    public void Checkout(Cart cart, Warehouse warehouse)
    {
        decimal payable = AmountPayable(cart);
        ReserveStock(cart, warehouse);
        PrintReceipt(cart, payable);
    }

    private static decimal AmountPayable(Cart cart)
    {
        decimal subtotal = 0;
        foreach (var line in cart.Lines)
        {
            subtotal += line.Quantity * line.UnitPrice;
        }
        decimal discount = cart.IsMember && subtotal > 100m ? subtotal * 0.1m : 0m;
        return subtotal - discount;
    }

    private static void ReserveStock(Cart cart, Warehouse warehouse)
    {
        foreach (var line in cart.Lines)
        {
            warehouse.Stock[line.Sku] -= line.Quantity;
        }
    }

    private static void PrintReceipt(Cart cart, decimal payable)
    {
        Console.WriteLine($"itens: {cart.Lines.Count}");
        Console.WriteLine($"pagar: {payable:F2}");
    }
}
```

Mesmo comportamento, e cada trecho agora tem um nome e uma entrada e saída claras. Extraia um
trecho de cada vez e execute os testes entre as extrações.

## Notas (C#)

- Uma função local (declarada dentro do método) é uma opção para um auxiliar usado em um só lugar.
  Ela pode ler as variáveis do escopo externo sem parâmetros, o que elimina o problema de
  variáveis fora de escopo do passo 3. Mova-a para um método depois, se outro código precisar dela.
- Funções locais que capturam variáveis podem esconder de quanto estado o trecho depende. Para um
  auxiliar que você espera mover, extraia primeiro para um método irmão, para que as dependências apareçam.
- Uma função local `static` (C# 8+) não pode capturar, então suas dependências continuam explícitas como
  parâmetros.
- Um struct passado por valor não é modificado por referência: um trecho que o altera
  só mexe em uma cópia. Devolva o novo valor, ou passe-o com `ref`. Prefira devolver um
  valor ou um record/tupla; use `out`/`ref` como último recurso.

## Verificação

- Compila e os testes passam após cada passo; um commit por refatoração.
- O comportamento observável e os efeitos colaterais não mudam, inclusive a ordem em que
  acontecem.
- O nome da nova função revela a sua finalidade, e quaisquer duplicatas encontradas no passo 7 agora a chamam.
