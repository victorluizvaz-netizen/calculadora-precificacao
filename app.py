import streamlit as st
import pandas as pd
import math

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Precificador Pro", layout="wide")

# --- CSS PERSONALIZADO (Layer Externa Roxa + Layers Internas Brancas) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .main-container {
        background-color: white;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }

    /* Labels e Textos Internos */
    label p, .stMarkdown p { color: #0F172A !important; font-weight: 600 !important; }
    .white-text { color: white !important; text-align: center; }

    /* Comparativo (Cards Estilo Anexo 2) */
    .comp-card {
        background: #F8FAFC;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    .metric-label { color: #64748B; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; }
    .metric-value { color: #0F172A; font-size: 1.4rem; font-weight: 700; margin: 8px 0; }
    .winner-badge { 
        background: #10B981; color: white; padding: 4px 10px; border-radius: 50px; font-size: 0.65rem; font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DADOS E CATEGORIAS (Restauradas do HTML) ---
#
CATEGORIAS = {
    "Eletrônicos": {"ml": 0.14, "shopee": 0.14},
    "Moda e Acessórios": {"ml": 0.12, "shopee": 0.13},
    "Casa e Decoração": {"ml": 0.11, "shopee": 0.12},
    "Esportes e Fitness": {"ml": 0.12, "shopee": 0.13},
    "Beleza e Cuidados": {"ml": 0.13, "shopee": 0.14},
    "Livros e Mídia": {"ml": 0.09, "shopee": 0.10},
    "Brinquedos e Jogos": {"ml": 0.13, "shopee": 0.13},
    "Outros": {"ml": 0.12, "shopee": 0.14}
}

if 'db' not in st.session_state:
    st.session_state.db = []

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete):
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0.0, 0.0, 0.0
    preco_base = (custo + taxa_fixa + frete) / denominador
    preco_final = math.ceil(preco_base) - 0.10 #
    taxas = (preco_final * comissao) + taxa_fixa
    lucro = preco_final - custo - (preco_final * (imposto/100)) - taxas - frete
    return preco_final, lucro, (lucro / preco_final * 100), taxas

# --- INTERFACE PRINCIPAL ---
st.markdown("<h1 class='white-text'>💰 Calculadora de Precificação</h1>", unsafe_allow_html=True)

# 1. CARD DE ENTRADA (Anexo 1)
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        nome = st.text_input("📦 Nome do Produto", placeholder="Ex: Smartwatch")
        cat = st.selectbox("📂 Categoria", list(CATEGORIAS.keys()))
    with c2:
        custo = st.number_input("💵 Custo (R$)", min_value=0.0, value=12.0)
        imposto = st.number_input("🧾 Imposto (%)", value=6.0)
    with c3:
        markup = st.number_input("📈 Margem Alvo (%)", value=30.0)
        frete = st.number_input("🚚 Frete Grátis (R$)", value=0.0)
    
    st.divider()
    
    col_ml, col_sh = st.columns(2)
    with col_ml:
        tipo_ml = st.radio("Mercado Livre", ["Clássico", "Premium"], horizontal=True)
        ml_fs = st.checkbox("Oferecer Frete Grátis ML")
    with col_sh:
        shopee_fs = st.checkbox("Participa do Frete Grátis Shopee (20%)")

    if st.button("CALCULAR E ADICIONAR À LISTA", use_container_width=True):
        # Lógica de cálculo
        com_ml = CATEGORIAS[cat]["ml"] + (0.04 if tipo_ml == "Premium" else 0.0)
        p_ml, l_ml, m_ml, t_ml = calcular_venda(custo, markup, imposto, com_ml, 6.25 if custo < 79 else 0, frete if ml_fs else 0)
        
        com_sh = 0.20 if shopee_fs else 0.14
        p_sh, l_sh, m_sh, t_sh = calcular_venda(custo, markup, imposto, com_sh, 4.0, frete if shopee_fs else 0)
        
        st.session_state.db.append({
            "Produto": nome, "Custo": custo, "Margem Alvo": markup,
            "Preço ML": p_ml, "Lucro ML": l_ml, "Margem ML": m_ml, "Taxas ML": t_ml,
            "Preço Shopee": p_sh, "Lucro Shopee": l_sh, "Margem Shopee": m_sh, "Taxas Shopee": t_sh
        })
    st.markdown('</div>', unsafe_allow_html=True)

# 2. TABELA DE HISTÓRICO (AGORA É O SELETOR)
if st.session_state.db:
    st.markdown("<h3 class='white-text'>📋 Selecione um produto abaixo para comparar:</h3>", unsafe_allow_html=True)
    df = pd.DataFrame(st.session_state.db)
    
    # Criamos a tabela interativa que permite seleção de linha
    event = st.dataframe(
        df[["Produto", "Custo", "Preço ML", "Lucro ML", "Preço Shopee", "Lucro Shopee"]],
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Lógica para pegar o índice selecionado ou o último por padrão
    selecionado = event.selection.rows[0] if event.selection.rows else len(st.session_state.db) - 1
    p = st.session_state.db[selecionado]

    # 3. COMPARATIVO DINÂMICO (Anexo 2)
    st.markdown(f"<h2 class='white-text'>📊 Comparando: {p['Produto']}</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        comp1, comp2, comp3, comp4 = st.columns(4)
        
        with comp1:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Melhor Margem</div>
                <div class="metric-value">{max(p['Margem ML'], p['Margem Shopee']):.1f}%</div>
                <div class="winner-badge">{'MERCADO LIVRE' if p['Margem ML'] > p['Margem Shopee'] else 'SHOPEE'}</div>
            </div>""", unsafe_allow_html=True)
        with comp2:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Maior Lucro</div>
                <div class="metric-value">R$ {max(p['Lucro ML'], p['Lucro Shopee']):.2f}</div>
                <div class="winner-badge">{'MERCADO LIVRE' if p['Lucro ML'] > p['Lucro Shopee'] else 'SHOPEE'}</div>
            </div>""", unsafe_allow_html=True)
        with comp3:
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Menor Taxa Total</div>
                <div class="metric-value">R$ {min(p['Taxas ML'], p['Taxas Shopee']):.2f}</div>
                <div class="winner-badge">{'SHOPEE' if p['Taxas Shopee'] < p['Taxas ML'] else 'MERCADO LIVRE'}</div>
            </div>""", unsafe_allow_html=True)
        with comp4:
            # Recomendação baseada no score do seu HTML
            ml_score = (1 if p['Margem ML'] > p['Margem Shopee'] else 0) + (1 if p['Lucro ML'] > p['Lucro Shopee'] else 0)
            rec = "Mercado Livre" if ml_score >= 1 else "Shopee"
            st.markdown(f"""<div class="comp-card">
                <div class="metric-label">Recomendação</div>
                <div class="metric-value" style="font-size: 1.1rem">{rec}</div>
                <div class="winner-badge" style="background:#667eea">MELHOR OPÇÃO</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# 4. PAINEL DE TAXAS (Sidebar)
with st.sidebar:
    st.markdown("### 📊 Taxas de Comissão")
    taxas_data = []
    for k, v in CATEGORIAS.items():
        taxas_data.append({"Categoria": k, "ML (%)": f"{v['ml']*100:.0f}%", "SHP (%)": f"{v['shopee']*100:.0f}%"})
    st.table(pd.DataFrame(taxas_data))
    if st.button("🗑️ Limpar Histórico"):
        st.session_state.db = []
        st.rerun()
