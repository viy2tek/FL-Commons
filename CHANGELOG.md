# Changelog

## 2026-10-14 — transporte real e SDK público

- Corrigida ordem do factory oficial: Host antes de Tag, com assert de compilação.
- Play/Pause/Play/Stop confirmados pelos callbacks do FL 26.1.7.5653 em projeto de teste.
- Componente nativo recupera token DPAPI quando FL é aberto sem variável de ambiente.
- FLStudio.connect(), status() e operações de transporte no pacote público flcommons.
- --native conecta o servidor Core ao componente; status, catálogo e controle em uma API.
- OpenAPI inicial, erros de protocolo estruturados, guia para programadores e template de capability.

## 2026-10-14 — mapa de interfaces da API

- Catálogo de 87 seletores do SDK, dez domínios inferidos, hashes, linhas e estados.
- Operação `sdk.catalog` com paginação/filtro, acessível pelo SDK Python e HTTP.
- Inventário de contratos, sem habilitar chamadas nativas não testadas.

## 2026-10-14 — alvo único e contrato do SDK

- Inspeção restrita ao build mais recente instalado, sem fallback multiversão.
- SDK recebido e examinado, sem cópia de seus arquivos no repositório MIT.
- Módulo C++ para Play/Pause e Stop usando contrato público do SDK; teste compilado
  com dispatcher controlado. Integração nativa no FL ainda não executada.

## 2026-10-14 — inspeção do host

- `host.inspect` e `Client.inspect_host()` consultam instalações, versões e
  processos reais no Windows, sem MIDI, injeção, abertura de projetos ou controle.
- Identificação limitada, timeout e falha explícita; não habilita transporte musical.

## 2026-10-14 — mudança de direção da v0.1

- API e SDK independentes de MIDI; simulação direta na API.
- Servidor padrão inicia desconectado e informa integração direta indisponível.
- MIDI Scripting restrito a opção explícita `--midi` para situações específicas.
- Integração direta com FL Studio ainda não implementada ou comprovada.

## 0.1.0 — 2026-10-13, development snapshot

- Authenticated local HTTP bridge and initial Python SDK.
- Allowlisted, version-reporting FL MIDI Scripting adapter.
- Authenticated experimental SysEx wire with correlation, bounded replay defense,
  read retries and explicit ambiguous-write errors.
- Demo simulator, adapter-bundle preparation, documentation and automated tests.
- Separate REA/Ghidra research readiness plan; no proprietary binary analysis.
- No verified FL build compatibility; private research wire pending an assigned
  manufacturer ID or other permitted framing before public transport release.
