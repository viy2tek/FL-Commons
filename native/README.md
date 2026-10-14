# API nativa hospedada no FL Studio

O plugin **FL Commons API.dll** hospeda HTTP diretamente no FL em
127.0.0.1:3211. Não requer MIDI nem servidor Python. FL Commons é independente
e não afiliado à Image-Line. DLL x64 compilada; testes de HTTP em host
controlado passaram. **Carregamento no FL 26.1.7.5653, leitura autenticada de
compatibilidade/estado inicial e rejeição de token incorreto confirmados.
Play/Pause e Stop confirmados por mudanças no callback em sessão de teste.**

O factory aceita somente FL64.exe ou FL64 (scaled).exe com ProductVersion
26.1.7.5653. Isso restringe o alvo; não certifica compatibilidade com o SDK de 2021.

A sessão real retornou playing=false via callback, GUI responsiva e
host_version_raw=26001007 após correção da assinatura (Host, Tag) do factory.
O retorno -1 anterior era evidência de uma chamada incorreta, não metadado válido.
O build é obtido por
metadados do executável e conferido pelo factory. fl_runtime_validated permanece
false: testes locais de transporte não certificam todo o SDK ou outros contextos.
Veja [evidência real](../research/fl-native-session-probe.json).
Transporte: [sequência confirmada](../research/fl-native-transport-probe.json).

## Compilar e carregar

Requer MSVC 2022 Build Tools x64 e Windows SDK. Extraia o SDK fornecido em
uma pasta externa ao repositório, preservando source/c:

```powershell
./native/build.ps1 -SdkDirectory 'D:/caminho/sdk-extraido' -OutputDirectory 'D:/caminho/build-flcommons'
```

O build compila externamente fp_plugclass.cpp e headers oficiais. Não os
copia ao projeto nem os licencia como MIT. A DLL contém material desse SDK:
seus termos continuam aplicáveis, inclusive antes de redistribuição pública.

Em uma sessão de teste, copie a DLL para uma pasta **FL Commons API** em
Plugins/Fruity/Effects da instalação FL Studio 2026, com nome instalado
**FL Commons API_x64.dll**. Não sobrescreva arquivos
existentes sem guardar uma cópia. Antes de iniciar o FL:

```powershell
$env:FL_COMMONS_TOKEN = 'SEU_TOKEN_PRIVADO_COM_PELO_MENOS_32_CARACTERES'
& 'C:/Program Files/Image-Line/FL Studio 2026/FL64.exe'
```

Use um token aleatório privado de 32..256 caracteres: letras ASCII, números,
hífen ou underscore. Não use o exemplo como segredo. O token não é salvo
no projeto. Um FL já aberto não herda a variável: feche normalmente antes.
Adicione o efeito FL Commons API a um slot livre do Mixer. Há uma instância
ativa por porta. Token inválido, porta ocupada ou build diferente recusam
carregamento; não existe interface visual própria neste estágio.

Para iniciar sem copiar tokens manualmente, feche o FL normalmente, salvando
seu trabalho, e use o instalador original:

```powershell
python native/setup.py --dll 'D:/caminho/build-flcommons/FL Commons API.dll' --launch
```

Ele seleciona somente a instalação mais recente, verifica o build-alvo, recusa
uma sessão já aberta e instala com o sufixo x64. Repetir a mesma DLL é permitido;
outra versão existente é preservada e exige guardar/mover uma cópia antes.
Se FL_COMMONS_TOKEN estiver ausente, gera um token aleatório. Antes de iniciar
o FL, guarda o token criptografado por Windows DPAPI em
%LOCALAPPDATA%/FLCommons/native-session.bin. O arquivo não contém o token em
texto aberto e o launcher não o imprime; o SDK o recupera com:

```python
from fl_commons.sdk import Client
client = Client.from_native_session()
print(client.compatibility())
```

DPAPI é proteção vinculada ao usuário Windows, não proteção contra outros
processos executados pelo mesmo usuário. [Contrato Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata).
Esse arquivo é local, não faz parte do ZIP e não é salvo em projetos.
O plugin agora lê esse arquivo diretamente quando FL_COMMONS_TOKEN não estiver
presente. Depois de preparar uma sessão pelo launcher, pode abrir o FL normalmente.
Uma variável explícita continua tendo prioridade; se usar outra chave, o cliente
deve usar a mesma. O arquivo protegido precisa existir para esse usuário Windows.
Se não aparecer no seletor, consulte os plugins instalados no Plugin Manager
e faça a atualização da lista pela interface oficial do FL.

Com o SDK Python FL Commons instalado, no ambiente com o mesmo token:

```python
import os
from fl_commons.sdk import Client
client = Client(os.environ["FL_COMMONS_TOKEN"], port=3211)
print(client.capabilities())
print(client.compatibility())
print(client.command("transport.state"))
print(client.command("transport.play_pause"))
print(client.command("transport.stop"))
```

O acesso direto não exige fl-commons serve. O modo opcional serve --native
roteia controle ao plugin e reúne status/catálogo no Core. O plugin não anuncia
sdk.catalog/host.inspect diretamente. Declarações do catálogo não habilitam
operações automaticamente.

## Contrato

- GET /v1/health, /v1/capabilities e /v1/compatibility; POST /v1/commands,
  todos com Bearer.
- compatibility fornece session_id aleatório por carregamento, perfil conhecido,
  build real somente em fl-native e host_version_raw (sem decodificação suposta).
  Registra callback observado, GUI idle observado, idade e responsividade em 2s.
  Observação não certifica comportamento: fl_runtime_validated permanece false
  e operações continuam experimentais/unverified. A consulta não altera projetos.
  Atualização automática de adaptadores ainda não está implementada.
- POST recebe method e params vazio, em qualquer ordem. Nomes e chaves ASCII
  literais, sem escapes JSON. Headers até 8192 bytes, corpo até 1024 bytes;
  prazo total de leitura 2s.
- Host exato 127.0.0.1:3211. Origin, Transfer-Encoding e headers duplicados
  são rejeitados. Sem CORS ou acesso remoto.
- playing começa null e só muda com FPD_SetPlaying; não inventa gravação,
  posição ou tempo. Play/Pause alterna reprodução, não é Start idempotente.
- Resposta de transporte preserva host_result e disposition (handled,
  delayed, not_handled, unavailable, unknown ou wrong_thread). Não garante
  alteração efetiva do estado; consulte novamente.
- Uma conexão por vez; fila de uma operação. O worker nunca chama o host.
  Idle_Public executa somente na thread que criou a instância.
- Após 2s sem começar: HTTP 504/not_executed e cancelamento. Se já começou:
  504/outcome_unknown. Não repetir automaticamente.
- Remover o plugin encerra sockets e cancela operações pendentes. Novo
  carregamento começa outro estado. Não há reconexão ou retry automáticos.

## Testes

```powershell
$env:FL_COMMONS_TEST_HOST = 'D:/caminho/build-flcommons/api_host.exe'
python -m unittest discover -s native/tests -p 'test_*.py' -v
```

Execute na raiz do projeto, com pacote instalado ou PYTHONPATH apontando
para ela. O host controlado verifica autenticação, limites, comandos, thread,
prazo e encerramento; o factory rejeita o processo Python. Estes testes não
substituem carregar a DLL no FL nem certificam todos os métodos virtuais.
