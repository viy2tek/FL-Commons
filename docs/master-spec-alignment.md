# Alinhamento com a especificação mestra v1.1

Análise em 14/10/2026. Referência fornecida pelo usuário:
Especificação mestra FL Commons v1.1, 17 páginas, fornecida em PDF.
Documento de produto, não evidência de funcionalidades implementadas.
Nenhuma instrução inserida no PDF foi executada como comando.

## Missão e decisões preservadas

FL Commons é uma infraestrutura comunitária independente da Image-Line.
FL Commons API é o contrato público para programas externos enviarem comandos,
consultarem estado e receberem eventos observáveis. Comunicação interna pertence
ao Core; não é um segundo produto. Os consumidores são integrações externas.

### Definição do projeto

O FL Commons é uma API comunitária independente para integrações com o FL Studio.
Expõe capacidades documentadas e verificadas por um contrato público estável.
Os programadores definem suas próprias integrações. A API oferece operações,
dados e eventos gerais, sem orientar seu contrato a aplicativos específicos.

O modelo comum deve distinguir estado ao vivo, arquivo salvo e dado indisponível,
com unidades, identidade, relações, limites e efeitos explícitos. A abrangência
pretendida não significa que todos esses recursos já estejam implementados.

A API deve crescer além de transporte: projeto, objetos/identidade, canais,
mixer/roteamento, padrões/notas, automação, plugins/parâmetros, mídia/dependências,
eventos/snapshots e operações seguras, à medida que exista acesso comprovado.
Contratos desses domínios serão definidos a partir das interfaces e evidências,
sem criar endpoints fictícios ou expor chamadas internas arbitrárias.

Continuam preservados: FL Commons, FL Commons API, integração nativa direta,
MIDI opcional, alvo de compatibilidade FL Studio 25/26 em diante, interfaces permitidas,
independência de IA/REA/Ghidra no runtime e ausência de modificações no executável.

O documento descreve a visão completa de adaptadores variáveis sob contrato
estável, descoberta de interfaces comprovadas, compatibilidade, atualizações
verificadas e degradação controlada. Isso não implica recuperar todo o código do
FL ou inventar funções desconhecidas.

As instruções mais recentes ampliam o alvo para FL Studio 25/26 em diante,
com detecção e adaptação por capacidades. Isso substitui a decisão anterior
de atender somente ao build mais recente instalado. MIDI continua opcional
e o contrato nativo oficial é preservado. O teste real no build 26.1.7.5653
permanece evidência daquele ambiente, não requisito definitivo do produto.
O runtime atual ainda contém a restrição exata; a implementação adaptativa
está descrita no [desenho para revisão](adaptive-compatibility-design.md).

O código original já tem licença MIT. O PDF deixa a licença final em aberto
(páginas 14 e 16). Não houve mudança de licença nem autorização de redistribuição
do SDK proprietário; seus termos permanecem separados.

## Comparação com o código e as evidências

| Requisito | Estado comprovado | Lacuna |
| --- | --- | --- |
| Core e canal bidirecional (p. 5–7, 12) | Plugin x64 com HTTP loopback autenticado, fila, limites, timeout, erros e SDK Python; leitura real no FL | Fluxo nativo não tem request_id público/deduplicação; escritas não são repetidas automaticamente; reconexão gerenciada ausente |
| Identidade e independência (p. 2–4, 11) | FL Commons, aviso de não afiliação, runtime sem IA/REA/Ghidra | Preparação para publicação comunitária ainda incompleta |
| status e capabilities (p. 7–8, 13) | SDK status e /v1/status no Core; backend nativo fornece detalhes, origem, restrições e indisponibilidade por operação | Native REST inicial usa compatibility como fallback de status; endpoints diretos ainda são subconjunto |
| Contrato único (p. 4–8) | FLStudio.connect() acessa componente diretamente; Core --native reúne catálogo e controle; OpenAPI inicial | Cliente precisa escolher caminho direto ou Core; transport.start é somente demo, não equivale a alternância |
| Primeiras operações (p. 7, 13–14) | Play-Pause-Play-Stop confirmado pelos callbacks no FL 26.1.7.5653 após corrigir factory oficial | Channels/Mixer e demais domínios ausentes |
| Compatibilidade adaptativa (p. 8–10, 13) | Restrição ao build-alvo, perfil conhecido e introspecção da sessão | Seleção entre adaptadores, matriz validada, atualização assinada, distribuição confiável, rollback e política de updates ausentes |
| Eventos (p. 10, 13) | Callback de reprodução atualiza cache de estado | Sem eventos normalizados públicos, sequências, ressincronização ou WebSocket |
| SDK e contrato (p. 3–4, 6, 13) | FLStudio.connect(), status e namespace transport; OpenAPI do Core | SDK TypeScript e namespaces dos demais domínios ausentes |
| Confiabilidade (p. 12–15) | 52 testes Python, 21 nativos (16 HTTP, 4 instalador, 1 DPAPI) e contrato C++; token DPAPI recuperável | Fechamento/recarregamento do FL durante comando e impacto em áudio ainda precisam de teste real |
| FLP offline (p. 11) | Não implementado | Complementar e posterior; não deve desviar o primeiro marco |

Arquivos conferidos: native/local_api.h, native/plugin.cpp, native/setup.py,
fl_commons/api.py, fl_commons/sdk.py, fl_commons/session.py e
research/native-api-validation.json. Evidência real:
[fl-native-session-probe.json](../research/fl-native-session-probe.json).
Os números de testes correspondem à [validação atual](validation.md), com
hashes distintos para a DLL compilada e a efetivamente testada no FL.

## Limites da prova atual

No FL Studio 26.1.7.5653 foram observados carregamento, leitura autenticada,
GUI idle/callback, rejeição de token incorreto e transições Play-Pause-Play-Stop.
A ordem incorreta dos parâmetros do factory foi detectada pelo primeiro teste
de escrita e corrigida para (Host, Tag), como nos exemplos do SDK. O HostVersion
correto retornou 26001007; o -1 anterior não era metadado válido. Build provém
dos metadados do executável conferidos pelo factory.

Isso não certifica todas as operações do SDK, todos os contextos de playback,
Mixer/Channels, outros builds, reconexão completa, áudio ou atualizações.
fl_runtime_validated=false continua intencional no componente experimental.

## Próximos incrementos em ordem

1. Unificar a semântica do contrato público e documentá-lo em OpenAPI; expor
   status de conexão e capabilities com origem, restrições e nível de evidência,
   preservando clientes existentes. Separar disponível de experimental/testado.
2. Completar request_id, confirmação correlacionada, proteção contra duplicação,
   erros semânticos e reconexão sem repetir escritas incertas.
3. Validar Play/Pause/Stop e desconexão/recarregamento em projeto descartável;
   verificar efeito pelo callback, não apenas pelo recebimento HTTP.
4. Adicionar Channels/Mixer somente pela interface que permita o acesso necessário
   e após teste. O contexto de um plugin do SDK não prova enumeração global.
   MIDI continua uma opção específica, não dependência obrigatória.
5. Ampliar perfis/adaptadores, eventos confiáveis e SDKs. Updater requer cadeia
   de confiança, assinatura e rollback definidos antes de instalação automática.

Não reiniciar o repositório nem criar pastas vazias para imitar o diagrama.
O trabalho existente é aproveitável. A visão é ampla; a v0.1 ainda não cumpre
todo o checklist de mínimo produto comprovável das páginas 13–14.
