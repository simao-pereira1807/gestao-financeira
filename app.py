import streamlit as st
import requests
import pandas as pd

# Login
USERNAME = st.secrets["login"]["USERNAME"]
PASSWORD = st.secrets["login"]["PASSWORD"]

# Configurar a página
st.set_page_config(page_title="Gestão Financeira", page_icon="💰", layout="centered")

# Verificar login
def verificar_login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔒 Login")

        user_input = st.text_input("Usuário")
        password_input = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user_input == USERNAME and password_input == PASSWORD:
                st.session_state.autenticado = True
                st.success("🎉 Acesso permitido!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        st.stop()

# Verificar login antes de carregar a aplicação
verificar_login()

# API Endpoint e API Key
API_KEY = st.secrets["general"]["API_KEY"]
API_URL = st.secrets["general"]["API_URL"]

# Criar ou recuperar a lista de transações temporárias
if "historico_transacoes" not in st.session_state:
    st.session_state.historico_transacoes = []  # Lista vazia inicialmente

# Criar o formulário de entrada
st.title("📊 Inserir Transações")

tipo = st.selectbox("💳 Tipo de Transação", ["Despesa", "Recebimento"], index=0, key="tipo_transacao")

with st.form("transacao_form"):
    data = st.date_input("📅 Data da Transação")

    if tipo == "Despesa":
        categoria = st.selectbox("📂 Categoria", [
            "Animal", "Combustível", "Calçado", "Ginásio", "Lazer", "Outros", "Prestação",
            "Propinas", "Restaurante", "Roupa", "Saúde", "Subscrições", "Supermercado",
            "Tecnologia", "ViaVerde"
        ])
    else:
        categoria = "N/A"

    descricao = st.text_input("📝 Descrição")
    valor = st.number_input("💰 Valor (€)", min_value=0.01, format="%.2f")

    submit_button = st.form_submit_button("📤 Submeter")

# Se clicar em "Submeter", adiciona a transação ao histórico e envia para a API
if submit_button:
    nova_transacao = {"data": str(data), "tipo": tipo, "categoria": categoria, "descricao": descricao, "valor": valor}

    # Adiciona à lista local
    st.session_state.historico_transacoes.insert(0, nova_transacao)  # Insere no início para manter ordem cronológica

    # Envia para a API
    headers = {"x-api-key": API_KEY}
    resposta = requests.post(API_URL, json=nova_transacao, headers=headers)

    try:
        resposta_json = resposta.json()
    except requests.exceptions.JSONDecodeError:
        resposta_json = {"status": "error", "message": "Resposta inválida da API"}

    if resposta.status_code == 200 and resposta_json["status"] == "success":
        st.success("🎉 Transação guardada com sucesso!")
    else:
        st.error(f"❌ Erro ao guardar transação: {resposta_json}")

# Exibir Histórico de Transações com Scrolling
st.subheader("📋 Últimas Transações")

if st.session_state.historico_transacoes:
    df_historico = pd.DataFrame(st.session_state.historico_transacoes)
    st.dataframe(df_historico, height=300)  # Permite scroll na tabela
else:
    st.info("Ainda não há transações registadas.")
