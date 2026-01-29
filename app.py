import streamlit as st
import pandas as pd
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precificador Pro", layout="wide", initial_sidebar_state="expanded")

# Estilização para aproximar do seu HTML
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .status-winner { color: #10b981; font-weight: bold; border: 1px solid #10b981; padding: 2px 8px; border-radius: 20px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- REGRAS DE NEGÓCIO (Baseadas no seu HTML) ---
CATEGORIAS = {
    "Eletrônicos": {"ml": 0.12, "shopee": 0.14},
    "Moda e Acessórios": {"ml": 0.12, "shopee": 0.13},
    "Casa e Decoração": {"ml": 0.11, "shopee": 0.12},
    "Esportes": {"ml": 0.12, "shopee": 0.13},
    "Outros": {"ml": 0.13, "shopee": 0.14}
}

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def arredondar_psicologico(preco):
    """Arredonda para terminar em .90 conforme seu HTML"""
    if preco <= 0: return 0.0
    return math.ceil(preco) - 0.10

def calcular_venda_completo(custo, markup_alvo, imposto_perc, comissao_perc, taxa_fixa, frete):
    # Fórmula: Preço = (Custo + Taxa Fixa + Frete) / (1 - Imposto - Comissão - Margem)
    denominador = 1 - (imposto_perc / 100) - comissao_perc - (markup_alvo / 100)
    
    if denominador <= 0:
        return 0.0, 0.0, 0.0
    
    preco_bruto = (custo + taxa_fixa + frete) / denominador
    preco_final = arredondar_psicologico(preco_bruto)
    
    # Recalcula valores reais baseados no preço final arredondado
    valor_comissao = (preco_final * comissao_perc) + taxa_fixa
    valor_imposto = preco_final * (imposto_perc / 100)
    lucro_real = preco_final - custo - valor_comissao - valor_imposto - frete
    margem_real = (lucro_real / preco_final) * 100 if preco_final > 0 else 0
    
    return preco_final, lucro_real, margem_real

# --- INTERFACE ---
if 'db' not in st.session_state:
    st.session_state.db = []

st.title("💰 Precificador Pro: ML & Shopee")

with st.sidebar:
    st.header("⚙️ Configurações Globais")
    regime = st.selectbox("Regime Tributário", ["Simples Nacional", "Lucro Presumido", "MEI"])
    imposto_padrao = 6.0 if regime == "Simples Nacional" else (0.0 if regime == "MEI" else 13.33)
    taxa_imposto = st.number_input("Alíquota de Imposto (%)", value=imposto_padrao)
    
    st.divider()
    st.markdown("### 📊 Taxas Atuais")
    df_taxas = pd.DataFrame([{"Cat": k, "ML": f"{v['ml']:.1%}", "SHP": f"{v['shopee']:.1%}"} for k, v in CATEGORIAS.items()])
    st.table(df_taxas)

# Formulário inspirado no seu card de entrada
with st.expander("➕ Adicionar Novo Produto para Cálculo", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        nome = st.text_input("Nome do Produto", placeholder="Ex: Smartwatch v8")
        cat_sel = st.selectbox("Categoria", list(CATEGORIAS.keys()))
        custo_in = st.number_input("Custo de Aquisição (R$)", min_value=0.0, value=50.0)
    with c2:
        margem_in = st.slider("Margem de Lucro Desejada (%)", 5, 50, 25)
        frete_in = st.number_input("Custo do Frete (Se grátis)", value=0.0)
    with c3:
        st.write("**Canais de Venda**")
        tipo_ml = st.radio("ML: Tipo de Anúncio", ["Clássico", "Premium"])
        shopee_fg = st.checkbox("Shopee: Programa Frete Grátis?")

    if st.button("🚀 Calcular e Comparar", use_container_width=True):
        # Lógica ML
        comissao_ml = CATEGORIAS[cat_sel]["ml"] + (0.05 if tipo_ml == "Premium" else 0.0)
        taxa_fixa_ml = 6.75 if custo_in < 79 else 0 # Regra ML
        p_ml, l_ml, m_ml = calcular_venda_completo(custo_in, margem_in, taxa_imposto, comissao_ml, taxa_fixa_ml, frete_in)
        
        # Lógica Shopee
        comissao_sh = 0.20 if shopee_fg else 0.14
        p_sh, l_sh, m_sh = calcular_venda_completo(custo_in, margem_in, taxa_imposto, comissao_sh, 4.0, frete_in)
        
        st.session_state.db.append({
            "Produto": nome,
            "Custo": custo_in,
            "Preço ML": p_ml,
            "Lucro ML": l_ml,
            "Margem ML": f"{m_ml:.1f}%",
            "Preço Shopee": p_sh,
            "Lucro Shopee": l_sh,
            "Margem Shopee": f"{m_sh:.1f}%",
            "Vantagem": "Mercado Livre" if l_ml > l_sh else "Shopee"
        })

# --- DASHBOARD DE RESULTADOS ---
if st.session_state.db:
    # Mostra o último cálculo em destaque (Igual aos seus cards do HTML)
    ultimo = st.session_state.db[-1]
    st.subheader(f"📊 Última Análise: {ultimo['Produto']}")
    
    res1, res2 = st.columns(2)
    with res1:
        st.info(f"**MERCADO LIVRE**\n\nPreço Sugerido: **{format_brl(ultimo['Preço ML'])}**\n\nLucro: {format_brl(ultimo['Lucro ML'])} ({ultimo['Margem ML']})")
    with res2:
        st.warning(f"**SHOPEE**\n\nPreço Sugerido: **{format_brl(ultimo['Preço Shopee'])}**\n\nLucro: {format_brl(ultimo['Lucro Shopee'])} ({ultimo['Margem Shopee']})")

    st.divider()
    
    # GRID HISTÓRICO
    st.subheader("📋 Histórico de Precificação")
    df_final = pd.DataFrame(st.session_state.db)
    
    # Aplicando formatação para o Grid
    df_grid = df_final.copy()
    for col in ["Custo", "Preço ML", "Lucro ML", "Preço Shopee", "Lucro Shopee"]:
        df_grid[col] = df_grid[col].apply(format_brl)
    
    st.dataframe(df_grid, use_container_width=True)

    # BOTÕES DE AÇÃO
    col_a, col_b = st.columns(2)
    with col_a:
        csv = df_final.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Completo", data=csv, file_name="precificacao.csv", mime="text/csv")
    with col_b:
        if st.button("🗑️ Limpar Tudo", type="secondary"):
            st.session_state.db = []
            st.rerun()
