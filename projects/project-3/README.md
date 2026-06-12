# Compliance Agent Platform

## Visão Geral

Este projeto implementa um agente autônomo para análise de conformidade de recomendações financeiras no contexto de Financial Services Office (FSO). A solução automatiza o fluxo operacional de ponta a ponta, desde a chegada de um novo documento até a decisão final de arquivamento ou encaminhamento para revisão humana.

O objetivo principal é reduzir o gargalo operacional de compliance, substituindo tarefas manuais repetitivas por uma execução automatizada, rastreável e orientada por métricas.

---

## Problema de Negócio

Antes da automação, o processo dependia de intervenção humana para:

- receber a minuta de recomendação;
- acionar a API de análise;
- interpretar o resultado retornado;
- decidir o destino do documento;
- mover o arquivo manualmente;
- registrar um alerta em caso de não conformidade.

Esse modelo criava um gargalo operacional e consumia tempo do time de compliance em tarefas operacionais repetitivas.

---

## Solução Proposta

A solução implementada neste projeto é o **Compliance Agent**, um agente autônomo que:

- monitora a chegada de novos arquivos no diretório `data/input`;
- lê e valida o conteúdo do documento;
- invoca a análise de conformidade utilizando a lógica RAG desenvolvida anteriormente;
- decide automaticamente com base no campo `is_compliant`;
- move o arquivo para a pasta de saída adequada;
- gera um alerta em log quando o caso exige revisão manual;
- mantém logs, status e métricas para rastreabilidade e medição de eficiência.

---

## Objetivo do Projeto

Construir um agente inteligente capaz de automatizar o fluxo de análise de conformidade de ponta a ponta, utilizando:

- orquestração de fluxo com LangGraph;
- comunicação estruturada entre agente e ferramentas via MCP;
- análise de conformidade baseada em RAG;
- monitoramento de diretório;
- métricas de automação e intervenção manual;
- logs claros e auditáveis.

---

## Entregáveis Atendidos

### 1. Fluxo de Agentes Funcional

O projeto entrega um fluxo funcional que:

- monitora `data/input/`;
- detecta novos arquivos `.txt`;
- invoca a análise de conformidade;
- decide se o documento está conforme ou não;
- move o documento para:
  - `data/output/approved` quando está conforme;
  - `data/output/rejected_for_review` quando exige revisão manual;
- cria alerta em log para documentos não conformes.

### 2. Logs e Rastreabilidade

O sistema registra eventos importantes em log, incluindo:

- detecção do arquivo;
- leitura e validação;
- chamada da análise;
- resultado da análise;
- decisão final;
- movimentação do documento;
- alertas;
- erros de execução.

Além disso:

- o último resultado processado é salvo em `logs/agent_status.json`;
- as métricas operacionais são salvas em `logs/metrics.json`.

### 3. Indicador de Automação

O projeto calcula e documenta indicadores operacionais e de negócio, incluindo:

- volume processado:
  - total de documentos analisados;
  - quantidade de casos aprovados;
  - quantidade de casos enviados para revisão;
  - quantidade de erros;

- desempenho:
  - tempo total de processamento;
  - tempo médio de análise por documento;

- indicadores de eficiência:
  - taxa de sucesso da automação;
  - taxa de intervenção manual;

- custo operacional do modelo de linguagem:
  - total de tokens de prompt;
  - total de tokens de resposta;
  - total de tokens utilizados na análise.

### 4. Documentação Arquitetural

O projeto inclui:

- `docs/architecture.md`
- `docs/decisions.md`

---

## Arquitetura Resumida

A solução foi dividida em componentes com responsabilidades claras:

- **FastAPI**: expõe a API de análise e as rotas de controle do agente;
- **LangGraph**: orquestra o fluxo do agente como um grafo de estados;
- **FastMCP**: formaliza a comunicação entre o agente e as ferramentas;
- **Watchdog**: monitora o diretório de entrada;
- **RAG**: recupera contexto e fundamenta a análise;
- **Azure OpenAI**: executa a inferência do modelo.

