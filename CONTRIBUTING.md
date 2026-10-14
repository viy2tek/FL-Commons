# Contribuir com FL Commons

O produto é uma API independente. Não introduza dependência obrigatória de MIDI,
MIDI Scripting ou de um serviço Bridge separado. Toda funcionalidade deve ser
exposta pelo contrato da API; MIDI fica restrito a integrações opcionais para
casos específicos. Não anuncie capacidade real apoiada apenas em uma simulação.

O nome descreve um bem comum: integrações acessíveis, interfaces abertas e
decisões transparentes. A autoria dos commits e contribuições é preservada;
ninguém precisa usar o nome ou identidade pessoal de um fundador como marca.

Antes de propor uma capacidade, identifique a interface oficial, versões da API,
parâmetros, efeitos e erros. Inclua testes do contrato e um registro separado de
teste real no FL. Função presente, executável instalado e teste simulado não são
evidência de compatibilidade. Não adicione engenharia reversa, injeção ou APIs
privadas ao núcleo estável. Veja a trilha de pesquisa em `research/README.md`.

Execute `python -m unittest discover -s tests -v`. Prefira a biblioteca padrão e
adicione dependências apenas com propósito e licença verificados. Não copie
implementações ou recursos da Image-Line. Contribuições originais são recebidas
sob a licença MIT do projeto; revise direitos antes de enviar código de terceiros.

Quando um repositório público for criado, revisão aberta decidirá a aceitação de
mudanças. Nenhuma organização, grupo de mantenedores, registro de marca ou apoio
da Image-Line foi estabelecido por esta entrega. Discussões devem respeitar
colaboradores e relatar divergências com evidências técnicas.
