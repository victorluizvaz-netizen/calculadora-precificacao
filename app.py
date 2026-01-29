import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DE CATEGORIAS E TAXAS ---
CATEGORIAS_DATA = {
    "Eletrônicos": {"ml_classico": 0.12, "ml_premium": 0.17, "shopee_base": 0.14},
    "Acessórios Automotivos": {"ml_classico": 0.14, "ml_premium": 0.19, "shopee_base": 0.14},
    "Casa e Decoração": {"ml_classico": 0.11, "ml_premium": 0.16, "shopee_base": 0.14},
    "Moda/Vestuário": {"ml_classico": 0.15, "ml_premium": 0.20, "shopee_base": 0.14},
    "Brinquedos": {"ml_classico": 0.13, "ml_premium": 0.18, "shopee_base": 0.14},
    "Outros": {"ml_classico": 0.13, "ml_premium": 0.18, "shopee_base": 0.14},
}

if 'lista_produtos' not in st.session_state:
    st.session_state.lista_produtos = []

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete, teto=None):
    perc_total_deducoes = (imposto / 100) + comissao + (markup / 100)
    
    if perc_total_deducoes >= 1:
        return 0.0, 0.0

    preco = (custo + frete + taxa_fixa) / (1 - perc_total_deducoes)
    
    if teto and (preco * comissao) > teto:
        preco = (custo + frete + taxa_fixa + teto) / (1 - (imposto / 100) - (markup / 100))
    
    comissao_valor = min(preco * comissao, teto) if teto else (preco * comissao)
    lucro = preco - custo - (preco * (imposto/100)) - comissao_valor - taxa_fixa - frete
    return round(preco, 2), round(lucro, 2)

st.set_page_config(page_title="Gestão de Precificação", layout="wide")
st.title("🚀 Precificador Pro: Gestão de Portfólio")

# --- SIDEBAR: TABELA DE TAXAS ---
with st.sidebar:
    st.header("📊 Diferença de Taxas")
    st.write("Comissões por Categoria:")
    
    # Criando um DataFrame para exibir as taxas de forma clara
    dados_taxas = []
    for cat, taxas in CATEGORIAS_DATA.items():
        dados_taxas.append({
            "Categoria": cat,
            "ML Clássico": f"{taxas['ml_classico']:.1%}",
            "ML Premium": f"{taxas['ml_premium']:.1%}",
            "Shopee Base": f"{taxas['shopee_base']:.1%}"
        })
    
    st.table(pd.DataFrame(dados_taxas))
    st.caption("⚠️ Shopee + Frete Grátis: Adiciona 6% de taxa.")

# --- ÁREA DE ENTRADA ---
with st.expander("➕ Adicionar Novo Produto", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nome = st.text_input("Nome do Produto", placeholder="Ex: Produto X", key="input_nome")
        categoria = st.selectbox("Categoria", list(CATEGORIAS_DATA.keys()), key="input_cat")
        custo = st.number_input("Custo (R$)", min_value=0.0, value=50.0, key="input_custo")
    with col2:
        markup = st.slider("Margem Alvo %", 1, 50, 15, key="input_markup")
        imposto = st.number_input("Imposto (%)", value=4.0, key="input_imposto")
        frete = st.number_input("Frete (R$)", value=0.0, key="input_frete")
    with col3:
        st.write("**Canais:**")
        anuncio_ml = st.radio("ML Anúncio", ["Clássico", "Premium"], key="input_ml_tipo")
        frete_shopee = st.checkbox("Shopee Frete Grátis?", key="input_shp_frete")

    if st.button("➕ Calcular e Adicionar", key="btn_adicionar"):
        if custo <= 0 or nome == "":
            st.error("Preencha os campos corretamente.")
        else:
            taxa_ml = CATEGORIAS_DATA[categoria]["ml_classico" if anuncio_ml == "Clássico" else "ml_premium"]
            fixa_ml = 6.75 if (custo + frete) < 79 else 0
            p_ml, l_ml = calcular_venda(custo, markup, imposto, taxa_ml, fixa_ml, frete)

            taxa_shopee = 0.20 if frete_shopee else 0.14
            p_shopee, l_shopee = calcular_venda(custo, markup, imposto, taxa_shopee, 4.0, frete, teto=103.0)

            st.session_state.lista_produtos.append({
                "Produto": nome,
                "Categoria": categoria,
                "Custo": custo,
                "Preço ML": p_ml,
                "Lucro ML": l_ml,
                "Preço Shopee": p_shopee,
                "Lucro Shopee": l_shopee
            })
            st.rerun()

# --- GRID VISUAL ---
st.subheader("📋 Seus Produtos")
if st.session_state.lista_produtos:
    df_grid = pd.DataFrame(st.session_state.lista_produtos)
    
    # Formatação de Moeda Brasileira
    df_display = df_grid.copy()
    colunas_fin = ['Custo', 'Preço ML', 'Lucro ML', 'Preço Shopee', 'Lucro Shopee']
    for col in colunas_fin:
        df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(df_display, use_container_width=True)

    st.divider()
    c1, c2 = st.columns(2)
    
    # O segredo para evitar o erro é a 'key' única no download_button
    csv = df_grid.to_csv(index=False).encode('utf-8-sig')
    c1.download_button(
        label="📥 Exportar Lista (Excel/CSV)",
        data=csv,
        file_name='meus_precos_ecommerce.csv',
        mime='text/csv',
        key='download_csv_final'
    )
    
    if c2.button("🗑️ Limpar Tudo", key="btn_limpar_lista"):
        st.session_state.lista_produtos = []
        st.rerun()
else:
    st.info("Adicione produtos para visualizar o grid.")
