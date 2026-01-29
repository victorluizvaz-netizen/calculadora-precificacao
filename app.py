import streamlit as st
import pandas as pd
import math
import base64

# --- CONFIGURAÇÃO E CSS (Mantendo seu estilo fiel) ---
st.set_page_config(page_title="Precificador Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; font-family: 'Outfit', sans-serif !important; }
    .main-container { background-color: white; border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    label p, .stMarkdown p { color: #0F172A !important; font-weight: 600 !important; }
    .white-text { color: white !important; text-align: center; }
    .comp-card { background: #F8FAFC; border-radius: 16px; padding: 15px; text-align: center; border: 1px solid #E2E8F0; height: 100%; }
    .metric-label { color: #64748B; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; }
    .metric-value { color: #0F172A; font-size: 1.4rem; font-weight: 700; margin: 8px 0; }
    .winner-badge { background: #10B981; color: white; padding: 4px 10px; border-radius: 50px; font-size: 0.65rem; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE EXPORTAÇÃO VISUAL (HTML/PDF Style) ---
def gerar_relatorio_html(df):
    linhas = ""
    for _, row in df.iterrows():
        linhas += f"""
        <tr>
            <td style="padding:12px; border-bottom:1px solid #eee;">{row['Produto']}</td>
            <td style="padding:12px; border-bottom:1px solid #eee;">R$ {row['Preço ML']:.2f}</td>
            <td style="padding:12px; border-bottom:1px solid #eee; color:#10B981; font-weight:bold;">R$ {row['Lucro ML']:.2f}</td>
            <td style="padding:12px; border-bottom:1px solid #eee;">R$ {row['Preço Shopee']:.2f}</td>
            <td style="padding:12px; border-bottom:1px solid #eee; color:#10B981; font-weight:bold;">R$ {row['Lucro Shopee']:.2f}</td>
        </tr>
        """
    
    html = f"""
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: sans-serif; color: #333; padding: 40px;">
        <div style="max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
            <h2 style="color: #667eea; text-align: center;">Relatório de Precificação Pro</h2>
            <p style="text-align: center; color: #666;">Documento gerado em tempo real para análise de Marketplaces</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background: #f4f4f4;">
                        <th style="padding:12px; text-align:left;">Produto</th>
                        <th style="padding:12px; text-align:left;">Preço ML</th>
                        <th style="padding:12px; text-align:left;">Lucro ML</th>
                        <th style="padding:12px; text-align:left;">Preço SHP</th>
                        <th style="padding:12px; text-align:left;">Lucro SHP</th>
                    </tr>
                </thead>
                <tbody>{linhas}</tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html

# --- LÓGICA DE NEGÓCIO ---
CATEGORIAS = {
    "Eletrônicos": {"ml": 0.14, "shopee": 0.14},
    "Moda e Acessórios": {"ml": 0.12, "shopee": 0.13},
    "Casa e Decoração": {"ml": 0.11, "shopee": 0.12},
    "Esportes e Fitness": {"ml": 0.12, "shopee": 0.13},
    "Beleza e Cuidados": {"ml": 0.13, "shopee": 0.14},
    "Outros": {"ml": 0.12, "shopee": 0.14}
}

if 'db' not in st.session_state: st.session_state.db = []

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete):
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0.0, 0.0, 0.0, 0.0
    preco_base = (custo + taxa_fixa + frete) / denominador
    preco_final = math.ceil(preco_base) - 0.10
    taxas = (preco_final * comissao) + taxa_fixa
    lucro = preco_final - custo - (preco_final * (imposto/100)) - taxas - frete
    return preco_final, lucro, (lucro/preco_final*100), taxas

# --- UI ---
st.markdown("<h1 class='white-text'>💰 Precificador Pro</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        nome = st.text_input("📦 Nome do Produto")
        cat = st.selectbox("📂 Categoria", list(CATEGORIAS.keys()))
    with c2:
        custo = st.number_input("💵 Custo (R$)", value=50.0)
        imposto = st.number_input("🧾 Imposto (%)", value=6.0)
    with c3:
        markup = st.number_input("📈 Margem Alvo (%)", value=20.0)
        frete = st.number_input("🚚 Frete (R$)", value=0.0)
    
    if st.button("CALCULAR E ADICIONAR", use_container_width=True):
        com_ml = CATEGORIAS[cat]["ml"]; fixa_ml = 6.25 if custo < 79 else 0
        p_ml, l_ml, m_ml, t_ml = calcular_venda(custo, markup, imposto, com_ml, fixa_ml, 0)
        p_sh, l_sh, m_sh, t_sh = calcular_venda(custo, markup, imposto, 0.14, 4.0, 0)
        st.session_state.db.append({"Produto": nome, "Custo": custo, "Preço ML": p_ml, "Lucro ML": l_ml, "Margem ML": m_ml, "Taxas ML": t_ml, "Preço Shopee": p_sh, "Lucro Shopee": l_sh, "Margem Shopee": m_sh, "Taxas Shopee": t_sh})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.db:
    df = pd.DataFrame(st.session_state.db)
    
    # Grid Interativo para Seleção
    st.markdown("<h3 class='white-text'>📋 Lista de Produtos (Selecione para comparar)</h3>", unsafe_allow_html=True)
    event = st.dataframe(df[["Produto", "Preço ML", "Lucro ML", "Preço Shopee", "Lucro Shopee"]], use_container_width=True, on_select="rerun", selection_mode="single-row")
    
    # Comparativo Dinâmico
    idx = event.selection.rows[0] if event.selection.rows else len(st.session_state.db) - 1
    p = st.session_state.db[idx]
    
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#0F172A; text-align:center;'>Análise: {p['Produto']}</h3>", unsafe_allow_html=True)
        comp1, comp2, comp3 = st.columns(3)
        comp1.markdown(f'<div class="comp-card"><div class="metric-label">Maior Lucro</div><div class="metric-value">R$ {max(p["Lucro ML"], p["Lucro Shopee"]):.2f}</div><div class="winner-badge">{"ML" if p["Lucro ML"] > p["Lucro Shopee"] else "SHP"}</div></div>', unsafe_allow_html=True)
        comp2.markdown(f'<div class="comp-card"><div class="metric-label">Preço Sugerido ML</div><div class="metric-value">R$ {p["Preço ML"]:.2f}</div></div>', unsafe_allow_html=True)
        comp3.markdown(f'<div class="comp-card"><div class="metric-label">Preço Sugerido SHP</div><div class="metric-value">R$ {p["Preço Shopee"]:.2f}</div></div>', unsafe_allow_html=True)
        
        # BOTÃO DE EXPORTAÇÃO BONITO
        st.divider()
        html_report = gerar_relatorio_html(df)
        st.download_button(
            label="📥 EXPORTAR RELATÓRIO VISUAL (HTML)",
            data=html_report,
            file_name=f"relatorio_precificacao.html",
            mime="text/html",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
