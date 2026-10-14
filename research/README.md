# Pesquisa separada: Ghidra + REA

**Atualização:** REA conectado ao Codex e Ghidra 12.1.4 usado para análise real
de uma DLL própria. Veja [validação prática e evidências](ghidra-validation.md).
O diagnóstico e o plano abaixo registram o estado anterior à configuração feita
pelo usuário; a ligação MCP já está disponível e não precisa ser refeita.

A trilha foi solicitada para auxiliar pesquisa de integração. Nenhuma descoberta
por descompilação alimenta o núcleo estável. Evidência, hipótese e comportamento
documentado devem permanecer distintos. Usar REA não cria direitos sobre o alvo.

## Diagnóstico realizado em 13/10/2026

- REA `rea-agents` 6.4.0 executou doctor e setup dry-run pela CLI.
- Node 24.18.0 disponível. JDK Oracle 26.0.2.1 detectado; compatibilidade com
  o Ghidra pretendido não foi validada.
- Nenhuma ferramenta REA conectada nesta sessão. Registro MCP do Codex ausente.
- GHIDRA_INSTALL_DIR não definido. Nenhuma instalação Ghidra confirmada nas
  localizações verificadas. Não houve análise Ghidra nem descompilação.
- Setup dry-run propôs registro do Codex e atualização da skill; não foi aplicado.
  O plano local de configuração permanece fora do repositório público.

O [guia atual do REA](https://github.com/morluto/rea/blob/main/docs/installation.md)
indica Ghidra 12.1.x com JDK completo dentro da faixa aceita pela instalação.
Windows x64 é suporte experimental. Use a distribuição oficial do
[Ghidra](https://github.com/NationalSecurityAgency/ghidra/releases), preserve suas
licenças e verifique o checksum fornecido. Não selecione automaticamente um alvo
proprietário só porque ele está instalado.

## Alvos e sequência de pesquisa

1. Validar primeiro o provider com um binário próprio, de teste, ou aberto cuja
   licença permita a análise. Selecionar artefato explícito, hash SHA-256 e pergunta.
2. Abrir com open_binary/provider ghidra depois de confirmar disponibilidade.
   Restringir inspeção à pergunta, preservar Evidence IDs e limitações e fechar
   a sessão ao terminar. Strings ou pseudocódigo não comprovam execução real.
3. Para FL Studio, revisar direitos antes de análise do binário. A
   [EULA publicada](https://www.image-line.com/image-line-software-eula) restringe
   engenharia reversa/descompilação; permissão específica ou exceção aplicável
   deve ser documentada antes de avançar sob o requisito de interfaces permitidas.
4. Continuar os testes da API nativa oficial independentemente dessa pesquisa.
   Somente interfaces documentadas e testes por build entram no núcleo estável.

Não foram copiados binários, recursos, credenciais ou código recuperado do FL.
Nenhuma alegação de localização de APIs internas, captura automática de todas as
funções ou adaptação irrestrita a builds futuros é feita.

## Configuração local

REA e Ghidra foram configurados e verificados para a pesquisa registrada acima.
Configurações da máquina, backups e planos de instalação não fazem parte do código
público. Nenhuma configuração dessas ferramentas é necessária para usar a API.
