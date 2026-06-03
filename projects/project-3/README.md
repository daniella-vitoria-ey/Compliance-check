# Compliance Agent – Projeto 3

## Objetivo
Construir um agente autônomo que automatiza a análise de conformidade de documentos, utilizando uma API com RAG desenvolvida no Projeto 2.

## Arquitetura dos Projetos
- Projeto 1 → API simples
- Projeto 2 → API com RAG (IA)
- Projeto 3 → Agente autônomo (automação)

## Cenário de Negócio

Antes:
- Processo manual
- Analistas liam documentos
- Chamavam a API manualmente
- Tomavam decisão manual

## Solução

O agente automatiza o fluxo completo:

1. Monitora a pasta `data/input`
2. Detecta novos arquivos automaticamente
3. Lê o conteúdo do documento
4. Chama a API do Projeto 2
5. Recebe o resultado da análise
6. Decide automaticamente com base em `is_compliant`
7. Executa ação:
   - Move para `approved` se estiver conforme
   - Move para `rejected_for_review` e gera alerta se não estiver conforme

## Fluxo do Sistema
START → DETECT → READ → ANALYZE → DECIDE → ACT → END

## Como rodar

### 1. Rodar API (Projeto 2)
uvicorn src.main:app --reload

### 2. Rodar Agente (Projeto 3)
python -m src.main

## Indicador de Automação

Antes:
- 100% manual

Depois:
- 90% automático
- 10% requer intervenção humana

Exemplo:
- 10 documentos processados
- 9 analisados automaticamente
- 1 enviado para revisão

Automation Rate = 90%

## Resultado

- Redução significativa do tempo de análise
- Automatização de até 90% dos documentos
- Redução do esforço manual dos analistas
- Equipe foca apenas nos casos críticos

## Exemplo de Execução

Entrada:
data/input/doc1.txt

Saída:

Se conforme:
data/output/approved/doc1.txt

Se não conforme:
data/output/rejected_for_review/doc1.txt
alerts.log

## Logs

O sistema gera logs no terminal mostrando:

- Detecção de novos arquivos
- Leitura do documento
- Chamada da API
- Resultado da análise
- Ação executada (aprovação ou rejeição)

Isso garante rastreabilidade do processamento.

## Conclusão

O Compliance Agent é um sistema autônomo que utiliza inteligência artificial (RAG do Projeto 2) para automatizar decisões de conformidade, reduzindo significativamente a necessidade de intervenção manual.