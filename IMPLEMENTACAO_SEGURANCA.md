# Implementação de segurança e confiabilidade

## Escopo

Esta entrega implementa as prioridades técnicas aprovadas para o backend MDE. A pasta `docs/` não foi alterada nem incluída no versionamento.

## Alterações realizadas

### Rotas e tratamento de erros

- Corrigidas duplicações, código morto e erros de indentação nas rotas de datasets e análises.
- Rotas passaram a resolver dependências dinamicamente, permitindo isolamento correto nos testes.
- Erros internos retornam mensagem genérica e um `correlation_id`, sem expor detalhes de infraestrutura.
- Respostas incluem o cabeçalho `X-Correlation-ID` para rastreamento.
- Adicionada política básica de Content Security Policy.

### Uploads e armazenamento

- Uploads aceitam somente arquivos CSV com extensões e tipos MIME permitidos.
- Persistência usa streaming em blocos, com limite máximo de 50 MB.
- Arquivos parciais são removidos quando ocorre falha ou excesso de tamanho.
- Nomes e diretórios são validados contra traversal, separadores de caminho e caracteres NUL.

### Auditoria

- Adicionado logger estruturado em JSON para eventos de autenticação, upload, consulta e análise.
- Eventos registram ação, usuário, recurso, resultado, IP e correlation ID.
- Senhas, tokens, conteúdo de arquivos e payloads sensíveis não são registrados.

### Segurança de autenticação

- O rate limiter agora exige explicitamente a dependência `slowapi`; falhas não são silenciosamente ignoradas.
- Fluxos de registro e login passaram a emitir eventos de auditoria de sucesso ou rejeição.

### Testes e CI

- Ampliados testes de segurança para auditoria, streaming, limites de arquivo, MIME e respostas de erro.
- Adicionado workflow GitHub Actions para instalar dependências e executar a suíte backend.
- Resultado local: `31 passed`.

## Ambiente Python

As dependências foram instaladas e os testes executados em `backend/.venv`. A ativação por `activate.bat` funciona; o PowerShell local bloqueia `Activate.ps1` por política de execução, sem alteração da política global.

## Fora do escopo desta entrega

Docker Compose, `.env.example` e migrations permanecem pendentes. Essas mudanças pertencem à etapa de infraestrutura e persistência, não foram implementadas nesta entrega.
