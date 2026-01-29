import streamlit as st
import pandas as pd
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precificador Pro", layout="wide")

# CSS Ajustado para usabilidade total
st.markdown("""
    <style>
    /* Fundo Gradiente Principal */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Títulos Principais */
    h1, h2, h3, p {
        color: white !important;
        text-align: center;
        font-family: 'Outfit', sans-serif;
    }

    /* CARD BRANCO DE ENTRADA */
    div[data-testid="stExpander"] {
        background-color: white !important;
        border-radius: 20px !important;
        padding: 10px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        border: none !important;
    }

    /* AJUSTE DOS CAMPOS DE INPUT (Para ficarem visíveis) */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        color: #0F172A !important; /* Texto Escuro */
    }
    
    /* Cor do texto dentro dos campos */
    div[data-testid="stMarkdownContainer"] p {
        color: #0F172A !important; /* Labels dentro do card ficam escuras */
        text-align: left !important;
        font-weight: 600;
        margin-bottom: 5px;
    }

    /* Botão Principal */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 3em;
        font-weight: bold !important;
        border: none !important;
        margin-top: 20px;
    }

    /* Grid de Dados */
    .stDataFrame {
        background-color: white !important;
        border-radius: 15px !important;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS DE NEGÓCIO ---
CATEGORIAS = {
    "Eletrônicos": {"ml": 0.12, "shopee": 0.14},
    "Moda e Acessórios": {"ml": 0.12, "shopee": 0.13},
    "Casa e Decoração": {"ml": 0.11, "shopee": 0.12},
    "Esportes": {"ml": 0.12, "shopee": 0.13},
    "Outros": {"ml": 0.12, "shopee": 0.14}
}

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete):
    # Lógica de cálculo baseada no seu HTML
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0.0, 0.0, 0.0
    
    preco_base = (custo + taxa_fixa + frete) / denominador
    # Arredondamento psicológico (.90) do seu HTML
    preco_final = math.ceil(preco_base) - 0.10
    
    lucro = preco_final - custo - (preco_final * (imposto/100)) - (preco_final * comissao) - taxa_fixa - frete
    margem = (lucro / preco_final) * 100 if preco_final > 0 else 0
    return preco_final, lucro, margem

# --- INTERFACE ---
if 'db' not in st.session_state:
    st.session_state.db = []

st.markdown("<h1>💰 Calculadora de Precificação</h1>", unsafe_allow_html=True)
st.markdown("<p>Calcule o preço ideal para vender no Mercado Livre e Shopee</p>", unsafe_allow_html=True)

# Card de Entrada
with st.expander("📝 Formulário de Dados do Produto", expanded=True):
    # Usando colunas para organizar melhor os campos
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome do Produto", placeholder="Ex: Teclado Gamer")
        custo = st.number_input("Custo de Aquisição (R$)", min_value=0.0, value=50.0, step=1.0)
        categoria = st.selectbox("Categoria", list(CATEGORIAS.keys()))
        tipo_ml = st.radio("Mercado Livre: Tipo de Anúncio", ["Clássico", "Premium"], horizontal=True)
        
    with col2:
        markup = st.slider("Margem de Lucro Desejada (%)", 5, 50, 20)
        imposto = st.number_input("Imposto (%)", value=6.0, step=0.1)
        frete = st.number_input("Custo de Frete (R$)", value=0.0, step=1.0)
        shopee_fg = st.checkbox("Shopee: Participa do Frete Grátis?")

    if st.button("CALCULAR E ADICIONAR"):
        if nome:
            # Cálculos
            taxa_ml = CATEGORIAS[categoria]["ml"] + (0.05 if tipo_ml == "Premium" else 0.0)
            fixa_ml = 6.75 if custo < 79 else 0
            p_ml, l_ml, m_ml = calcular_venda(custo, markup, imposto, taxa_ml, fixa_ml, frete)

            taxa_sh = 0.20 if shopee_fg else 0.14
            p_sh, l_sh, m_sh = calcular_venda(custo, markup, imposto, taxa_sh, 4.0, frete)

            st.session_state.db.append({
                "Produto": nome,
                "Preço ML": p_ml, "Lucro ML": l_ml,
                "Preço Shopee": p_sh, "Lucro Shopee": l_sh
            })
            st.rerun()

# --- EXIBIÇÃO DOS RESULTADOS ---
if st.session_state.db:
    st.markdown("### 📊 Histórico de Cálculos")
    df = pd.DataFrame(st.session_state.db)
    
    # Formatação visual da tabela
    df_styled = df.copy()
    for col in ["Preço ML", "Lucro ML", "Preço Shopee", "Lucro Shopee"]:
        df_styled[col] = df_styled[col].apply(format_brl)
        
    st.dataframe(df_styled, use_container_width=True)

    if st.button("🗑️ LIMPAR TUDO", type="secondary"):
        st.session_state.db = []
        st.rerun()
