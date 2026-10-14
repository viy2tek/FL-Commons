# Validação desta entrega

## Catálogo amplo de interfaces, 14/10/2026

**42 testes Python passaram**, incluindo filtro/paginação do catálogo, validação
de parâmetros e consulta pelo SDK sobre HTTP autenticado. O catálogo contém 87
seletores FHD_ do SDK fornecido, agrupados em dez domínios inferidos. Cada fato
mantém origem/linha; todos os seletores permanecem não invocáveis pela API.
Esta etapa não constitui análise de todo o código interno do FL Studio.

## SDK e seleção de versão, 14/10/2026

**37 testes Python passaram**, além das assertions do módulo C++ e do teste
SDK Python → HTTP → inspeção real instalada, que retornou somente 26.1.7.5653.

Alvo restrito à versão mais recente instalada: **26.1.7.5653**. A seleção numérica
foi testada inclusive em versões 26.1.9 versus 26.1.10; não retorna executáveis ou
processos de versões anteriores. Versão desconhecida causa erro, não downgrade.
Consulta real confirmou somente os executáveis padrão/scaled do FL Studio 2026.

SDK fpsdk_20210311b recebido do usuário e ZIP íntegro. Módulo C++ original de
Play/Pause e Stop compilado contra três headers externos do SDK. Assertions de
contrato passaram com dispatcher controlado, incluindo bloqueio de thread.
Nenhum plugin foi instalado ou comando executado no FL. O teste do contrato
não certifica compatibilidade com o build-alvo. Veja [avaliação](../research/sdk-assessment.md).

## Inspeção real do host em 14/10/2026

Suíte atual: **35 testes aprovados**; compilação Python aprovada; wheel reconstruído,
instalado e testado com SDK → HTTP autenticado → consulta real do Windows. Registro
da consulta em [evidência local](../research/host-inspection-evidence.json).

`host.inspect` exercitado neste Windows sem MIDI: retornou FL Studio 2025
25.2.5.5319 e FL Studio 2026 26.1.7.5653, com executáveis padrão/scaled. Nenhum
processo FL com os nomes consultados observado no momento da consulta. O comando
não inicia o aplicativo nem lê o projeto. Identificação limitada a locais usuais
de instalação e caminhos de processos acessíveis. Correspondência de caminho não
certifica assinatura do binário. A implementação tem timeout e validação do JSON.
O mapa e as fontes estão em [interfaces diretas](../research/direct-interface-map.md).

## Atualização em 14/10/2026: API independente

Servidor e SDK separados do protocolo MIDI. O serviço padrão anuncia estado
desconectado e retorna `backend_unavailable` para comandos de controle. O demo
usa diretamente a API; MIDI Scripting exige opção explícita `--midi`.
A suíte atual passou em 30 testes, incluindo ausência de imports MIDI no caminho da API,
erro de integração indisponível, seleção explícita de MIDI e HTTP com demo direto.
Integração direta com FL Studio ainda não implementada. Os registros abaixo
preservam a validação anterior, inclusive a opção MIDI agora secundária.

Data local: 13/10/2026, America/Sao_Paulo. Snapshot de desenvolvimento v0.1.0.

| Verificação | Resultado |
| --- | --- |
| Windows x64, Python 3.14 | suíte unittest local: 27 testes aprovados |
| Wheel e instalação isolada | pacote FL Commons construído e instalado |
| Compilação Python e dependências | compileall aprovado; pip check sem dependências quebradas |
| Extra MIDI | Mido 1.3.3 e python-rtmidi 1.5.8 instalados; backend nativo compilado para Python 3.14 |
| Processo instalado fora da pasta de fontes | HTTP/SDK demo, leitura/start/stop e geração do bundle aprovados |
| Codec com Mido real | ida e volta SysEx preservou bytes e conteúdo autenticado |
| Portas MIDI pelo backend real | nenhuma entrada; saída Microsoft GS Wavetable Synth 0 |
| Entrada de script FL | callbacks do projeto com módulos de host simulados; resposta adiada até OnIdle |
| REA | versão 6.4.0 conectada após configuração pelo usuário |
| Ghidra | 12.1.4: análise e descompilação real de DLL própria PE x64, duas funções; [evidências](../research/ghidra-validation.md) |

A suíte cobre assinatura, adulteração, limites de tamanho, valores não finitos,
JSON duplicado, timestamp inválido, sequências/replays, respostas duplicadas,
capacidades ausentes, reinício da sessão, timeout, retentativa de leitura,
ambiguidade de escrita, exclusão com prazo, autenticação HTTP, Host/Origin,
contrato JSON, SDK, bundle e callback do adaptador. As falhas foram reproduzidas
antes de implementar/corrigir seus respectivos comportamentos.

## Compatibilidade real

| Alvo | Observado | Teste de integração |
| --- | --- | --- |
| FL Studio 2025 | pasta de instalação presente | não executado |
| FL Studio 2026 | metadado ProductVersion 26.1.7.5653 | não executado |
| Outros builds/edições/OS | sem evidência | não testado |

