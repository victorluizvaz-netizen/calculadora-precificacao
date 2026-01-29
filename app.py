import streamlit as st
import pandas as pd
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precificador Pro", layout="wide")

# --- CSS PERSONALIZADO (Fiel ao seu HTML e Anexos) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Layer Externa: Gradiente Roxo */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Layer Interna: Cards Brancos (Anexo 1) */
    .main-container {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }

    /* Inputs dentro do card branco */
    div[data-testid="stExpander"], .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #F8FAFC !important;
        border: 2px solid #E2E8F0 !important;
        color: #0F172A !important;
    }
    
    label p { color: #0F172A !important; font-weight: 600 !important; }

    /* Comparativo (Anexo 2) */
    .comp-card {
        background: #F8FAFC;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid #E2E8F0;
    }
    .metric-label { color: #64748B; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 10px; }
    .metric-value { color: #0F172A; font-size: 1.5rem; font-weight: 700; margin: 5px 0; }
    .winner-badge { 
        background: #10B981; color: white; padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; font-weight: bold;
    }

    /* Títulos em Branco (fora dos cards) */
    .white-text { color: white !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'db' not in st.session_state:
    st.session_state.db = []

# --- FUNÇÕES DE CÁLCULO (Baseadas no seu HTML) ---
def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete):
    #
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0.0, 0.0, comissao + (taxa_fixa/100) # Erro de margem
    
    preco_base = (custo + taxa_fixa + frete) / denominador
    preco_final = math.ceil(preco_base) - 0.10 # Arredondamento .90
    
    taxas_totais = (preco_final * comissao) + taxa_fixa
    lucro = preco_final - custo - (preco_final * (imposto/100)) - taxas_totais - frete
    margem = (lucro / preco_final) * 100 if preco_final > 0 else 0
    return preco_final, lucro, margem, taxas_totais

# --- HEADER ---
st.markdown("<h1 class='white-text'>💰 Calculadora de Precificação</h1>", unsafe_allow_html=True)
st.markdown("<p class='white-text'>Calcule o preço ideal para Mercado Livre e Shopee</p><br>", unsafe_allow_html=True)

# --- CAMADA DE ADIÇÃO DE DADOS (Card Branco - Anexo 1) ---
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#0F172A'>📦 Dados do Produto</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        nome = st.text_input("Nome do Produto", placeholder="Ex: Smartwatch v8")
    with c2:
        custo = st.number_input("Custo de Aquisição (R$)", value=50.0)
    with c3:
        markup = st.number_input("Margem Desejada (%)", value=25.0)

    with st.expander("Configurações Avançadas (Impostos e Categorias)"):
        ca, cb, cc = st.columns(3)
        with ca:
            imposto = st.number_input("Imposto (%)", value=6.0)
            categoria = st.selectbox("Categoria", ["Eletrônicos", "Moda", "Casa", "Outros"])
        with cb:
            tipo_ml = st.radio("ML: Anúncio", ["Clássico", "Premium"], horizontal=True)
            frete_ml = st.number_input("Frete ML (se grátis)", value=0.0)
        with cc:
            shopee_fg = st.checkbox("Shopee Frete Grátis?")
            frete_sh = st.number_input("Frete Shopee (se grátis)", value=0.0)

    if st.button("CALCULAR E ADICIONAR PREÇO", use_container_width=True):
        # Lógica ML
        com_ml = 0.14 if tipo_ml == "Premium" else 0.10
        p_ml, l_ml, m_ml, t_ml = calcular_venda(custo, markup, imposto, com_ml, 6.75 if custo < 79 else 0, frete_ml)
        
        # Lógica Shopee
        com_sh = 0.20 if shopee_fg else 0.14
        p_sh, l_sh, m_sh, t_sh = calcular_venda(custo, markup, imposto, com_sh, 4.0, frete_sh)
        
        st.session_state.db.append({
            "Produto": nome, "Custo": custo, 
            "Preço ML": p_ml, "Lucro ML": l_ml, "Margem ML": m_ml, "Taxas ML": t_ml,
            "Preço Shopee": p_sh, "Lucro Shopee": l_sh, "Margem Shopee": m_sh, "Taxas Shopee": t_sh
        })
    st.markdown('</div>', unsafe_allow_html=True)

# --- CAMPO DE COMPARATIVO DINÂMICO (Anexo 2) ---
if st.session_state.db:
    st.markdown("<h2 class='white-text'>📊 Comparativo entre Plataformas</h2>", unsafe_allow_html=True)
    
    # Seletor de produto para carregar no comparativo
    lista_nomes = [p["Produto"] for p in st.session_state.db]
    produto_sel_nome = st.selectbox("Selecione um produto da lista para comparar:", lista_nomes, index=len(lista_nomes)-1)
    
    # Busca os dados do produto selecionado
    p_data = next(item for item in st.session_state.db if item["Produto"] == produto_sel_nome)

    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        comp1, comp2, comp3, comp4 = st.columns(4)
        
        with comp1:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Melhor Margem</div>
                <div class="metric-value">{max(p_data['Margem ML'], p_data['Margem Shopee']):.1f}%</div>
                <div class="winner-badge">{'MERCADO LIVRE' if p_data['Margem ML'] > p_data['Margem Shopee'] else 'SHOPEE'}</div>
            </div>""", unsafe_allow_html=True)
            
        with comp2:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Maior Lucro</div>
                <div class="metric-value">R$ {max(p_data['Lucro ML'], p_data['Lucro Shopee']):.2f}</div>
                <div class="winner-badge">{'MERCADO LIVRE' if p_data['Lucro ML'] > p_data['Lucro Shopee'] else 'SHOPEE'}</div>
            </div>""", unsafe_allow_html=True)
            
        with comp3:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Menor Taxa Total</div>
                <div class="metric-value">R$ {min(p_data['Taxas ML'], p_data['Taxas Shopee']):.2f}</div>
                <div class="winner-badge">{'SHOPEE' if p_data['Taxas Shopee'] < p_data['Taxas ML'] else 'MERCADO LIVRE'}</div>
            </div>""", unsafe_allow_html=True)
            
        with comp4:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Recomendação</div>
                <div class="metric-value" style="font-size: 1.1rem">{'Mercado Livre' if p_data['Lucro ML'] > p_data['Lucro Shopee'] else 'Shopee'}</div>
                <div class="winner-badge" style="background:#667eea">MELHOR OPÇÃO</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- GRID HISTÓRICO ---
if st.session_state.db:
    st.markdown("<h3 class='white-text'>📋 Histórico de Produtos</h3>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.db)
    st.dataframe(df[["Produto", "Custo", "Preço ML", "Lucro ML", "Preço Shopee", "Lucro Shopee"]], use_container_width=True)
    
    if st.button("🗑️ LIMPAR TUDO"):
        st.session_state.db = []
        st.rerun()
