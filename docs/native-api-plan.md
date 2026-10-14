# API nativa inicial

Implementação autorizada: plugin x64 do SDK oficial, com HTTP autenticado em
127.0.0.1:3211 dentro do processo FL. Não requer servidor Python nem MIDI.
Alvo permitido: ProductVersion 26.1.7.5653. Isso delimita o alvo, não comprova compatibilidade.

Superfícies: plugin/factory e encerramento, servidor e validação HTTP, fila de
comandos atendida por Idle_Public, estado recebido em callbacks, SDK Python já
existente, build com SDK externo, testes e documentação.

Comandos iniciais: transport.state, transport.play_pause e transport.stop.
Play/Pause é alternância; uma resposta do host não comprova mudança de estado.
Fila de uma operação, prazo finito, cancelamento antes de execução e nenhuma
repetição automática. O worker nunca chama o host. Encerramento cancela pedidos
pendentes e interrompe sockets antes de aguardar o worker.

Validação: contrato oficial já testado; exercitar HTTP real em host controlado
(token, origem, Host, JSON, limites, thread, prazo e encerramento), compilar DLL
com MSVC e executar testes Python. Carregar no FL é validação separada.
Não distribuir fontes do SDK nem implementar interfaces internas não documentadas.
