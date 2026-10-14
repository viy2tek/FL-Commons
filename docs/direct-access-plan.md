# Acesso direto: próximo incremento da API

Diretriz: todas as operações pelo contrato FL Commons API, sem serviço Bridge
separado e sem MIDI no caminho principal. MIDI é uma opção de casos específicos.

Escopo atualizado pelo usuário: somente a versão mais recente instalada.
`host.inspect` seleciona a maior versão numérica do executável e filtra processos
pelo caminho verificado dessa versão, sem fallback para builds anteriores.

Primeiro incremento verificável: `host.inspect`, operação somente de leitura que
consulta instalações e processos do FL pelo Windows, sem abrir projetos, iniciar
o FL, enviar teclas, ler memória do processo ou usar funções internas. Retorna
versões dos executáveis, processos observados, identificação verificada por
caminho e limites de cobertura. Presença do FL nunca habilita comandos musicais.

Implementação usa PowerShell do Windows com script constante, sem interpolação
de parâmetros HTTP, sem shell, sem profile e com prazo de 5 segundos. O SDK
expõe a mesma operação. JSON malformado e falhas da consulta retornam erro, não
uma lista vazia que possa ser interpretada como ausência do FL. Busca limitada
a diretórios `Image-Line/FL Studio *` em Program Files e Program Files (x86).
Outras instalações são desconhecidas. Processo sem acesso ao caminho aparece
com identidade não verificada; isso não é evidência de acesso ao projeto.

Testes: formatos válidos/inválidos, timeout, plataforma não suportada, ausência
de MIDI, API/SDK HTTP e ausência de sucesso falso no transporte. Validar também
a consulta real neste Windows, registrando as versões efetivamente retornadas.

Depois: avaliar o SDK oficial de plugins e outras interfaces documentadas por
domínio (transporte, mixer, canais, padrões e plugins). O SDK permite plugins
nativos, mas não foi demonstrado que ele exponha todos esses domínios; seu pacote
e termos ainda precisam ser examinados. Não gerar endpoints que finjam operações
reais nem usar APIs privadas em produção. Análise Ghidra de um fixture não prova
acesso às funções do FL Studio.
