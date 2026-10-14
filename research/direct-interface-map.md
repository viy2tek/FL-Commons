# Interfaces para o FL Commons API

Atualização: SDK fornecido pelo usuário e examinado. O bloqueio de download da
etapa anterior foi resolvido pelo arquivo recebido. Veja [avaliação](sdk-assessment.md)
e [módulo nativo](../native/README.md). O alvo agora é apenas a versão mais recente
instalada; os registros multiversão abaixo são históricos, não escopo de suporte.

Pesquisa em 14/10/2026. Esta tabela é uma delimitação de evidências, não uma
promessa de controle completo nem prova de inexistência de outras interfaces.
Nenhum endpoint de controle foi habilitado a partir de suposição ou pseudocódigo.

| Interface | Alcance observado/documentado | Estado no FL Commons |
| --- | --- | --- |
| Windows Get-Process e FileVersionInfo | nomes/PIDs/caminhos acessíveis e versão do arquivo | `host.inspect` implementado e exercitado neste Windows |
| Comandos de renderização FL | exportação por linha de comando documentada pela Image-Line | candidato para tarefa de exportação; execução não testada |
| FL Plugin SDK oficial | criação de plugins nativos em Delphi/Visual C++; pacote publicado para FL 20.8 | candidato a acesso nativo; pacote/termos/callbacks não examinados nesta etapa |
| Piano roll scripting | manipulação de notas no contexto de scripts do Piano Roll | interface contextual; integração com API externa não demonstrada |
| VFX Script | eventos/vozes/controllers e contexto de playback dentro de Patcher | alcance contextual; controle geral externo não demonstrado |
| FL Studio Remote scripting | scripts de pads e módulos relacionados ao MIDI | secundário, fora do caminho principal solicitado |
| Funções internas obtidas por descompilação | sem contrato público demonstrado | não utilizadas pelo núcleo estável |

## Fontes primárias consultadas

- [Get-Process, Microsoft](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-5.1).
- [FileVersionInfo.ProductVersion, Microsoft](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.fileversioninfo.productversion).
- [SDK oficial FL Plugin, publicação Image-Line](https://forum.image-line.com/viewtopic.php?t=12092).
- [Anúncio Image-Line sobre renderização por linha de comando](https://www.image-line.com/fl-studio-news/fl-studio-12-4-released).
- [Piano roll scripting, Image-Line](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/pianoroll_scripting_api.htm).
- [VFX Script, Image-Line](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/VFX%20Script.htm).
- [Remote scripting, Image-Line](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/fl_studio_remote_scripting_api.htm).

O fórum do SDK mostra informações públicas e um pacote anexado; seu conteúdo e
licença não foram obtidos. A publicação afirma criação de plugins, não uma API
externa universal para controlar o FL. O uso num build 2026 e o acesso aos domínios
de mixer/canais/padrões dependem de exame dos contratos e testes reais.

## Evidência local obtida por `host.inspect`

Executáveis padrão/scaled encontrados para FL Studio 2025 (25.2.5.5319) e
FL Studio 2026 (26.1.7.5653). Nenhum processo com nome FL, FL64 ou FL64 (scaled)
observado no momento da consulta. Não foi iniciado nem alterado o FL Studio.
Busca restrita a instalações usuais da Image-Line; outras pastas não são cobertas.
Um processo pode desaparecer durante a consulta; identidade sem caminho acessível
fica desconhecida. Correspondência por caminho não equivale a assinatura digital.

## Próxima evidência necessária para controle musical nativo

A tentativa de download do SDK no endereço oficial respondeu HTTP 403 neste
ambiente. O pacote e seus termos não foram obtidos; não foram usados espelhos
nem contornos de acesso. É necessário obter o pacote oficial para esta próxima etapa.

Examinar o pacote e os termos do SDK oficial e listar callbacks por domínio.
Depois selecionar a primeira operação com contrato comprovado e criar um teste
num projeto descartável. Uma integração que exija componente nativo dentro do FL
deve implementá-lo como parte da própria API, sem ressuscitar um serviço Bridge
separado ou dependência obrigatória de MIDI.
