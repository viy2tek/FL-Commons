# FL Commons API v0.1 — contrato inicial para programadores

O caminho principal usa o componente nativo oficial no FL, HTTP em 127.0.0.1:3211
e SDK Python. MIDI, IA, REA e Ghidra não são requisitos de execução.

```python
from flcommons import FLStudio, APIError

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())

# Em uma sessão de teste, com gravação desarmada:
reply = fl.transport.play_pause()
print(reply)
print(fl.transport.state())
fl.transport.stop()
```

Play/Pause é uma alternância. Não existe play() idempotente neste contrato.
O retorno preserva host_result e disposition; confirme o efeito por state().
Timeout de escrita não permite repetição automática. Client continua disponível
em fl_commons.sdk; flcommons.FLStudio é o mesmo cliente sob o nome público.

FLStudio.connect() recupera o token protegido do usuário Windows, verifica a
conexão e restringe ao build-alvo. status() mantém compatibilidade com o plugin
inicial, consultando /v1/compatibility quando /v1/status não está presente.
Se o FL reiniciar e o token mudar, execute connect() novamente. Não se repetem
automaticamente comandos anteriores.

## Servidor Core opcional com backend nativo

Para clientes HTTP que também precisem do catálogo do SDK:

```powershell
$env:FL_COMMONS_TOKEN = 'TOKEN_PRIVADO_DO_SERVIDOR_COM_PELO_MENOS_32_CARACTERES'
fl-commons serve --native
```

A porta 3210 usa esse token de cliente. O backend lê separadamente o token
DPAPI do componente nativo na 3211. Sem plugin acessível, status.connected=false,
capabilities omite controle e comandos retornam not_connected. Não há fallback
silencioso para simulação. --demo e --midi continuam modos explícitos.
O servidor Core é opcional: FLStudio.connect() acessa o plugin diretamente.

| Caminho Core | Função |
| --- | --- |
| GET /v1/health | Saúde do serviço HTTP, sem presumir conexão com FL |
| GET /v1/status | Conexão, modo, build e sessão conforme o backend |
| GET /v1/capabilities | Operações implementadas, com modo e compatibilidade explícitos |
| POST /v1/commands | method e params; resposta result ou error |

Comandos nativos iniciais: transport.state, transport.play_pause e transport.stop.
sdk.catalog é executado localmente pelo Core, com filtro/paginação do inventário.
Não habilita as outras declarações do SDK. O adaptador nativo não aceita
transport.start, comandos arbitrários ou parâmetros não documentados.

Erros relevantes: not_connected (503), version_unverified (409), unsupported
(422), invalid_params (400), busy (503), outcome_unknown (504), unauthorized (401).
O plugin inicial também retorna not_executed (504) quando cancela antes de executar.

Veja [OpenAPI do servidor Core](openapi.json). A interface REST nativa v0.1 é um
subconjunto separado: health/capabilities/compatibility/commands; status é
normalizado pelo SDK. A especificação não anuncia Channels/Mixer/projetos ainda
não implementados. A evolução desses domínios mantém a missão documentada em
[alinhamento](master-spec-alignment.md).
