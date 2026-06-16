import time
from typing import Dict, Optional

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Compliance Agent", layout="wide")
st.title("Compliance Agent")
st.write("Interface para análise via API, monitoramento do agente e dashboard de observabilidade.")


def post_json(url: str, payload: dict):
    try:
        return requests.post(url, json=payload, timeout=120)
    except Exception as e:
        st.error(f"Erro ao chamar {url}: {e}")
        return None


def post_no_body(url: str):
    try:
        return requests.post(url, timeout=120)
    except Exception as e:
        st.error(f"Erro ao chamar {url}: {e}")
        return None


def get_url(url: str):
    try:
        return requests.get(url, timeout=120)
    except Exception as e:
        st.error(f"Erro ao chamar {url}: {e}")
        return None


def poll_last_result(max_attempts: int = 15, wait_seconds: int = 2) -> Optional[Dict]:
    for _ in range(max_attempts):
        response = get_url(f"{API_BASE}/agent/last-result")

        if response is not None and response.ok:
            data = response.json()
            status = str(data.get("status", "")).lower()

            if status not in ["processing", "running", "pending", "in_progress"]:
                return data

        time.sleep(wait_seconds)

    response = get_url(f"{API_BASE}/agent/last-result")
    if response is not None and response.ok:
        return response.json()

    return None


STEP_LABELS = {
    "receive_upload": "Arquivo recebido",
    "validate_file": "Conteúdo validado",
    "save_input_document": "Arquivo salvo na entrada",
    "waiting_monitor": "Aguardando monitor",
    "monitor_detected_file": "Monitor detectou o arquivo",
    "start_processing": "Processamento iniciado",
    "analyze_recommendation": "API de análise chamada",
    "route_document": "Documento movido",
    "finish": "Processamento finalizado",
    "processing_error": "Erro no processamento",
}

STATUS_LABELS = {
    "ok": "Concluído",
    "pending": "Pendente",
    "approved": "Aprovado",
    "review": "Revisão",
    "error": "Erro",
    "running": "Em execução",
    "stopped": "Parado"
}


def humanize_step(step_name: str) -> str:
    return STEP_LABELS.get(step_name, step_name.replace("_", " ").capitalize())


def humanize_status(status: str) -> str:
    return STATUS_LABELS.get(str(status).lower(), str(status).capitalize())


def step_icon(step_name: str) -> str:
    icons = {
        "receive_upload": "📥",
        "validate_file": "✅",
        "save_input_document": "📂",
        "waiting_monitor": "⏳",
        "monitor_detected_file": "👀",
        "start_processing": "⚙️",
        "analyze_recommendation": "🤖",
        "route_document": "📤",
        "finish": "🏁",
        "processing_error": "❌",
    }
    return icons.get(step_name, "•")


def render_result_cards(final_result: Dict):
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    with col1:
        st.metric("Status", humanize_status(final_result.get("status", "-")))

    with col2:
        st.metric("Destino", final_result.get("destination", "-"))

    with col3:
        st.metric("Trace ID", final_result.get("trace_id", "-"))

    with col4:
        st.text_input("Motivo", value=str(final_result.get("reason", "-")), disabled=True)

    with col5:
        st.text_input("Arquivo processado", value=str(final_result.get("last_file", "-")), disabled=True)


def render_trace_steps(trace_id: str):
    response = get_url(f"{API_BASE}/agent/trace/{trace_id}")

    if response is None:
        st.error("Não foi possível consultar o trace.")
        return

    if not response.ok:
        st.error("Não foi possível carregar o passo a passo.")
        return

    trace_data = response.json()
    steps = trace_data.get("steps", [])

    if not steps:
        st.info("Nenhuma etapa encontrada.")
        return

    st.subheader("Passo a passo do agente")

    for idx, step in enumerate(steps, start=1):
        raw_step = step.get("step", f"etapa_{idx}")
        title = humanize_step(raw_step)
        detail = step.get("detail", "-")
        status = humanize_status(step.get("status", "-"))
        icon = step_icon(raw_step)

        with st.container():
            st.markdown(f"**{icon} {idx}. {title}**")
            st.write(detail)
            st.caption(f"Status: {status}")
            st.markdown("---")


if "last_agent_result" not in st.session_state:
    st.session_state.last_agent_result = None

if "current_trace_id" not in st.session_state:
    st.session_state.current_trace_id = None

if "show_agent_result" not in st.session_state:
    st.session_state.show_agent_result = False

if "show_agent_steps" not in st.session_state:
    st.session_state.show_agent_steps = False


tab1, tab2, tab3 = st.tabs(["Análise via API", "Agente via API", "Observabilidade"])