---

## Estrutura do Projeto

```text
project-3/
├── data/
│   ├── input/
│   └── output/
│       ├── approved/
│       └── rejected_for_review/
├── docs/
│   ├── architecture.md
│   └── decisions.md
├── logs/
│   ├── agent_status.json
│   └── metrics.json
├── knowledge_base/
├── src/
│   ├── agents/
│   │   └── compliance_agent.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── analysis.py
│   │   │   └── agent_control.py
│   │   └── schemas/
│   │       └── analysis.py
│   ├── core/
│   │   ├── agent_status.py
│   │   ├── file_manager.py
│   │   ├── llm_client.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   ├── monitor.py
│   │   └── paths.py
│   ├── mcp/
│   │   ├── client.py
│   │   └── server.py
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   └── reranker.py
│   ├── services/
│   │   └── compliance_service.py
│   └── main.py
├── frontend.py
├── requirements.txt
└── requirements_frontend.txt
```

---

## Fluxo Operacional

O fluxo executado pelo agente é:

1. um novo arquivo `.txt` é recebido em `data/input`;
2. o monitor detecta o novo arquivo;
3. o agente lê o documento;
4. o agente valida conteúdo e perfil do cliente;
5. o agente chama a tool MCP `analyze_recommendation`;
6. o servidor MCP chama a rota FastAPI `/analyze`;
7. a API executa a lógica RAG;
8. a API retorna um resultado com `is_compliant` e `reason`;
9. o agente decide o destino final do documento;
10. o agente chama a tool MCP `move_document`;
11. se necessário, o agente chama a tool MCP `create_alert`;
12. o sistema atualiza métricas, logs e status do último processamento.

---

## Formato do Documento de Entrada

Os documentos de entrada devem ser arquivos `.txt`.

Formato recomendado:

```text
client_profile: conservador
Recomendamos investimento em Tesouro Direto para preservação de capital e baixa exposição a risco.
```

Perfis aceitos:

- conservador
- moderado
- agressivo
- arrojado

Caso a primeira linha não seja informada, o sistema assume `conservador` como padrão.

---

## Rotas da API

### Análise de conformidade

**POST** `/analyze`

Exemplo de payload:

```json
{
  "text_to_analyze": "Recomendamos investimento em tesouro direto para um cliente conservador.",
  "client_profile": "conservador"
}
```

---

### Controle do agente

**POST** `/agent/start-monitor`  
Inicia o monitoramento do diretório de entrada.

**POST** `/agent/stop-monitor`  
Solicita a parada do monitor.

**GET** `/agent/status`  
Retorna o status atual do monitor.

**GET** `/agent/last-result`  
Retorna o resultado do último documento processado.

**POST** `/agent/upload-document`  
Recebe um arquivo `.txt` e o salva em `data/input` para processamento automático.

---

### Métricas

**GET** `/metrics/summary`  
Retorna um resumo com indicadores calculados, incluindo taxa de automação, taxa de intervenção manual e tempo médio de análise.

**GET** `/metrics/raw`  
Retorna os dados brutos acumulados de métricas operacionais.

---

## Indicador de Automação (Antes vs. Depois)

### Antes da automação

Todo o processo era manual:

- recebimento do documento;
- execução da análise;
- interpretação do resultado;
- movimentação do arquivo;
- abertura de alerta.

```text
Antes: 100% de intervenção manual
```

### Depois da automação

O agente passa a automatizar:

- leitura do documento;
- validação;
- análise;
- decisão;
- movimentação do arquivo;
- criação de alerta;
- atualização de métricas e status.

Assim, a intervenção humana fica restrita apenas aos casos enviados para revisão manual.

---

## Fórmulas dos Indicadores

### Taxa de sucesso da automação

```text
(approved_count + review_count) / total_processed * 100
```

Esse indicador mostra o percentual de casos concluídos pelo agente sem falha técnica.

### Taxa de intervenção manual

