# Ghidra + REA: validação prática

Foi executada análise estática real com REA 6.4.0, Ghidra 12.1.4 e JDK 26.0.2.1
em Windows x64. O alvo é uma DLL própria, criada apenas para esta verificação;
não é um binário do FL Studio nem um novo componente do núcleo da Bridge.

## Alvo e reprodução

Fonte: [fixtures/frame_probe.c](fixtures/frame_probe.c), código original MIT.
Compilador: MSVC 19.44, ferramentas x64 14.44.35207. Construção:

```text
cl /nologo /LD /GS- /Zl /Od frame_probe.c /Fo:frame_probe.obj /Fe:frame_probe.dll
   /link /NOENTRY /NODEFAULTLIB /MACHINE:X64 /IMPLIB:frame_probe.lib
```

A DLL de teste não possui rotina de entrada ou dependências de runtime C.
Foi analisada com `open_binary` selecionando explicitamente `provider_id: ghidra`,
seguido de `procedure_pseudo_code` para cada função exportada e `close_binary`.
Nenhuma execução da DLL foi solicitada.

SHA-256 antes e depois da análise:
`73ad22895a034e0b258ee9ae26461a5cdd82d536ef3068cf4b854a0cc2356299`.
O hash igual comprova que esse artefato permaneceu inalterado nessa sessão.

## Observações

| Função | Observado no pseudocódigo | Evidência |
| --- | --- | --- |
| fc_is_frame | rejeita tamanho menor que 7 ou maior que 4096; confere F0 7D 46 43 01 e F7 final | [registro completo](ghidra-frame-evidence.json), `ev_b80cb381d769b327ba5acecf50b4844678dd8d04fd74f56fd8b2defc6d5c9a46` |
| fc_next_sequence | retorna zero para 0xffffffff; caso contrário incrementa um | [registro completo](ghidra-sequence-evidence.json), `ev_3980adfba7443a38d1497cae5458aff8040c4533c7e80167252d9769526f0ed7` |

As condições descompiladas correspondem às condições da fonte de teste. Ghidra
representou alguns bytes e inteiros como valores com sinal, por exemplo -0x10
para F0 e -1 para 0xffffffff; isso não altera os padrões de bits comparados.
Tipos recuperados e nomes de parâmetros não são recuperação exata da fonte.

## Conclusão e limites

O caminho Codex → REA → Ghidra completou importação, análise padrão e descompilação
de duas funções numa DLL PE x64 pequena. `close_binary` concluiu o encerramento.
Isso valida esse fluxo neste ambiente, sem estabelecer cobertura de outros
formatos, arquiteturas, binários grandes ou comportamento executado.

O teste não implementa HMAC, parsing JSON ou todas as regras da Bridge; o fixture
só oferece lógica conhecida para conferir a ferramenta. O protocolo Python
estável não recebeu dependência de Ghidra ou código recuperado de terceiros.
O suporte Windows do provider continua experimental. A análise de binários do
FL Studio permanece fora desta validação e depende das condições descritas no
[plano de pesquisa](README.md). Não há conclusão sobre APIs internas ou
compatibilidade real da Bridge com FL Studio.
