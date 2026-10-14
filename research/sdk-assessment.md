# SDK recebido: avaliação inicial

Arquivo fornecido: `D:/downloads/fpsdk_20210311b.zip`.
SHA-256: `a29c5bfbfd576ab9798574920ce911a7b4fe68c2aa7d11bec2546cdf4a6b35b1`.
ZIP íntegro, 269146 bytes. Não foram executados instaladores, scripts ou exemplos
do pacote. Somente três headers foram preparados na pasta work para compilação
local; nenhum arquivo do SDK entrou no pacote de fontes FL Commons.

## Evidências no pacote

| Local | Evidência e consequência |
| --- | --- |
| doc/general.html | destinado a criar plugins do FL, não hosts alternativos de plugins; a API nativa deve viver no contexto de um plugin carregado pelo FL |
| doc/titlescreen.html | copyright Image-Line, todos os direitos reservados; documentação informa que ainda não foi atualizada para a versão 1.6 |
| source/c/fp_plugclass.h, linha 365 | TFruityPlugHost::Dispatcher usa TPluginTag e intptr_t |
| mesmo header, linha 793 | FHD_Transport: Play e Stop suportados; retorno pode indicar tratamento por diferentes destinos ou adiamento |
| source/c/generictransport.h | FPT_Play é Play/Pause; FPT_Stop é Stop; valor 1 representa switch |
| fp_plugclass.h, linhas 280–289 | distinção de callbacks GUI/mixer; Idle_Public é GUI |
| mesmo header, linhas 749–750 | leitura de tempo de mixer/playback |
| mesmo header, linha 774 | leitura de informações do projeto |
| mesmo header, linhas 978–990 | contexto de track: leitura e algumas alterações; não comprova enumeração de todas as tracks |

Os números de linha acima usam quebras normalizadas do header original (CR removido).
O SDK não é uma API REST universal pronta. O seu nome/data e os headers disponíveis
não comprovam suporte ao FL 26. O único alvo atual é o build mais recente instalado,
26.1.7.5653; não será mantida compatibilidade com o FL 2025 nesta fase.

## Implementação e teste realizados

[Módulo de transporte nativo](../native/transport_commands.h) escrito pelo projeto,
com teste contra headers do SDK e dispatcher controlado. MSVC x64 compilou o teste,
que validou Play/Pause, Stop, códigos de retorno, comando inválido e bloqueio de
thread. Sem interação com um projeto do FL, sem injeção e sem alterações do executável.

O pacote consultado não contém um arquivo de licença identificado que autorize
redistribuição dos headers/exemplos sob MIT. O propósito documentado é construir
plugins; preservar o SDK como dependência externa fornecida pelo usuário evita
incluí-lo na licença original do FL Commons. Redistribuição de materiais ou código
do SDK exigirá termos específicos; esta entrega não concede direitos da Image-Line.

Ainda falta implementar o plugin que alojará a própria API, verificar ciclo de
vida/thread e executar as chamadas documentadas no FL 26. O serviço Python não
anuncia comandos nativos como disponíveis enquanto essa ligação não estiver validada.
