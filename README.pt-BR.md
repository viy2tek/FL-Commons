# FL Commons

O FL Commons é uma API comunitária independente para integrações com o FL Studio. Expõe capacidades documentadas e verificadas por um contrato público estável. Os programadores definem suas próprias integrações.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · **Português (Brasil)** · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Capacidades atuais

v0.1.0 experimental: HTTP local autenticado, SDK Python, estado de reprodução, Play/Pause e Stop por um plugin do SDK oficial. O Core opcional oferece um catálogo de evidências de 87 seletores do SDK; entradas do catálogo não habilitam comandos automaticamente. MIDI é opcional; a API direta dispensa servidor Python separado.

```text
transport.state
transport.play_pause
transport.stop
```

## Início rápido

**Alvo de compatibilidade: FL Studio 25/26 em diante, em Windows x64.** O repositório atualmente distribui código-fonte. Compilar exige Python 3.10+, MSVC 2022 Build Tools, Windows SDK e o **fpsdk_20210311b** fornecido externamente. São requisitos de compilação para desenvolvedores. Extraia o SDK fora do repositório e substitua os caminhos de exemplo.

Instale o pacote Python deste repositório e compile o componente nativo:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Salve seu trabalho e feche o FL normalmente antes da instalação. O instalador preserva versões existentes em vez de sobrescrevê-las. Depois de iniciar, adicione **FL Commons API** a um slot livre do Mixer. O launcher guarda o token com Windows DPAPI. Uma instância nativa usa a porta 3211.

```powershell
.\.venv\Scripts\python native/setup.py --dll 'C:/path/to/flcommons-build/FL Commons API.dll' --launch
```

## SDK Python

```python
from flcommons import FLStudio

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())
```

Comece pelas consultas de leitura. Execute os comandos abaixo apenas quando quiser mudar a reprodução. Play/Pause é uma alternância, não um início idempotente. Após timeout de escrita ou `outcome_unknown`, confira o estado antes de decidir; não repita automaticamente.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Servidor Core opcional

O SDK direto conecta ao plugin em `127.0.0.1:3211`. Para também acessar o catálogo e o contrato OpenAPI do Core, inicie o servidor opcional na porta 3210. Seu token de cliente é separado do token DPAPI nativo. `--demo` é simulação explícita; o servidor padrão inicia desconectado.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Validação e limites

**Verificado:** 79 testes Python e 28 nativos passaram localmente. O CI Python passou em Windows e Linux com Python 3.10, 3.12 e 3.14. Play → Pause → Play → Stop foi confirmado pelos callbacks do FL numa sessão de teste autorizada no build 26.1.7.5653. O CI Linux não valida o plugin do FL.

Edição de Mixer/canais/projetos e eventos públicos não estão implementados. A seleção adaptativa usa perfis de interfaces implementadas; atualizações verificadas oferecem staging e rollback. Outros contratos precisam de perfis verificados; não há descoberta irrestrita nem compatibilidade comprovada com todos os builds. Consulte o guia de compatibilidade para evidências e requisitos de compilação/recarga.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/adaptive-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Documentação

Os links abaixo aprofundam a documentação, atualmente em sua maioria em português. Inglês é o README principal; correções nas traduções são bem-vindas.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Contribuições e licença

Contribua com interfaces documentadas, evidências reproduzíveis e testes. Separe código original, material do SDK e pesquisa. Um símbolo detectado ou resultado simulado não comprova controle do FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

O código original do FL Commons usa licença **MIT**. Arquivos do SDK Image-Line e DLLs compiladas não são distribuídos aqui; os termos do SDK se aplicam separadamente. FL Commons não é afiliado, endossado ou mantido pela Image-Line. FL Studio é uma marca da Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
