# Decisões Arquiteturais

## Contexto

O objetivo do projeto é automatizar o fluxo de análise de conformidade de recomendações financeiras, reduzindo intervenção humana e transformando uma API de análise em um processo operacional autônomo.

Este documento registra as principais decisões arquiteturais adotadas.

---

## 1. Uso de LangGraph para orquestração do agente

### Decisão
O fluxo foi implementado com `LangGraph`.

### Motivação
O processo exige múltiplas etapas explícitas: ler, validar, analisar, decidir, agir e tratar erros. Um grafo de estados representa esse fluxo de forma clara e rastreável.

### Consequência
O comportamento do agente ficou mais explícito, auditável e fácil de evoluir.

---

## 2. Estado estruturado com `DocumentState`

### Decisão
Foi criado um estado tipado para transportar dados ao longo do fluxo.

### Motivação
Cada documento precisa manter contexto entre as etapas, incluindo conteúdo, perfil do cliente, resultado, destino, status e tempo de análise.

### Consequência
O fluxo ficou consistente e menos sujeito a acoplamento implícito.

---

## 3. Uso de MCP entre agente e ferramentas

### Decisão
A comunicação entre o agente e as ferramentas foi formalizada com `FastMCP`.

### Motivação
O MCP melhora o desacoplamento entre o orquestrador e a execução operacional, além de explicitar os contratos das ferramentas.

### Consequência
A solução ficou mais organizada, extensível e alinhada ao conceito de tool calling estruturado.

---

## 4. Exposição da análise via FastAPI

### Decisão
A análise de conformidade foi exposta em `POST /analyze`.

### Motivação
Isso permite reutilização, teste isolado e uma apresentação mais clara da solução, separando a inteligência de análise da automação operacional.

### Consequência
A API se tornou uma interface estável consumida pelo MCP.

---

## 5. Reaproveitamento da lógica RAG da etapa anterior

### Decisão
A solução reutiliza recuperação, reranqueamento e inferência construídos anteriormente.

### Motivação
O foco do Projeto final é automação de fluxo, não reconstrução de toda a inteligência da etapa anterior.

### Consequência
Houve continuidade arquitetural e menor retrabalho.

---

## 6. Monitoramento de diretório com Watchdog

### Decisão
O gatilho principal do agente foi implementado com `Watchdog` em `data/input`.

### Motivação
O requisito de negócio pede reação automática à chegada de novos documentos.

### Consequência
O sistema se torna orientado a evento no contexto local, mantendo simplicidade de demonstração.

---

## 7. Decisão operacional baseada em `is_compliant`

### Decisão
A regra do agente foi definida como:
- `is_compliant = true` → aprovar e arquivar;
- `is_compliant = false` → enviar para revisão manual e gerar alerta.

### Motivação
Essa regra traduz diretamente o critério de negócio do projeto.

### Consequência
O comportamento final é objetivo, claro e explicável.

---

## 8. Saída operacional em diretórios físicos

### Decisão
Foram definidos dois destinos finais:
- `data/output/approved`
- `data/output/rejected_for_review`

### Motivação
Isso facilita teste, rastreabilidade e demonstração visual do resultado do agente.

### Consequência
O fluxo final fica concreto e simples de validar.

---

## 9. Alerta simulado em log

### Decisão
O mecanismo de alerta foi implementado como um registro estruturado em log.

### Motivação
A abordagem prioriza simplicidade operacional e rastreabilidade, permitindo registrar eventos críticos de forma consistente sem introduzir dependências externas ou aumentar a complexidade do sistema.

### Consequência
Os alertas tornam-se facilmente auditáveis, garantindo visibilidade sobre casos que exigem intervenção manual, ao mesmo tempo em que mantêm a solução leve, modular e de fácil manutenção.

---

## 10. Persistência de métricas e status

### Decisão  
As informações de status do agente e as métricas operacionais são persistidas em arquivos JSON no diretório `logs/`.

### Motivação  
A abordagem prioriza simplicidade, transparência e facilidade de inspeção, permitindo acesso direto aos dados gerados pelo sistema sem necessidade de infraestrutura adicional. Essa estratégia também reduz acoplamento e mantém a solução leve durante as etapas iniciais de desenvolvimento.

Além disso, permite consolidar diferentes tipos de métricas, incluindo volume processado, desempenho operacional e custo de uso do modelo de linguagem.

### Consequência  
A solução garante visibilidade imediata sobre o comportamento do sistema, facilita processos de auditoria e debugging e permite acompanhar indicadores de eficiência e custo operacional.

A arquitetura permanece preparada para evolução futura, possibilitando a substituição por soluções baseadas em banco de dados ou ferramentas de observabilidade sem alterações significativas no restante do fluxo.

---

## 11. Centralização de caminhos do projeto

### Decisão
Foi criado um módulo `paths.py` para concentrar `BASE_DIR`, diretórios de dados, logs, base de conhecimento e ChromaDB.

### Motivação
O projeto tinha risco de inconsistência por usar caminhos relativos e absolutos em pontos diferentes.

### Consequência
A execução ficou mais robusta e previsível.

---

## 12. Inclusão de endpoint de métricas na API

### Decisão
As métricas foram expostas por meio dos endpoints:

- `GET /metrics/summary`
- `GET /metrics/raw`

### Motivação
Separar métricas agregadas e dados brutos permite atender tanto cenários de visualização direta quanto análises detalhadas.

### Consequência
Os indicadores ficam facilmente acessíveis para consumo por interfaces, testes e futuras integrações, mantendo flexibilidade e clareza na exposição dos dados.

---

## 13. Guardrails mínimos no agente

### Decisão
Foram implementados guardrails básicos:
- apenas `.txt`;
- arquivo não vazio;
- perfil válido;
- validação do retorno da análise;
- encerramento controlado em caso de erro.

### Motivação
Mesmo em ambiente de projeto, um agente autônomo precisa operar dentro de limites seguros.

### Consequência
A confiabilidade da automação aumentou.

---

## 14. Estratégia de Observabilidade Adotada


### Decisão  
A solução não inclui, nesta versão, instrumentação avançada de observabilidade com ferramentas como OpenTelemetry, LangSmith, Prometheus ou Grafana.

### Motivação  
A priorização foi dirigida à construção de um fluxo funcional completo, com foco em automação ponta a ponta e coleta de métricas operacionais e de negócio, incluindo indicadores de desempenho e consumo de tokens do modelo de linguagem.

### Consequência  
O sistema já oferece visibilidade relevante por meio de logs, métricas e indicadores calculados, permitindo monitoramento básico e análise de desempenho.

A arquitetura permanece preparada para evolução incremental, possibilitando a integração futura com ferramentas de observabilidade avançada sem necessidade de mudanças estruturais significativas.

---

## Conclusão

As decisões arquiteturais priorizaram clareza, aderência ao problema de negócio e qualidade de demonstração. O resultado final é uma solução modular, rastreável e coerente com a proposta do projeto: transformar uma análise isolada em um processo autônomo orientado a valor.