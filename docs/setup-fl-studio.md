# Integração MIDI opcional: instalação e teste

Este roteiro se aplica apenas a uma ocasião específica que use `--midi`.
Não é requisito do FL Commons API nem prova de integração direta sem MIDI.

O FL Commons utiliza a interface pública de
[MIDI Scripting da Image-Line](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm).
O usuário configura as duas direções MIDI explicitamente. Nenhuma instalação
do FL Studio é alterada pela ferramenta de preparação.

1. Use uma cópia legítima do FL Studio e uma sessão descartável. Confirme que
   seu build recebe e envia SysEx sem travar. Há um
   [relato no fórum oficial](https://forum.image-line.com/viewtopic.php?t=342637)
   sobre falha em builds 26; este projeto não comprova resolução desse relato.
2. Disponibilize dois caminhos MIDI: **Bridge → FL** e **FL → Bridge**. No Windows,
   escolha um roteador/driver permitido e configure-o por sua conta. Não é
   incluído, instalado ou licenciado pelo FL Commons. Evite loops de feedback,
   portas compartilhadas com controladores e limitação/filtragem de SysEx.
3. Instale o extra MIDI no ambiente Python: `python -m pip install '.[midi]'`.
   Liste nomes: `python -m fl_commons ports`. Escolha nomes exatos e únicos.
4. Gere um token aleatório como no README. Opcionalmente defina também
   `FL_COMMONS_MIDI_KEY` com outra chave aleatória; na ausência dela, usa-se o
   token HTTP como chave MIDI. Mantenha as mesmas chaves entre as execuções.
5. Execute `python -m fl_commons prepare-adapter --output adapter-bundle`.
   O destino deve ser novo; o comando não sobrescreve bundles existentes.
6. Copie o conteúdo do bundle para uma nova pasta `FL Commons` no diretório
   **User data folder → Settings → Hardware** do FL. O local é configurável;
   não assuma que ele é a pasta padrão de Documents. A pasta deve conter
   `device_FLCommons.py`, `flcommons_config.py` e `flcommons_wire/` juntos.
7. Em MIDI Settings, habilite a entrada de **Bridge → FL**, escolha o controlador
   **FL Commons** e defina um número de porta disponível. Habilite a saída
   **FL → Bridge** com o mesmo número. Esta ligação permite `device.midiOutSysex`.
8. Inicie `python -m fl_commons serve --midi --input 'FL → Bridge' --output 'Bridge → FL'`
   substituindo pelos nomes reais vistos no passo 3. Não use `--demo`.
9. Consulte `client.capabilities()`. Deve retornar `mode: fl-studio`, a versão
   reportada por `ui.getVersion()`, a versão da API de `general.getVersion()` e
   apenas comandos cujas funções documentadas estão disponíveis.
10. Comece por `transport.state`. Só então teste start/stop numa sessão descartável.
    Registre build, edição, SO, Python embutido, backend, roteador e resultado.

Se não houver resposta, confira chave, ligação das portas, console do script,
callbacks OnInit/OnSysEx/OnIdle e suporte a SysEx. O servidor não deduz a
configuração nem tenta portas diferentes automaticamente. Se uma porta física
desconectar, reinicie o serviço após reconectá-la. Se só o script reiniciar,
refaça a negociação com `capabilities()`; uma escrita antiga recebe 409 e não é
reenviada. O adaptador permite até 16 clientes por ciclo de vida; recarregar o
script renova esse limite.

O script é escrito sem dependências externas e usa sintaxe compatível com Python
3.9. A disponibilidade de módulos padrão e o tipo aceito pela saída SysEx precisam
ser verificados no Python embutido do build usado. A existência do FL instalado
neste computador não constitui um teste dessa integração.
