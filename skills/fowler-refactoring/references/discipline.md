# Disciplina de refatoração

Fowler (2018), cap. 2, pp. 45-70, e cap. 4, pp. 85-100. Parafraseado.

## O que conta como refatoração

Uma mudança na estrutura interna que torna o código mais fácil de entender e mais barato de alterar **sem mudar o comportamento observável** (cap. 2, p. 45). É uma cadeia de passos pequenos, cada um deixando o código funcionando. Se o código fica quebrado por dias, não é refatoração. Nada que importe a um usuário pode mudar; um bug que você encontra continua sendo um bug até você terminar e corrigi-lo separadamente.

Ajuste de desempenho é diferente: aceita código mais difícil de ler em troca de velocidade. A refatoração pode acelerar ou desacelerar, porque o seu objetivo é a clareza.

## Dois chapéus

Use um de cada vez (cap. 2, p. 46):

- **Chapéu de funcionalidade:** adicione comportamento e testes; não reestruture.
- **Chapéu de refatoração:** reestruture; não adicione comportamento nem testes (exceto para um caso que você deixou passar). Altere testes só quando uma interface mudou.

Troque com frequência, mas saiba qual deles você está usando.

## Quando refatorar

Principalmente de forma oportunista, como parte de outro trabalho (cap. 2, pp. 50-53):

- **Regra dos três:** tolere a duplicação duas vezes, refatore na terceira.
- **Preparatória:** logo antes de adicionar uma funcionalidade ou corrigir um bug, remodele o código para que a mudança fique fácil.
- **De compreensão:** quando você teve que quebrar a cabeça com um código, devolva ao código o que aprendeu (nomes, estrutura).
- **Limpeza de passagem:** pequenas limpezas pelo caminho; anote as maiores e volte depois.
- **Planejada/de longo prazo:** rara; distribua os grandes esforços pelas mudanças do dia a dia em vez de um bloco de tempo.

## O ciclo

1. **Base verde.** Execute os testes. Não comece nem continue enquanto algum teste falhar. Se uma falha aparecer no meio do caminho, volte à última versão que passava.
2. **Um passo pequeno** da mecânica da refatoração.
3. **Compile e execute os testes.** Compilar sozinho não basta: referências por nome, reflexão e dados serializados são invisíveis para o compilador.
4. **Faça commit** após cada refatoração concluída e verde. Faça commits com mais frequência se um passo for arriscado. Manter commits de refatoração separados dos de funcionalidade é um padrão, não uma lei: o livro (p. 53) deixa isso a critério da equipe. O padrão tem uma vantagem prática, já que cada commit de refatoração vira um ponto seguro para reverter.
5. **Repita** com o próximo smell.

Passos pequenos parecem mais lentos, mas são mais rápidos no total: você quase nunca depura, porque a última mudança é a única suspeita.

## Testes primeiro (cap. 4)

A refatoração precisa de testes autoverificáveis: eles rodam sozinhos e informam passou/falhou. São o detector dos erros que você vai cometer.

- Não há testes em torno do código que você quer alterar? Escreva-os primeiro, depois refatore.
- Escreva o teste do novo comportamento antes do código quando puder; isso o obriga a pensar na interface.
- Teste o que pode quebrar (orientado a risco), não todo getter e setter. Alguns testes na lógica mais arriscada valem mais que um plano de cobertura completa que nunca é escrito.
- **Veja cada novo teste falhar uma vez.** Quebre o código temporariamente (por exemplo, inverta uma comparação ou devolva uma constante) e confirme que o teste fica vermelho, depois desfaça. Um teste que não pode falhar não protege nada.
- Sonde os limites: coleções vazias, zero, valores negativos ou fora da faixa, e os caminhos de erro, onde os bugs tendem a se concentrar.
- Mantenha os testes independentes: crie objetos novos por teste em vez de compartilhar uma fixture mutável, para que um teste não possa quebrar outro.
- Use `Introduzir Asserção` (Introduce Assertion) ([introduce-assertion.md](conditional-logic/introduce-assertion.md)) para declarar uma regra que o código assume, de modo que uma violação falhe de forma ruidosa.
- Execute os testes que cobrem o código que você tocou a cada poucos minutos, e a suíte inteira pelo menos uma vez por dia.

## Quando não refatorar

- Código que você não precisa alterar: código feio, mas estável, pode ficar como está.
- Código mais fácil de reescrever do que de remodelar: recomece em vez de uma longa cadeia de passos (cap. 2, p. 55).
- Renomear ou alterar uma interface publicada (usada por código que você não pode editar, como um pacote ou outras equipes) exige uma transição: mantenha a antiga repassando para a nova por um tempo (cap. 2, p. 57).

## Além do livro: código legado sem testes

Não vem dos cap. 2-4 de Fowler. O termo é de Michael Feathers, *Working Effectively with Legacy Code*.

Um **teste de caracterização** fixa o que o código faz hoje (afirma a saída atual), mesmo que essa saída pareça estranha. Use-o antes de reestruturar código que não tem testes.

Prática geral, também fora do livro: tudo o que é referenciado por nome de fora do código (configuração, reflexão, dados serializados, scripts) precisa de uma busca antes de ser renomeado, movido ou removido, porque o compilador não pega uma referência quebrada.

## Mensagem de commit

Uma linha, no formato que o projeto usa para commits, descrevendo uma única refatoração.

## Checklist de verificação (igual para toda refatoração)

- Compila sem novos avisos.
- Os testes passam (os novos testes falharam uma vez antes de passar).
- Commit feito no verde, comportamento inalterado.
