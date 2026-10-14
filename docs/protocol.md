# MIDI wire protocol 1

Pacote experimental: `F0 7D 46 43 01 <JSON ASCII> F7`, no máximo 4096 bytes.
0x7D é reservado a desenvolvimento/uso não comercial; não é um identificador
de fabricante atribuído ao FL Commons. Antes de lançamento público do transporte,
comercial ou gratuito, defina uma atribuição/enquadramento válido e migre o
protocolo. Esta entrega é um snapshot de pesquisa privada. Veja a
[explicação no fórum da MIDI Association](https://midi.org/community/postid/4226).
A interoperabilidade aqui exige os dois endpoints FL Commons e portas dedicadas.
Não há fragmentação nem envio de dados arbitrariamente grandes.

Envelope: `{body: <object>, mac: <64 hex chars>}`. HMAC-SHA256 sobre o JSON do body
com sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False.
Os bytes de transporte são ASCII e não contêm dados MIDI de 8 bits internos.
O MAC autentica e detecta alteração; não cifra o tráfego. Chaves de no mínimo
32 caracteres ASCII, geradas aleatoriamente. Mensagens não autenticadas são
descartadas sem resposta. Toda resposta também recebe MAC.

Request body: `kind: request`, `protocol: 1`, `client: <random UUID hex>`,
`id: <random UUID hex>`, `seq: <positive increasing integer>`,
`boot: <adapter nonce or null for hello>`, `method`, `params: {}`,
`sent_at: <Unix seconds>`. Timestamp deve estar a até 30 segundos do receptor.
Protocol/client/id/seq correlacionam a resposta. Início da sessão usa
`bridge.hello`, que devolve catálogo, versões e boot nonce.

Response body: `kind: response`, `protocol: 1`, mesmos client/id/seq,
`boot: <current nonce>`, `ok: true, result: ...` ou
`ok: false, error: {code, message}`. Recebimento de frame inválido, assinatura
errada ou identificação diferente não encerra a espera da requisição correta.

Um request por vez, prazo padrão de 1,5 s por tentativa. Hello e state repetem
o mesmo frame até três vezes. Escritas enviam uma vez. O dispatcher mantém
128 respostas e a sequência mais alta de cada um de até 16 clientes. Duplicata
idêntica retorna a resposta armazenada; sequência antiga, mesmo após expulsão
do cache, não executa. Uma sessão nova muda o boot nonce e bloqueia comandos
antigos. Não há garantia de execução única através de reinicialização, queda
durante execução ou nova submissão HTTP. Em falha de host, uma escrita pode ter
executado parcialmente e não deve ser repetida automaticamente.

MIDI externo: fila de até 128 frames; FL: fila de até 16, no máximo dois por
OnIdle. Frames excedentes são descartados, provocando retry de leitura ou erro
explícito de escrita. FL não processa comandos se a saída linked não estiver
atribuída. Resposta confirma retorno da função, não audita estado acústico nem
persistência do projeto. O recebimento e a execução ocorrem em callbacks do FL;
nenhuma thread externa chama sua API.
