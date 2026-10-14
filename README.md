# FL Commons

Investigação atual: [mapa de interfaces para uma API ampla](research/universal-api-scope.md).
O SDK pode consultar o catálogo de evidências com `client.sdk_catalog()`;
declarações ainda não são operações de controle habilitadas.

**Uma API comunitária independente para integração com FL Studio.**

Missão: fornecer os recursos de projeto, estado, eventos e operações verificáveis
que permitam à comunidade construir FL Studio Time Machine, Universal Project
Search, FL Studio Self-Healing, Universal DAW Translator e outras integrações.
Esses casos orientam a evolução da API; ainda não estão implementados.
Veja [missão e lacunas](docs/master-spec-alignment.md).

Escopo atual: somente a versão mais recente instalada do FL Studio. A seleção
compara numericamente o build dos executáveis encontrados e ignora versões
anteriores. Neste ambiente o alvo é **26.1.7.5653**. Detecção não comprova controle
musical. Veja [avaliação do SDK recebido](research/sdk-assessment.md).

FL Commons não é afiliado, endossado ou mantido pela Image-Line. FL Studio é uma
marca da Image-Line. Este projeto não distribui código, executáveis ou recursos
proprietários do FL Studio. Código original sob licença MIT.

## Estado da v0.1: snapshot de desenvolvimento

Diretriz atual: toda funcionalidade é exposta pela API. Servidor HTTP autenticado,
SDK Python e catálogo são independentes de MIDI. O modo demo simula consulta de
reprodução/gravação/posição, iniciar e parar reprodução diretamente, sem SysEx.
MIDI Scripting é uma integração opcional para situações específicas, ativada
somente por `--midi`; não é requisito do servidor nem a arquitetura principal.

**Plugin nativo inicial compilado:** hospeda HTTP no FL em 127.0.0.1:3211,
com estado por callback, Play/Pause e Stop pelo SDK oficial. Não requer MIDI
nem servidor Python. Compilação e host controlado validados; carregamento no FL
e rejeição de token incorreto confirmados. Leitura autenticada de compatibilidade
e estado inicial comprovada no FL; Play/Pause e Stop confirmados em sessão de teste.
Veja [instalação e uso](native/README.md).

Play → Pause → Play → Stop foi confirmado por callbacks no FL
26.1.7.5653, em sessão de teste autorizada. O SDK público permite:

```python
from flcommons import FLStudio
fl = FLStudio.connect()
print(fl.status())
print(fl.transport.state())
# Somente quando quiser alternar a reprodução:
fl.transport.play_pause()
fl.transport.stop()
```

O caminho direto não exige servidor Python. Para reunir controle nativo e catálogo
em uma API HTTP opcional, use `fl-commons serve --native`. Sem componente nativo
acessível, `/v1/status` informa desconexão e comandos falham explicitamente.
Veja [contrato público e OpenAPI](docs/public-api.md).

O servidor Python `serve` inicia a API
com `mode: disconnected`; no Windows, `host.inspect` consulta instalações,
versões e processos reais pelas interfaces do sistema. Comandos de controle retornam
`backend_unavailable`. `serve --demo` permite testar o contrato com simulação
explícita. Isso não representa controle real do FL. Veja
[desenho atual](docs/design.md) e [validação](docs/validation.md).

O plugin possui introspecção de sessão em `client.compatibility()`: perfil
conhecido, build, ID por carregamento, atividade da GUI e callback observado.
As operações permanecem experimentais; observação não é certificação de
compatibilidade. Veja [incremento de compatibilidade](docs/compatibility-increment.md).

Somente a opção MIDI experimental usa SysEx 0x7D para pesquisa privada; um
lançamento público dessa opção exige enquadramento MIDI permitido.

## Executar agora, sem conectar ao FL Studio

Python 3.10 ou superior para o servidor/SDK. O núcleo usa apenas a biblioteca
padrão. Dentro desta pasta, em PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install .
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --demo
```

Guarde o token de forma privada e forneça o mesmo valor ao cliente. Encerre com Ctrl+C.
O serviço aceita apenas `127.0.0.1`, por padrão na porta 3210. O modo demo anuncia
`mode: simulated` e `fl_version: null` explicitamente.

Para iniciar o serviço sem simulação, use `python -m fl_commons serve`. A API
estará disponível com inspeção real do host no Windows, sem anunciar controle
musical até que esse acesso seja implementado e validado.

SDK Python, em outro terminal/processo com o mesmo token:

```python
import os
from fl_commons.sdk import Client, APIError

client = Client(os.environ['FL_COMMONS_TOKEN'])
print(client.health())
print(client.capabilities())
print(client.command('transport.state'))
# Estas duas operações alteram reprodução quando conectadas ao FL real:
client.command('transport.start')
client.command('transport.stop')
```

Não repita automaticamente uma escrita após `outcome_unknown`. Confira o estado
do FL antes de decidir. O SDK não faz retentativas HTTP.

No serviço padrão (sem `--demo`), `client.inspect_host()` retorna instalações,
versões e processos observados no Windows. A presença do FL não habilita os
comandos musicais. Veja [interfaces pesquisadas](research/direct-interface-map.md).

## Estrutura

```text
fl_commons/          API, servidor HTTP, SDK e CLI; MIDI opcional separado
  hardware/          callbacks da integração MIDI opcional
flcommons_common/   validação compartilhada, sem dependência de MIDI
flcommons_wire/     protocolo da integração MIDI opcional
tests/              testes de contrato, falhas e integração HTTP real local
docs/               instalação, API, transporte, segurança e validação
research/           trilha isolada de pesquisa com REA/Ghidra
examples/           cliente mínimo
```

Teste: `python -m unittest discover -s tests -v`. CI configura uma matriz de
Python/Windows/Linux; essa configuração não significa que as execuções remotas
já ocorreram. [Contribuir](CONTRIBUTING.md), [segurança](SECURITY.md),
[API](docs/api.md), [protocolo](docs/protocol.md),
[licenças de terceiros](THIRD_PARTY_NOTICES.md).

Se uma ocasião específica exigir MIDI Scripting, consulte
[configuração opcional](docs/setup-fl-studio.md). Essa opção não é necessária
para iniciar a API ou usar seu SDK.

Não há descoberta irrestrita, auto-update, patch do executável, acesso a APIs
privadas, carregamento de plugins arbitrários, exportação de áudio nem edição
de notas nesta versão. Ampliar a API exige contrato documentado e testes reais.