with tab1:
    st.subheader("Executar somente a análise de conformidade")

    text = st.text_area(
        "Texto da recomendação",
        value="Recomendamos investimento em tesouro direto para um cliente conservador.",
        height=180
    )

    profile = st.selectbox(
        "Perfil do cliente",
        ["conservador", "moderado", "agressivo", "arrojado"]
    )

    if st.button("Analisar", key="btn_analisar"):
        payload = {
            "text_to_analyze": text,
            "client_profile": profile
        }

        response = post_json(f"{API_BASE}/analyze", payload)

        if response is not None:
            if response.ok:
                st.success("Análise executada com sucesso")
                st.json(response.json())
            else:
                st.error(response.text)


with tab2:
    st.subheader("Executar o agente e acompanhar o resultado final")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("Iniciar monitor", key="btn_start_monitor", use_container_width=True):
            response = post_no_body(f"{API_BASE}/agent/start-monitor")
            if response is not None:
                if response.ok:
                    st.success("Monitor iniciado")
                else:
                    st.error(response.text)

    with col2:
        if st.button("Ver status do monitor", key="btn_status_monitor", use_container_width=True):
            response = get_url(f"{API_BASE}/agent/status")
            if response is not None:
                if response.ok:
                    data = response.json()
                    st.info(f"Status do monitor: {humanize_status(data.get('status', '-'))}")
                else:
                    st.error(response.text)

    with col3:
        if st.button("Ver resultado do agente", key="btn_show_result", use_container_width=True):
            st.session_state.show_agent_result = not st.session_state.show_agent_result

    with col4:
        if st.button("Ver passo a passo", key="btn_show_steps", use_container_width=True):
            st.session_state.show_agent_steps = not st.session_state.show_agent_steps

    with col5:
        if st.button("Parar monitor", key="btn_stop_monitor", use_container_width=True):
            response = post_no_body(f"{API_BASE}/agent/stop-monitor")
            if response is not None:
                if response.ok:
                    st.warning("Solicitação de parada enviada")
                else:
                    st.error(response.text)

    st.markdown("---")

    if st.session_state.show_agent_result:
        st.subheader("Resultado do agente")

        if st.session_state.last_agent_result:
            render_result_cards(st.session_state.last_agent_result)

            if st.session_state.last_agent_result.get("result"):
                with st.expander("Resultado retornado pela análise", expanded=False):
                    st.json(st.session_state.last_agent_result.get("result"))
        else:
            st.info("Ainda não existe resultado disponível. Envie um arquivo e depois clique aqui.")

        st.markdown("---")

    if st.session_state.show_agent_steps:
        if st.session_state.current_trace_id:
            render_trace_steps(st.session_state.current_trace_id)
        else:
            st.info("Ainda não existe passo a passo disponível. Envie um arquivo e depois clique aqui.")

        st.markdown("---")

    st.subheader("Enviar documento para processamento")

    uploaded_file = st.file_uploader("Escolha um arquivo .txt", type=["txt"])

    if uploaded_file is not None:
        try:
            preview = uploaded_file.getvalue().decode("utf-8")
        except Exception:
            preview = "Não foi possível mostrar preview."

        st.text_area("Preview do arquivo", value=preview, height=180)

        if st.button("Enviar arquivo", key="btn_send_file", use_container_width=True):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")
            }

            try:
                response = requests.post(
                    f"{API_BASE}/agent/upload-document",
                    files=files,
                    timeout=120
                )

                if response.ok:
                    upload_data = response.json()
                    st.session_state.current_trace_id = upload_data.get("trace_id")

                    st.success("Arquivo enviado com sucesso. Aguarde o processamento.")

                    with st.spinner("Processando documento..."):
                        final_result = poll_last_result(max_attempts=15, wait_seconds=2)

                    if final_result:
                        st.session_state.last_agent_result = final_result
                        st.success("Processamento concluído. Clique em 'Ver resultado do agente' ou 'Ver passo a passo'.")
                    else:
                        st.error("Não foi possível consultar o resultado final.")

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Erro ao enviar arquivo: {e}")


with tab3:
    st.subheader("Dashboard de Observabilidade")

    response = get_url(f"{API_BASE}/metrics/summary")

    if response is not None and response.ok:
        metrics = response.json()

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        col1.metric("Total Processados", metrics.get("total_processed", 0))
        col2.metric("Aprovados", metrics.get("approved_count", 0))
        col3.metric("Revisão Manual", metrics.get("review_count", 0))
        col4.metric("Taxa de Automação (%)", metrics.get("automation_success_rate", 0))
        col5.metric("Tempo Médio (s)", metrics.get("average_analysis_time", 0))
        col6.metric("Tokens Usados", metrics.get("total_tokens_used", 0))
    else:
        st.error("Não foi possível carregar as métricas.")