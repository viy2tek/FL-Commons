# Segurança

FL Commons API v0.1 é um serviço para um único computador confiável. Não exponha sua
porta por proxy, túnel ou rede. Escuta apenas 127.0.0.1, exige token em todas as
rotas, restringe Host, rejeita Origin e não habilita CORS. O servidor HTTP usa a
biblioteca padrão para este caso local; não é infraestrutura pública de produção.

MIDI é opcional; os detalhes de chave e transporte a seguir só se aplicam quando
essa integração for explicitamente selecionada. O serviço padrão não usa MIDI.

Token HTTP e chave MIDI devem ser aleatórios. FL_COMMONS_MIDI_KEY pode separar os
segredos; por padrão reutiliza-se FL_COMMONS_TOKEN. Bundle preparado contém chave
em texto e precisa de proteção por permissões do usuário. `chmod` não garante
ACL privada no Windows: use uma pasta privada e revise suas permissões. Rotação
exige preparar uma nova pasta de bundle, substituir manualmente a configuração
do script e reiniciar os endpoints. Não distribua bundles configurados.

Autenticação protege contra outro cliente sem segredo, não contra malware, outro
processo com acesso às suas credenciais, nem administradores do computador. MIDI
e HTTP local não são cifrados. Nenhum caminho avalia código recebido; cada
adaptador tem uma lista fechada de operações e valida seus parâmetros.
Expiração, MAC, sequência e sessão se referem ao protocolo MIDI opcional.
O HTTP nativo limita fila/prazo, mas ainda não fornece request_id/deduplicação
persistente: não repetir escritas incertas nem presumir execução única.

Perda da resposta de escrita indica resultado desconhecido. Não tente novamente
automaticamente. A Bridge não oferece garantia de execução única entre falhas ou
nova submissão HTTP. Não use a v0.1 para executar ações irreversíveis não cobertas
por seu catálogo. O serviço limita corpos, filas e conexões; saturação pode fechar
conexões ou recusar operações. Uma nova conexão HTTP que falhe pode deixar uma
escrita ambígua, mesmo antes de receber um erro estruturado.

O repositório é público; ainda não há endereço de segurança designado nesta entrega.
Até essa estrutura existir, compartilhe relatos com os mantenedores pelo canal
privado acordado, sem incluir tokens, projetos privados ou dados do computador.
