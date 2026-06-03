# Architectural Decisions

## Estrutura do Sistema
- Projeto 1 → API simples
- Projeto 2 → API com RAG (IA)
- Projeto 3 → Agente autônomo

## Fluxo do Agente
1. Detecta arquivo
2. Lê conteúdo
3. Chama API do Projeto 2
4. Recebe resposta (is_compliant)
5. Decide automaticamente
6. Executa ação:
   - approved
   - rejected_for_review + alerta

## Design
O agente foi implementado como um pipeline com estado:

- read_file
- analyze
- decide
- act

Cada etapa é separada, simulando um grafo de estados (inspirado em LangGraph)

## Ferramentas
- API Client → análise com IA
- File Manager → mover arquivos
- Logger → logs

## Decisões Técnicas
- Separar API e agente → mais organizado
- Usar RAG → análise inteligente
- Pipeline → código limpo
- Logs → rastreabilidade

## Trade-offs
Simples e funcional  
Não usa LangGraph direto  
MCP não implementado  

## Futuro
- Usar LangGraph
- Adicionar métricas
- Dashboard

## Conclusão
Sistema de agente autônomo que usa IA para automatizar análise de compliance.