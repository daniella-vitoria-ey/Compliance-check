import streamlit as st
import requests
import time

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Compliance Agent", layout="wide")
st.title("Compliance Agent")
st.write("Interface para análise via API, monitoramento do agente e dashboard de observabilidade.")

def post_json(url: str, payload: dict):
    try:
        response = requests.post(url, json=payload, timeout=120)
        return response
    except Exception as e:
        st.error(f"Erro ao chamar {url}: {e}")
        return None

def post_no_body(url: str):
    try:
        response = requests.post(url, timeout=120)
        return response
    except Exception as e:
        st.error(f"Erro ao chamar {url}: {e}")
        return None

def get_url(url: str):
    try:
        response = requests.get(url, timeout=120)
        return response
    except Exception as e:
        st.error(f"Erro ao chamar {url}: {e}")
        return None

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

    if st.button("Analisar"):
        payload = {
            "text_to_analyze": text,
            "client_profile": profile
        }

        response = post_json(f"{API_BASE}/analyze", payload)

        if response is not None:
            st.write("Status code:", response.status_code)
            if response.ok:
                st.success("Análise executada com sucesso")
                st.json(response.json())
            else:
                st.error(response.text)

with tab2:
    st.subheader("Executar o agente e acompanhar o resultado final")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Iniciar monitor"):
            response = post_no_body(f"{API_BASE}/agent/start-monitor")
            if response is not None:
                if response.ok:
                    st.success("Monitor iniciado")
                    st.json(response.json())
                else:
                    st.error(response.text)

    with col2:
        if st.button("Ver status do monitor"):
            response = get_url(f"{API_BASE}/agent/status")
            if response is not None:
                if response.ok:
                    st.info("Status consultado")
                    st.json(response.json())
                else:
                    st.error(response.text)

    with col3:
        if st.button("Parar monitor"):
            response = post_no_body(f"{API_BASE}/agent/stop-monitor")
            if response is not None:
                if response.ok:
                    st.warning("Solicitação de parada enviada")
                    st.json(response.json())
                else:
                    st.error(response.text)

    st.markdown("---")
    st.subheader("Enviar documento para processamento")

    uploaded_file = st.file_uploader("Escolha um arquivo .txt", type=["txt"])

    if uploaded_file is not None:
        try:
            preview = uploaded_file.getvalue().decode("utf-8")
        except Exception:
            preview = "Não foi possível mostrar preview."

        st.text_area("Preview do arquivo", value=preview, height=180)

        if st.button("Enviar arquivo"):
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
                    st.success("Arquivo enviado. Aguardando processamento...")
                    st.json(response.json())

                    time.sleep(4)

                    result_response = get_url(f"{API_BASE}/agent/last-result")

                    if result_response is not None and result_response.ok:
                        final_result = result_response.json()

                        st.subheader("Resultado do agente")
                        st.write("Arquivo processado:", final_result.get("last_file"))
                        st.write("Status final:", final_result.get("status"))
                        st.write("Destino:", final_result.get("destination"))
                        st.write("Motivo:", final_result.get("reason"))
                        st.write("Trace ID:", final_result.get("trace_id"))

                        if final_result.get("result"):
                            st.json(final_result.get("result"))
                    else:
                        st.error("Não foi possível consultar o último resultado.")

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

        st.markdown("---")
        st.json(metrics)

    else:
        st.error("Não foi possível carregar as métricas.")