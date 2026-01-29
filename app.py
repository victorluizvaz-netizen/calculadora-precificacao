import streamlit as st
import pandas as pd
import math

# --- CONFIGURAÇÃO DA PÁGINA E CSS CUSTOMIZADO ---
st.set_page_config(page_title="Precificador Pro", layout="wide")

# Injetando o CSS do seu HTML para transformar o visual do Streamlit
st.markdown("""
    <style>
    /* Fundo Gradiente igual ao seu HTML */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #0F172A;
    }
    
    /* Estilização dos Cards de Entrada e Grid */
    div[data-testid="stExpander"], .stDataFrame, div[data-testid="stMetricValue"] {
        background-color: white !important;
        border-radius: 20px !important;
        padding: 10px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }

    /* Títulos em Branco para contrastar com o fundo */
    h1, h2, h3, p {
        color: white !important;
    }

    /* Botão Primário Estilizado */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }

    /* Badges de Plataforma */
    .badge-ml {
        background-color: #FFE600;
        color: #0F172A;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-shopee {
        background-color: #EE4D2D;
        color: white;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS DE NEGÓCIO E TAXAS ---
CATEGORIAS = {
    "Eletrônicos": {"ml": 0.12, "shopee": 0.14},
    "Moda e Acessórios": {"ml": 0.12, "shopee": 0.13},
    "Casa e Decoração": {"ml": 0.11, "shopee": 0.12},
    "Esportes": {"ml": 0.12, "shopee": 0.13},
    "Outros": {"ml": 0.12, "shopee": 0.14}
}

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def arredondar_psicologico(preco):
    if preco <= 0: return 0.0
    return math.ceil(preco) - 0.10

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete):
    # Baseado na lógica do seu script HTML
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0.0, 0.0, 0.0
    
    preco_base = (custo + taxa_fixa + frete) / denominador
    preco_final = arredondar_psicologico(preco_base)
    
    lucro = preco_final - custo - (preco_final * (imposto/100)) - (preco_final * comissao) - taxa_fixa - frete
    margem = (lucro / preco_final) * 100 if preco_final > 0 else 0
    return preco_final, lucro, margem

# --- INTERFACE ---
if 'db' not in st.session_state:
    st.session_state.db = []

st.markdown("<h1 style='text-align: center;'>💰 Calculadora de Precificação</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Calcule o preço ideal para vender no Mercado Livre e Shopee</p>", unsafe_allow_html=True)

# Container de Entrada (Simulando o Card Branco do seu HTML)
with st.container():
    st.markdown("<h3 style='color: #0F172A !important;'>📦 Dados do Produto</h3>", unsafe_allow_html=True)
    with st.expander("Clique para expandir o formulário", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto", placeholder="Ex: Smartwatch")
            custo = st.number_input("Custo de Aquisição (R$)", min_value=0.0, value=50.0)
            categoria = st.selectbox("Categoria", list(CATEGORIAS.keys()))
        with col2:
            markup = st.slider("Margem Desejada (%)", 5, 50, 30)
            imposto = st.number_input("Imposto Simples Nacional (%)", value=6.0)
            frete = st.number_input("Custo de Frete (Se grátis)", value=0.0)

        tipo_ml = st.radio("ML: Tipo de Anúncio", ["Clássico", "Premium"], horizontal=True)
        shopee_fg = st.checkbox("Shopee: Programa Frete Grátis (Taxa 20%)")

        if st.button("CALCULAR PREÇO"):
            # Lógica ML
            taxa_ml = CATEGORIAS[categoria]["ml"] + (0.05 if tipo_ml == "Premium" else 0.0)
            fixa_ml = 6.75 if custo < 79 else 0
            p_ml, l_ml, m_ml = calcular_venda(custo, markup, imposto, taxa_ml, fixa_ml, frete)

            # Lógica Shopee
            taxa_sh = 0.20 if shopee_fg else 0.14
            p_sh, l_sh, m_sh = calcular_venda(custo, markup, imposto, taxa_sh, 4.0, frete)

            st.session_state.db.append({
                "Produto": nome, "Custo": custo,
                "Preço ML": p_ml, "Lucro ML": l_ml, "Margem ML": f"{m_ml:.1f}%",
                "Preço Shopee": p_sh, "Lucro Shopee": l_sh, "Margem Shopee": f"{m_sh:.1f}%"
            })
            st.rerun()

# --- RESULTADOS ESTILIZADOS ---
if st.session_state.db:
    st.markdown("### 📊 Comparativo de Resultados")
    item = st.session_state.db[-1] # Pega o último calculado
    
    res_ml, res_sh = st.columns(2)
    
    with res_ml:
        st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 20px; border-top: 6px solid #FFE600;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #0F172A; font-weight: bold; font-size: 1.2em;">Mercado Livre</span>
                    <span class="badge-ml">ML</span>
                </div>
                <hr>
                <p style="color: #64748B !important; margin:0;">Preço Recomendado:</p>
                <h2 style="color: #0F172A !important; margin:0;">{format_brl(item['Preço ML'])}</h2>
                <p style="color: {'#10B981' if item['Lucro ML'] > 0 else '#EF4444'} !important; font-weight: bold;">
                    Lucro: {format_brl(item['Lucro ML'])} ({item['Margem ML']})
                </p>
            </div>
        """, unsafe_allow_html=True)

    with res_sh:
        st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 20px; border-top: 6px solid #EE4D2D;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #0F172A; font-weight: bold; font-size: 1.2em;">Shopee</span>
                    <span class="badge-shopee">SHOPEE</span>
                </div>
                <hr>
                <p style="color: #64748B !important; margin:0;">Preço Recomendado:</p>
                <h2 style="color: #0F172A !important; margin:0;">{format_brl(item['Preço Shopee'])}</h2>
                <p style="color: {'#10B981' if item['Lucro Shopee'] > 0 else '#EF4444'} !important; font-weight: bold;">
                    Lucro: {format_brl(item['Lucro Shopee'])} ({item['Margem Shopee']})
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Grid Histórico
    st.markdown("<br><h3 style='color: white !important;'>📋 Histórico Completo</h3>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.db)
    st.dataframe(df, use_container_width=True)

    if st.button("🗑️ LIMPAR HISTÓRICO"):
        st.session_state.db = []
        st.rerun()
