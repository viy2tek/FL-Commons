# Primeiro perfil de compatibilidade do FL Commons

Plano histórico desse incremento. A leitura e o transporte no FL foram
posteriormente verificados, e o OpenAPI inicial foi adicionado. Consulte
[validação atual](validation.md) e [contrato público](public-api.md).

Objetivo autorizado: avançar a API comunitária consistente do plano original.
Este incremento usa o fluxo nativo existente: leitura autenticada de evidências
da sessão e instalação para o build mais recente. Execução inline autorizada
pela continuação do projeto; sem publicação ou atualização remota.

Superfícies: local_api.h, criação do plugin, SDK Python, testes nativos,
instalador, documentação, DLL compilada e evidências. Contratos existentes de
comando continuam aceitos. Não há alteração do executável ou escrita em projetos.

O perfil fpsdk-20210311b-transport-v1 representa três interfaces conhecidas.
GET /v1/compatibility separa declaração de observação e certificação. ID muda
por carregamento. Idle/callback observados não habilitam Mixer ou outras funções.
Nenhum probe musical de escrita é executado automaticamente.

Instalador: latest-only, build exato, impede setup com FL aberto, preserva
versões diferentes, nome nativo x64, token herdado apenas ao iniciar FL.
Uma instalação anterior é guardada antes da atualização local desta entrega.

Verificação: sockets reais em host controlado, sessão diferente após reload,
leitura sem GUI/callback não inventa atividade, autenticação do endpoint,
instalação repetível e preservação de arquivo distinto. Teste no FL é separado.

Ainda faltam operações reais por domínio, validação no FL, seleção entre
adaptadores futuros, assinaturas/atualizações/rollback remoto, eventos/WebSocket,
OpenAPI e TypeScript. Não se apresenta este perfil como engine adaptativo completo.
