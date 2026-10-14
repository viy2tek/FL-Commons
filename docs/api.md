# API HTTP v1 e SDK

`sdk.catalog` consulta as 87 declarações do dispatcher do SDK recebido. Aceita
`offset` (inteiro >= 0), `limit` (1..32) e `domain` opcional. No SDK Python:
`client.sdk_catalog(domain=None, offset=0, limit=32)`. A resposta inclui entries,
total, next_offset, hashes de origem e `fl_runtime_tested: false`. Os domínios
são inferidos; `callable_via_api: false` impede confundir declaração com execução.
Não é um endpoint para invocar funções internas arbitrárias.

O serviço funciona independentemente de MIDI. Sem opção de integração,
`capabilities` retorna `mode: disconnected`, `fl_version: null` e, no Windows,
`host.inspect` como operação real de inspeção do sistema;
comandos conhecidos retornam HTTP 503 `backend_unavailable`.
`--demo` oferece simulação direta na API. `--midi` ativa uma integração opcional
para casos específicos. Os campos protocol/boot/adapter_version/midi_api_version
abaixo pertencem somente a essa integração opcional, não ao contrato obrigatório.

Base: `http://127.0.0.1:3210`. Todas as chamadas exigem
`Authorization: Bearer <token>`, inclusive health. Apenas Host exato
`127.0.0.1:<porta>` é aceito. Requisições com Origin são rejeitadas; não há CORS.

| Endpoint | Resposta/uso |
| --- | --- |
| GET `/v1/health` | `{service, version, scope: service-only}`; não testa o FL |
| GET `/v1/capabilities` | padrão/demo: `{api_version, fl_version, mode, compatibility, capabilities}`; campos adicionais apenas na opção MIDI |
| POST `/v1/commands` | JSON `{method, params: {}}`, responde `{result: ...}` |

| Capacidade | Resultado | Tipo |
| --- | --- | --- |
| `transport.state` | `{playing: bool, recording: bool, position: number}` | leitura |
| `transport.start` | `null` após o callback retornar | escrita |
| `transport.stop` | `null` após o callback retornar | escrita |
| `host.inspect` | `{platform, installations, processes, coverage, control_connected: false}` | leitura real do Windows, fora do demo |

`host.inspect` aceita params vazio e procura instalações usuais da Image-Line
em Program Files e Program Files (x86), lendo ProductVersion. Lista processos
FL/FL64/FL64 (scaled), seus PIDs e caminhos acessíveis. `identity_verified` é
apenas correspondência de caminho com uma instalação encontrada, não assinatura
digital. Outras pastas e processos sem caminho acessível ficam fora da verificação.

A resposta contém somente executáveis da versão numérica mais recente encontrada
e processos com caminho verificado pertencente a essa versão. `selected_version`
identifica o alvo; é null se nenhuma instalação foi encontrada. Metadado de versão
desconhecido provoca erro de inspeção, evitando escolha silenciosa de versão antiga.
Processos sem caminho identificável não são atribuídos ao alvo mais recente.
Isso não consulta o projeto, transporte musical, mixer ou plugins. A consulta
tem prazo de 5 segundos; falha não é apresentada como ausência do FL. Linux/macOS
retornam `unsupported_platform`; não se simula host.inspect no modo demo.

`position` usa o formato normalizado retornado por `transport.getSongPos()` sem
argumentos. Não são unidades de tempo ou beats. `compatibility: unverified`
significa que a resposta não certifica testes reais nesse build. O catálogo é
uma lista fechada, reduzida pelas funções disponíveis; não enumera APIs internas.

As operações transport.* dessa tabela são simuladas em `--demo` e só chegam ao
FL na integração MIDI opcional. Nenhuma delas tem implementação de controle
musical nativo direto nesta etapa. `host.inspect` é a operação real implementada
no serviço padrão Windows; não mede o estado musical do aplicativo.

O corpo tem limite de 8192 bytes, precisa de Content-Length único e Content-Type
application/json. Parâmetros são validados por operação; campos extras, chaves duplicadas, JSON inválido e
valores não finitos são rejeitados. Transfer-Encoding não é aceito.

Erro: `{error: {code, message}}`.

| HTTP | Códigos comuns | Significado |
| --- | --- | --- |
| 400/411/413/415 | `invalid_request`, `length_required`, `too_large`, `invalid_content_type` | requisição recusada |
| 401/403 | `unauthorized`, `forbidden` | acesso recusado |
| 404/422 | `not_found`, `unsupported` | rota ou capacidade indisponível |
| 409 | `session_changed`, `handshake_required` | refazer handshake; escrita não reenviada |
| 503 | `busy`, `unavailable`, `backend_unavailable`, `host_inspection_failed` | ocupado, sem resposta, controle não implementado ou consulta do sistema falhou |
| 504 | `outcome_unknown` | escrita pode ter executado; conferir estado |
| 502 | `host_error`, `protocol_error`, `replay`, `expired`, `client_limit` | falha na fronteira MIDI/host |

SDK: `Client(token, port=3210, timeout=20)`, `health()`, `capabilities()` e
`command(method, params=None)`, além de `inspect_host()`. `APIError` fornece `status`, `code` e mensagem.
Falha de conexão HTTP durante POST também informa resultado desconhecido. Não há
retentativa automática HTTP, nem garantia de execução única se o chamador enviar
a mesma escrita como uma nova requisição.

Somente na integração MIDI, um handshake é realizado na primeira operação, numa consulta explícita de
capacidades ou após invalidação da sessão. Não há heartbeat nem monitoramento
contínuo. O servidor limita oito conexões de trabalho e o RPC usa exclusão com
prazo; se todas as conexões estiverem ocupadas, uma nova conexão é fechada.
