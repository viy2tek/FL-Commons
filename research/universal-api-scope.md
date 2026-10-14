# Investigação do sistema para uma API ampla

Objetivo: uma API comunitária para os diferentes domínios do FL Studio, sem
serviço Bridge separado, sem MIDI obrigatório e só para a versão mais recente
instalada. Alvo atual: **26.1.7.5653**.

Esta etapa mapeou interfaces do SDK fornecido, não todo o código interno do FL.
O SDK não contém o código-fonte do motor, mixer, editores ou Browser do aplicativo.

## Evidência extraída

Arquivo: fpsdk_20210311b.zip. SHA-256:
`a29c5bfbfd576ab9798574920ce911a7b4fe68c2aa7d11bec2546cdf4a6b35b1`.
Membro: source/c/fp_plugclass.h. Linhas normalizadas pela remoção de CR.
Encontrados **87 seletores FHD_ com valor numérico literal**. Essa contagem não
representa todas as funções ou recursos do FL Studio.

O [catálogo estruturado](../fl_commons/data/sdk_catalog.json) registra símbolos,
IDs, linhas, estados, hash do membro e classificação, sem incluir os headers
ou implementações da Image-Line. A divisão em dez domínios é **inferência do
analista**, não uma classificação publicada pelo SDK.

| Domínio | Evidência do SDK | Limite observado |
| --- | --- | --- |
| Transporte | FHD_Transport=79; FPT_Play/FPT_Stop | Play/Pause é toggle; retorno pode indicar adiamento |
| Projeto | FHD_GetProjectInfo=61 | metadados, não grafo completo do projeto |
| Notas | FHD_AddNotesToPR=17; FHD_NoteOn=20; FHD_NoteOff=21 | contexto de plugin/canal, sem acesso global comprovado |
| Contexto de track | FHD_GetContextInfo=76 e FHD_SetContextInfo=77; CI_Track* | não prova enumeração ou edição de todo o mixer |
| Arquivos | FHD_GetPath=29; FHD_LocatePlugin=7; FHD_LocateDataFile=14 | localização no host; não revela o algoritmo completo de busca |
| Parâmetros | OnParamChanged e ProcessParam; menus publicados | não prova controle de qualquer plugin de terceiros |
| Áudio/roteamento | GetInBuffer/GetOutBuffer e FHD_GetNumInOut=50 | contexto e restrições de momento/thread |
| Ciclo de vida/UI | Dispatcher, Idle_Public, DestroyObject | requer alojamento no FL e respeito às threads |
| Conteúdo | seletores de download/media | não utilizados nem testados pela API |
| MIDI opcional | seletores MIDI publicados | fora do caminho principal solicitado |

## Funcionalidade entregue

`sdk.catalog` é uma operação de consulta pela API autenticada e SDK Python, com
filtro de domínio e paginação, disponível sem FL aberto e sem MIDI.

```python
page = client.sdk_catalog(domain='transport', limit=32)
print(page['source'])
print(page['entries'])
```

Estados: declared_unverified, reserved, obsolete e contract_tested. Este último
indica apenas o teste C++ controlado de FHD_Transport. `fl_runtime_tested: false`
e `callable_via_api: false` continuam explícitos. Símbolos FHD_ não são aceitos
como comandos arbitrários. O catálogo não é descoberta automática do executável.

## Trabalho necessário para controle amplo

1. Componente nativo e HTTP implementados para o build-alvo, com testes de fila,
   autenticação e encerramento em host controlado. Carregamento e recusa de pedido
   sem token observados no FL. Leitura autenticada de compatibilidade e estado
   inicial e Play-Pause-Play-Stop comprovados; falta ciclo de vida completo no FL.
   Veja [componente nativo](../native/README.md).
2. Validar operações reais por domínio: primeiro estado/transporte, depois projeto,
   contexto de mixer, parâmetros e notas. A thread HTTP não chamará o host diretamente.
3. Registrar entrada, saída, unidade, efeito, contexto, thread, falhas e testes por
   operação. Reservado/obsoleto não será habilitado indiscriminadamente.
4. Interfaces não expostas permanecem desconhecidas ou indisponíveis. Pesquisa
   adicional precisa respeitar as condições autorizadas de licenças/interfaces e
   manter APIs internas não documentadas fora do núcleo estável.

Ainda não foram recuperados implementação da busca, índice/tags do Browser,
grafo completo do projeto, enumeração universal de plugins/canais/padrões,
agendamento DSP ou formatos privados. O relatório não afirma recuperação de
código-fonte original nem que a API universal já esteja implementada.