```text
review_count / total_processed * 100
```

Esse indicador mostra o percentual de documentos que exigiram análise humana.

### Tempo médio de análise

```text
total_analysis_time_seconds / total_processed
```

Esse indicador mostra o tempo médio de processamento por documento.

---

## Exemplo de Ganho Operacional

Exemplo de interpretação:

```text
Antes: 100% manual
Depois: 95% de automação operacional e 5% de intervenção manual
Resultado: redução expressiva de esforço operacional semanal
```

Se o fluxo manual consumisse 10 minutos por documento e houvesse 100 documentos por semana:

- antes: 1000 minutos por semana;
- depois: 50 minutos por semana;
- redução estimada: 950 minutos por semana;
- ganho aproximado: 15,8 horas semanais.

---

## Como Executar o Projeto

### 1. Criar e ativar ambiente virtual

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```powershell
pip install -r requirements.txt
pip install -r requirements_frontend.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` com:

```env
AZURE_OPENAI_KEY=...
AZURE_OPENAI_API_VERSION=...
AZURE_OPENAI_ENDPOINT=...
AZURE_DEPLOYMENT_NAME=...
```

### 4. Executar a ingestão da base de conhecimento

```powershell
python -m src.rag.ingestion
```

### 5. Subir a API FastAPI

```powershell
uvicorn src.api.main:app --reload --port 8000
```

### 6. Subir o servidor MCP

Em outro terminal:

```powershell
python -m src.mcp.server
```

### 7. Rodar o monitor diretamente (opcional)

```powershell
python -m src.main
```

### 8. Rodar o frontend (opcional)

```powershell
streamlit run frontend.py
```

---

## Como Testar

### Teste via Swagger ou frontend

1. subir a API;
2. subir o servidor MCP;
3. iniciar o monitor via `/agent/start-monitor`;
4. enviar um arquivo via `/agent/upload-document`;
5. consultar `/agent/last-result`;
6. consultar `/metrics/summary`.

### Teste via diretório monitorado

1. subir a API;
2. subir o MCP;
3. iniciar o monitor;
4. adicionar manualmente um `.txt` em `data/input`;
5. verificar a movimentação do arquivo e a atualização dos logs/métricas.

---

## Logs e Rastreabilidade

A aplicação registra logs claros e auditáveis para cada etapa importante do processo.

Também mantém:

- `logs/agent_status.json`: último caso processado;
- `logs/metrics.json`: métricas acumuladas;
- log da aplicação com eventos operacionais e de erro.

Além dos logs, o sistema registra métricas operacionais detalhadas, permitindo acompanhar não apenas o comportamento do agente, mas também seu desempenho e custo de execução. Isso inclui monitoramento de tempo de análise e consumo de tokens do modelo de linguagem, oferecendo uma visão mais completa da eficiência da solução.

---

## Guardrails Implementados

O agente foi construído com mecanismos básicos de segurança e validação:

- aceita apenas arquivos `.txt`;
- rejeita arquivos vazios;
- valida o perfil do cliente;
- exige resposta estruturada da análise;
- interrompe o fluxo em caso de erro;
- gera alerta em caso de falha grave ou necessidade de revisão manual.

---

## Limitações Atuais

- a solução não utiliza ainda ferramentas especializadas de observabilidade como OpenTelemetry, LangSmith, Prometheus ou Grafana, embora já implemente métricas operacionais e de custo que fornecem visibilidade básica sobre desempenho e execução;

---

## Conclusão

O projeto evolui uma solução de análise baseada em RAG para uma arquitetura de automação inteligente orientada a processo. Em vez de apenas produzir uma resposta analítica, o sistema assume responsabilidade sobre o fluxo operacional completo: monitora, analisa, decide, executa ações, registra evidências operacionais e mede eficiência.

Com isso, o Compliance Agent reduz gargalos manuais, aumenta a rastreabilidade do processo e libera o time de compliance para focar nos casos que realmente exigem julgamento humano.