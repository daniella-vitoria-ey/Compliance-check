# Arquitetura da Solução

## Visão Geral

A solução foi desenhada como uma plataforma modular de automação de compliance. O sistema recebe documentos `.txt`, executa uma análise de conformidade a partir da lógica RAG da etapa anterior e realiza automaticamente a ação operacional correspondente.

A arquitetura separa claramente:
- entrada do documento;
- orquestração do agente;
- comunicação via MCP;
- análise RAG;
- movimentação do arquivo;
- alertas;
- métricas e status.

---

## Componentes Principais

### 1. Camada de Entrada

A entrada pode ocorrer de duas formas:

#### a) Diretório monitorado
O `Monitor` observa `data/input` e dispara o agente quando um novo `.txt` é detectado.

#### b) Upload via API
A rota `POST /agent/upload-document` salva o arquivo em `data/input`, reutilizando o mesmo fluxo do monitor.

---

### 2. Camada de Orquestração

O `ComplianceAgent` é o orquestrador do processo. Ele foi implementado com `LangGraph`, modelando o fluxo como um grafo de estados.

O estado de cada documento carrega:
- caminho do arquivo;
- conteúdo;
- perfil do cliente;
- resultado da análise;
- destino final;
- status;
- mensagem de erro;
- tempo de análise.

---

### 3. Camada MCP

A comunicação entre o agente e suas ferramentas foi formalizada com `FastMCP`.

#### Cliente MCP
Responsável por invocar tools e acessar recursos.

#### Servidor MCP
Responsável por expor:
- `analyze_recommendation`;
- `move_document`;
- `create_alert`;
- recurso `metrics://automation`.

---

### 4. Camada de API

A API FastAPI expõe:

#### Análise
- `POST /analyze`

#### Controle do agente
- `POST /agent/start-monitor`
- `POST /agent/stop-monitor`
- `GET /agent/status`
- `POST /agent/upload-document`
- `GET /agent/last-result`
- #### Métricas
- `GET /metrics/summary`
- `GET /metrics/raw`

---

### 5. Camada de Serviço de Compliance

O serviço `analyze_text`:
- recupera os chunks relevantes da base;
- aplica reranqueamento;
- constrói o prompt;
- chama o LLM;
- normaliza o retorno;
- entrega uma resposta estruturada.

Estrutura de saída:

```json
{
  "is_compliant": true,
  "reason": "string",
  "mentioned_products": [],
  "sources": [
    {
      "source_document": "string",
      "source_chunk_id": "string"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}

Além dos campos de decisão e justificativa, a resposta inclui informações de uso do modelo de linguagem (`usage`), permitindo acompanhar o consumo de tokens e estimar o custo operacional da análise.
```

---

### 6. Camada RAG

#### Ingestão
Lê documentos da base, faz chunking e persiste no ChromaDB.

#### Recuperação
Seleciona os documentos mais relevantes para a consulta.

#### Reranking
Refina a ordem dos resultados antes da montagem do prompt.

---

### 7. Infraestrutura Operacional

#### `agent_status.py`
Persiste o resultado mais recente do agente.

#### `metrics.py`

Responsável por persistir métricas operacionais e calcular indicadores de desempenho do agente.

As métricas incluem:

- volume processado:
  - `total_processed`
  - `approved_count`
  - `review_count`
  - `error_count`

- desempenho:
  - `total_analysis_time_seconds`
  - `average_analysis_time`

- indicadores de negócio:
  - `automation_success_rate`
  - `manual_intervention_rate`

- custo operacional de LLM:
  - `total_prompt_tokens`
  - `total_completion_tokens`
  - `total_tokens_used`

#### `file_manager.py`
Realiza a movimentação física dos arquivos.

#### `logger.py`
Centraliza logs da aplicação.

#### `paths.py`
Centraliza caminhos absolutos do projeto para evitar inconsistências entre execução local, API e monitor.

---

## Fluxo Arquitetural de Ponta a Ponta

1. O documento chega em `data/input`.
2. O monitor detecta o novo arquivo.
3. O agente lê o conteúdo.
4. O agente valida o documento.
5. O agente chama a tool MCP `analyze_recommendation`.
6. O MCP chama a rota `/analyze`.
7. O serviço de compliance executa a análise RAG.
8. O retorno volta ao agente.
9. O agente verifica `is_compliant`.
10. O agente chama a tool `move_document`.
11. Se necessário, chama `create_alert`.
12. O sistema atualiza status, métricas e logs.

---

## Grafo de Estados do Agente

```text
(start)
   |
   v
read_file
   |
   v
validate_content
   |----------------------|
   | ok                   | error
   v                      v
analyze_document      handle_error
   |
   |----------------------|
   | ok                   | error
   v                      v
check_compliance      handle_error
   |
   v
take_action
   |
   v
(end)
```

---

## Estado do Documento

O agente manipula um `DocumentState` com:
- `file_path`
- `content`
- `client_profile`
- `result`
- `destination`
- `status`
- `error_message`
- `analysis_time_seconds`

Esse estado torna a execução explícita e auditável.

---

## Contratos MCP

### Tool: `analyze_recommendation`
Entrada:

```json
{
  "text": "string",
  "client_profile": "string"
}
```

Saída:

```json
{
  "is_compliant": true,
  "reason": "string",
  "mentioned_products": [],
  "sources": []
}
```

### Tool: `move_document`
Entrada:

```json
{
  "source": "string",
  "destination": "string"
}
```

Saída:

```json
{
  "success": true,
  "source": "string",
  "destination": "string"
}
```

### Tool: `create_alert`
Entrada:

```json
{
  "message": "string"
}
```

Saída:

```json
{
  "success": true,
  "message": "string"
}
```

---

## Considerações Finais

A arquitetura foi desenhada para demonstrar claramente a evolução de um componente de análise para um sistema autônomo orientado a processo. O foco foi separar responsabilidades, manter visibilidade operacional e alinhar a implementação aos entregáveis do projeto.