import time
import uuid
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from src.core.logger import get_logger
from src.core.metrics import update_metrics
from src.core.agent_status import save_agent_status
from src.mcp.client import ComplianceMCPClient
from src.tools.alert_tool import create_alert_tool

logger = get_logger(__name__)


class DocumentState(TypedDict):
    file_path: str
    content: str
    client_profile: str
    result: Dict[str, Any]
    destination: str
    status: str
    error_message: str
    analysis_time_seconds: float
    trace_id: str


class ComplianceAgent:
    def __init__(self):
        self.mcp = ComplianceMCPClient()

        workflow = StateGraph(DocumentState)

        workflow.add_node("read_file", self.read_file)
        workflow.add_node("validate_content", self.validate_content)
        workflow.add_node("analyze_document", self.analyze_document)
        workflow.add_node("check_compliance", self.check_compliance)
        workflow.add_node("take_action", self.take_action)
        workflow.add_node("handle_error", self.handle_error)

        workflow.set_entry_point("read_file")
        workflow.add_edge("read_file", "validate_content")

        workflow.add_conditional_edges(
            "validate_content",
            self.route_after_validation,
            {
                "ok": "analyze_document",
                "error": "handle_error"
            }
        )

        workflow.add_conditional_edges(
            "analyze_document",
            self.route_after_analysis,
            {
                "ok": "check_compliance",
                "error": "handle_error"
            }
        )

        workflow.add_edge("check_compliance", "take_action")
        workflow.add_edge("take_action", END)
        workflow.add_edge("handle_error", END)

        self.graph = workflow.compile()

    def process(self, file_path: str):
        trace_id = str(uuid.uuid4())

        logger.info(f"[trace_id={trace_id}] Iniciando processamento: {file_path}")

        save_agent_status({
            "last_file": file_path,
            "status": "processing",
            "destination": None,
            "reason": None,
            "result": None,
            "trace_id": trace_id
        })

        initial_state: DocumentState = {
            "file_path": file_path,
            "content": "",
            "client_profile": "",
            "result": {},
            "destination": "",
            "status": "started",
            "error_message": "",
            "analysis_time_seconds": 0.0,
            "trace_id": trace_id
        }

        final_state = self.graph.invoke(initial_state)

        logger.info(
            f"[trace_id={trace_id}] Processamento finalizado: {final_state['file_path']} | "
            f"status={final_state['status']} | destino={final_state['destination']}"
        )

        save_agent_status({
            "last_file": final_state["file_path"],
            "status": final_state["status"],
            "destination": final_state["destination"],
            "reason": final_state["result"].get("reason") if final_state.get("result") else final_state.get("error_message"),
            "result": final_state.get("result", {}),
            "trace_id": trace_id
        })

        return final_state

    def read_file(self, state: DocumentState):
        logger.info(f"[trace_id={state['trace_id']}] Lendo arquivo")

        try:
            with open(state["file_path"], "r", encoding="utf-8") as f:
                content = f.read()

            state["content"] = content

            if "client_profile:" in content.lower():
                first_line = content.splitlines()[0]
                state["client_profile"] = first_line.split(":", 1)[1].strip().lower()
                state["content"] = "\n".join(content.splitlines()[1:]).strip()
            else:
                state["client_profile"] = "conservador"

            return state

        except Exception as e:
            state["status"] = "error"
            state["error_message"] = f"Erro ao ler arquivo: {str(e)}"
            logger.exception(f"[trace_id={state['trace_id']}] {state['error_message']}")
            return state

    def validate_content(self, state: DocumentState):
        logger.info(f"[trace_id={state['trace_id']}] Validando conteúdo")

        if state["status"] == "error":
            return state

        try:
            if not state["file_path"].endswith(".txt"):
                raise ValueError("Formato inválido. Apenas .txt é permitido.")

            if not state["content"].strip():
                raise ValueError("Arquivo vazio.")

            if state["client_profile"] not in ["conservador", "moderado", "agressivo", "arrojado"]:
                raise ValueError("Perfil do cliente inválido.")

            state["status"] = "validated"
            return state

        except Exception as e:
            state["status"] = "error"
            state["error_message"] = f"Erro de validação: {str(e)}"
            logger.exception(f"[trace_id={state['trace_id']}] {state['error_message']}")
            return state

    def route_after_validation(self, state: DocumentState):
        return "error" if state["status"] == "error" else "ok"

    def analyze_document(self, state: DocumentState):
        logger.info(f"[trace_id={state['trace_id']}] Executando análise via MCP")

        if state["status"] == "error":
            return state

        start = time.perf_counter()

        try:
            result = self.mcp.call_tool(
                "analyze_recommendation",
                {
                    "text": state["content"],
                    "client_profile": state["client_profile"]
                }
            )

            if hasattr(result, "data") and isinstance(result.data, dict):
                result = result.data
            elif hasattr(result, "structured_content") and isinstance(result.structured_content, dict):
                result = result.structured_content
            elif isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
                result = result[0]

            end = time.perf_counter()

            if not isinstance(result, dict):
                raise ValueError(
                    f"Resultado da análise MCP não é um dicionário. Tipo recebido: {type(result)}"
                )

            if "is_compliant" not in result:
                raise ValueError("Resultado sem campo 'is_compliant'.")

            if "reason" not in result:
                raise ValueError("Resultado sem campo 'reason'.")

            state["result"] = result
            state["analysis_time_seconds"] = round(end - start, 2)
            state["status"] = "analyzed"

            logger.info(f"[trace_id={state['trace_id']}] Resultado da análise: {result}")
            logger.info(f"[trace_id={state['trace_id']}] Tempo de análise: {state['analysis_time_seconds']}s")

            return state

        except Exception as e:
            state["status"] = "error"
            state["error_message"] = f"Erro na análise: {str(e)}"
            logger.exception(f"[trace_id={state['trace_id']}] {state['error_message']}")
            return state

    def route_after_analysis(self, state: DocumentState):
        return "error" if state["status"] == "error" else "ok"

    def check_compliance(self, state: DocumentState):
        logger.info(f"[trace_id={state['trace_id']}] Verificando conformidade")

        is_compliant = state["result"].get("is_compliant", False)

        if is_compliant:
            state["destination"] = "data/output/approved"
            state["status"] = "approved"
            logger.info(f"[trace_id={state['trace_id']}] Documento classificado como conforme")
        else:
            state["destination"] = "data/output/rejected_for_review"
            state["status"] = "review"
            logger.warning(f"[trace_id={state['trace_id']}] Documento classificado para revisão manual")

        return state

    def take_action(self, state: DocumentState):
        logger.info(f"[trace_id={state['trace_id']}] Executando ação via MCP")

        try:
            self.mcp.call_tool(
                "move_document",
                {
                    "source": state["file_path"],
                    "destination": state["destination"]
                }
            )

            if state["status"] == "review":
                self.mcp.call_tool(
                    "create_alert",
                    {
                        "message": (
                            f"ALERTA: documento {state['file_path']} enviado para revisão. "
                            f"Motivo: {state['result'].get('reason', 'sem motivo informado')}"
                        )
                    }
                )

            usage = state["result"].get("usage", {})

            update_metrics(
                status=state["status"],
                analysis_time_seconds=state["analysis_time_seconds"],
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )

            return state

        except Exception as e:
            state["status"] = "error"
            state["error_message"] = f"Erro ao executar ação: {str(e)}"
            logger.exception(f"[trace_id={state['trace_id']}] {state['error_message']}")

            try:
                create_alert_tool(state["error_message"])
            except Exception:
                logger.exception(f"[trace_id={state['trace_id']}] Falha ao gerar alerta local")

            update_metrics(
                status="error",
                analysis_time_seconds=state["analysis_time_seconds"]
            )

            return state

    def handle_error(self, state: DocumentState):
        logger.error(f"[trace_id={state['trace_id']}] Fluxo encerrado com erro: {state['error_message']}")

        try:
            create_alert_tool(
                f"ERRO no processamento do documento {state['file_path']}: {state['error_message']}"
            )
        except Exception:
            logger.exception(f"[trace_id={state['trace_id']}] Falha até no alerta local")

        update_metrics(
            status="error",
            analysis_time_seconds=state["analysis_time_seconds"]
        )

        return state