Nenhum FL foi iniciado, script instalado, projeto aberto ou executável modificado.
Não houve rota MIDI bidirecional configurada para testes. Python embutido, módulos
padrão usados, OnIdle, saída SysEx e efeitos das funções precisam de teste real.
O relato de travamento de SysEx em builds 26 não foi reproduzido nem considerado
resolvido. CI está configurado, mas não foi publicado/executado.

O ID experimental MIDI 0x7D é para pesquisa privada. Atribuição/enquadramento
válido é requisito antes do lançamento público do transporte, mesmo gratuito.
A disponibilidade de capacidades indica apenas funções presentes e permitidas
pelo catálogo do adaptador. Não certifica comportamento num build.

## Registro para adicionar um build testado

Registre build exato/edição, SO, versão do MIDI Scripting/Python embutido, roteador
e backend MIDI, configuração de portas, versão/commit FL Commons e procedimentos.
Em sessão descartável: autenticação correta/incorreta, handshake, estado parado,
start/state/stop/state, perda de resposta, reinício do script e reconexão de portas.
Anote resultados, limitações e evidências sem segredos nem conteúdo de projeto.
O registro começa vazio: nenhum build real é declarado suportado nesta entrega.

## API nativa inicial — 2026-10-14

DLL x64 FL Commons API compilada com MSVC e SDK externo. 42 testes Python
existentes, 11 testes HTTP nativos e assertions C++ do contrato passaram.
O SDK Python comunicou por sockets reais com host controlado. Casos incluem
token, Host/Origin, headers duplicados, JSON/limites, estado desconhecido,
thread, porta exclusiva, cancelamento antes de execução, outcome_unknown
após início e encerramento com request incompleto. O factory recusa Python.
ProductVersion fixo do FL instalado conferido: 26.1.7.5653.

**Não instalado/carregado no FL; nenhum comando musical real executado.**
Não foi testado áudio, todos os callbacks virtuais, múltiplas instâncias no
FL, remoção durante reprodução ou compatibilidade SDK 2021/FL 2026.
DLL usa material do SDK externo; não atribuir licença MIT ao binário inteiro.
Evidência e hash: [native-api-validation.json](../research/native-api-validation.json).

## Perfil de compatibilidade e carregamento — 2026-10-14

44 testes Python, 15 testes HTTP nativos, 4 testes do instalador e o contrato
C++ passaram. A DLL atual foi instalada como FL Commons API_x64.dll, com
backup da versão anterior. O usuário carregou o efeito; a consulta de módulos
do processo FL64 confirmou a DLL e GET /v1/health sem token retornou 401.

Isso comprova carregamento/inicialização e a barreira de autenticação neste
build, não comprova estado ou efeito de comandos. A primeira tentativa de
leitura autenticada expirou antes do carregamento; seu token estava somente
na memória do verificador encerrado. O launcher agora guarda token com DPAPI
e o SDK oferece Client.from_native_session(), testados com DPAPI real.
Leitura autenticada e controle musical ainda aguardam reinício normal do FL
com esse launcher. Não fechar/descartar trabalho do usuário automaticamente.
Nenhuma escrita musical foi executada nem projeto salvo. Atualização
automática, rollback remoto e os demais domínios permanecem não implementados.

## Leitura autenticada no FL real — 2026-10-14

Depois do reinício normal e carregamento pelo usuário, o SDK instalado
recuperou o token DPAPI e consultou o plugin no FL 26.1.7.5653. Health=ok;
GUI idle observado e responsivo; callback de reprodução observado;
transport.state retornou playing=false. Token incorreto rejeitado com 401.
host_version_raw=-1 foi preservado sem interpretação; o build deriva
dos metadados do executável verificados pelo factory. Nenhum comando
Play/Pause/Stop foi enviado. Nenhum projeto foi salvo ou modificado pelo
verificador. Transições de estado, controle musical e demais domínios
continuam pendentes; fl_runtime_validated=false é intencional.
Evidência: [fl-native-session-probe.json](../research/fl-native-session-probe.json).

## Controle real e API pública — 2026-10-14

Este registro substitui as pendências de transporte dos registros históricos acima. A assinatura da fábrica foi corrigida para a ordem oficial `(Host, Tag)`, com assertion de compilação. Após reinício e carregamento pelo usuário, Play → Pause → Play → Stop foi confirmado pelos callbacks do FL 26.1.7.5653. HostVersion bruto observado: 26001007; o valor -1 anterior ocorreu com a assinatura incorreta.

52 testes Python e 21 nativos passaram (16 HTTP, 4 instalador, 1 provedor DPAPI). O pacote Python foi construído e instalado; FLStudio.connect(), status e estado foram consultados no FL real. O Core opcional com NativeBackend confirmou status, capacidades, catálogo e estado por HTTP. Nenhuma escrita foi executada nesse último smoke.

A DLL atualmente compilada inclui uma correção adicional que libera o bloqueio da fila antes de enviar respostas. Seu teste com cliente lento passou, mas essa alteração adicional ainda não foi recarregada no FL. Os hashes compilado e efetivamente testado estão separados no registro JSON. Mixer, canais, edição de projetos, áudio e outros builds não foram validados.

Evidências: [transporte](../research/fl-native-transport-probe.json), [API pública](../research/public-api-smoke.json), [registro](../research/native-api-validation.json).
