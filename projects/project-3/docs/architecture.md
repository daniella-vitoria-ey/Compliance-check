# Arquitetura do Sistema

## Visão Geral

O sistema é composto por três projetos integrados:

- Projeto 1 → API simples de análise
- Projeto 2 → API com RAG (IA + base de conhecimento)
- Projeto 3 → Agente autônomo responsável pela automação

O Projeto 3 atua como orquestrador e utiliza a API RAG do Projeto 2 para tomar decisões inteligentes.

---

## Componentes do Sistema

### Monitor de Diretório
Observa a pasta data/input e detecta novos arquivos.

Função:
- Disparar o processamento automático

---

### Agente de Compliance

Executa o fluxo completo:

- Ler arquivo
- Validar conteúdo
- Chamar API
- Interpretar resposta
- Tomar decisão
- Executar ação

---

### API RAG (Projeto 2)

Responsável pela análise inteligente.

Entrada:
- Texto do documento

Saída:
- is_compliant (True ou False)
- reason (explicação da decisão)

---

### File Manager

Responsável por mover arquivos:

- approved
- rejected_for_review

---

### 🔹 Logger

Registra todo o processo:

- rastreabilidade
- auditoria
- debug

---

## Fluxo do Sistema

1. Detecta arquivo em data/input
2. Lê conteúdo
3. Valida conteúdo (evita vazio)
4. Envia para API RAG
5. Recebe resposta
6. Decide:
   - Conforme → approved
   - Não conforme → rejected_for_review
7. Move arquivo
8. Gera log

---

## Modelo de Execução

Pipeline do agente:

START → READ → ANALYZE → DECIDE → ACT → END

Cada etapa é separada e organizada.

---

## Estrutura de Pastas

project-3/
- src/
  - agents/
  - core/
  - services/
- data/
  - input/
  - output/
    - approved/
    - rejected_for_review/
- docs/
  - architecture.md
  - decisions.md

---

## Comunicação

- O agente se comunica com a API via HTTP
- Método: POST
- Endpoint: /analyze

---

## Tomada de Decisão

- is_compliant = True → aprovado
- is_compliant = False → rejeitado + alerta

---

## Características

- Arquitetura modular
- Separação de responsabilidades
- Uso de IA (RAG)
- Escalável e reutilizável

---

## Evoluções Futuras

- Uso de LangGraph
- Métricas de performance
- Dashboard
- Observabilidade (OpenTelemetry)

---

## Conclusão

A arquitetura permite:

- Automação completa do fluxo
- Decisão baseada em IA
- Redução de trabalho manual

Resultado: sistema inteligente de compliance automatizado
