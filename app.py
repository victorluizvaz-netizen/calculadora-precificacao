import streamlit as st
import pandas as pd
import math

# --- CONFIGURAÇÃO E CSS (Fiel ao seu HTML) ---
st.set_page_config(page_title="Precificador Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Fundo Gradiente idêntico ao HTML */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Títulos em Branco */
    h1, h2, h3, .stMarkdown p { color: white !important; text-align: center; }

    /* CARD BRANCO (Estilo seu HTML) */
    .main-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
    }

    /* INPUTS VISÍVEIS (Texto Escuro e Fundo Light) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        color: #0F172A !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
    }

    /* Labels dos campos dentro do Card (Preto para leitura) */
    label[data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
        font-weight: 600 !important;
        text-align: left !important;
    }

    /* Botão Estilizado */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        width: 100%;
        transition: all 0.3s ease;
    }

    /* Cards de Resultado coloridos */
    .res-ml { border-top: 8px solid #FFE600; background: white; padding: 20px; border-radius: 15px; color: #0F172A; }
    .res-sh { border-top: 8px solid #EE4D2D; background: white; padding: 20px; border-radius: 15px; color: #0F172A; }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS DE TAXAS (Recuperadas do seu HTML) ---
#
CATEGORIAS_TAXAS = {
    "Eletrônicos": {"ml": 0.14, "shopee": 0.14},
    "Moda e Acessórios": {"ml": 0.12, "shopee": 0.13},
    "Casa e Decoração": {"ml": 0.11, "shopee": 0.12},
    "Esportes e Fitness": {"ml": 0.12, "shopee": 0.13},
    "Beleza e Cuidados": {"ml": 0.13, "shopee": 0.14},
    "Brinquedos e Jogos": {"ml": 0.13, "shopee": 0.13},
    "Outros": {"ml": 0.12, "shopee": 0.14}
}

def arredondar_psicologico(preco):
    # Lógica de arredondamento .90 do seu HTML
    return math.ceil(preco) - 0.10

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete):
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0.0, 0.0
    preco_sugerido = (custo + taxa_fixa + frete) / denominador
    preco_final = arredondar_psicologico(preco_sugerido)
    lucro = preco_final - custo - (preco_final * (imposto/100)) - (preco_final * comissao) - taxa_fixa - frete
    return preco_final, lucro

# --- INTERFACE ---
if 'historico' not in st.session_state:
    st.session_state.historico = []

# BARRA LATERAL COM TAXAS (Transparência total)
with st.sidebar:
    st.markdown("### 📊 Taxas por Categoria")
    df_taxas = pd.DataFrame([{"Cat": k, "ML": f"{v['ml']:.0%}", "SHP": f"{v['shopee']:.0%}"} for k, v in CATEGORIAS_TAXAS.items()])
    st.table(df_taxas)
    st.info("Nota: ML Premium (+4%) e Shopee Frete Grátis (+6%) são somados ao calcular.")

st.markdown("<h1>💰 Calculadora de Precificação</h1>", unsafe_allow_html=True)
st.markdown("<p>Fiel ao seu design original com inteligência de dados</p>", unsafe_allow_html=True)

# CARD PRINCIPAL DE ENTRADA
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("📦 Nome do Produto", placeholder="Ex: Smartwatch")
        custo = st.number_input("💵 Custo de Aquisição (R$)", min_value=0.0, value=50.0)
        cat = st.selectbox("📂 Categoria", list(CATEGORIAS_TAXAS.keys()))
    with c2:
        markup = st.slider("📈 Margem de Lucro Alvo (%)", 5, 50, 25)
        imposto = st.number_input("🧾 Imposto (%)", value=6.0)
        frete = st.number_input("🚚 Frete (se grátis)", value=0.0)
    
    st.markdown("<hr style='border: 1px solid #E2E8F0'>", unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3:
        tipo_ml = st.radio("Anúncio Mercado Livre", ["Clássico", "Premium"], horizontal=True)
    with c4:
        shopee_fg = st.checkbox("Participa do Frete Grátis Shopee?")

    if st.button("CALCULAR PREÇO AGORA"):
        # Lógica ML
        taxa_ml = CATEGORIAS_TAXAS[cat]["ml"] + (0.04 if tipo_ml == "Premium" else 0.0)
        fixa_ml = 6.75 if custo < 79 else 0
        p_ml, l_ml = calcular_venda(custo, markup, imposto, taxa_ml, fixa_ml, frete)
        
        # Lógica Shopee
        taxa_sh = 0.20 if shopee_fg else 0.14
        p_sh, l_sh = calcular_venda(custo, markup, imposto, taxa_sh, 4.0, frete)
        
        st.session_state.historico.append({
            "Produto": nome, "Custo": custo, "Preço ML": p_ml, "Lucro ML": l_ml, "Preço Shopee": p_sh, "Lucro Shopee": l_sh
        })
    st.markdown('</div>', unsafe_allow_html=True)

# CARDS DE RESULTADO (Estilo do seu HTML)
if st.session_state.historico:
    ultimo = st.session_state.historico[-1]
    res1, res2 = st.columns(2)
    
    with res1:
        st.markdown(f"""<div class="res-ml">
            <h3 style="color:#0F172A !important; text-align:left">Mercado Livre</h3>
            <p style="color:#64748B !important; text-align:left">Preço Recomendado:</p>
            <h2 style="color:#0F172A !important; text-align:left">R$ {ultimo['Preço ML']:.2f}</h2>
            <p style="color:#10B981 !important; text-align:left; font-weight:bold">Lucro: R$ {ultimo['Lucro ML']:.2f}</p>
        </div>""", unsafe_allow_html=True)
        
    with res2:
        st.markdown(f"""<div class="res-sh">
            <h3 style="color:#0F172A !important; text-align:left">Shopee</h3>
            <p style="color:#64748B !important; text-align:left">Preço Recomendado:</p>
            <h2 style="color:#0F172A !important; text-align:left">R$ {ultimo['Preço Shopee']:.2f}</h2>
            <p style="color:#10B981 !important; text-align:left; font-weight:bold">Lucro: R$ {ultimo['Lucro Shopee']:.2f}</p>
        </div>""", unsafe_allow_html=True)

    # HISTÓRICO EM GRID
    st.markdown("<br><h3>📋 Histórico de Precificação</h3>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.historico)
    st.dataframe(df, use_container_width=True)
