import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DE CATEGORIAS E TAXAS ---
# Valores baseados nas médias gerais (ajuste conforme sua realidade específica)
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
    # O denominador não pode ser zero ou negativo (Soma das % deve ser < 100)
    perc_total_deducoes = (imposto / 100) + comissao + (markup / 100)
    
    if perc_total_deducoes >= 1:
        return 0.0, 0.0 # Retorna zero em vez de erro/branco

    preco = (custo + frete + taxa_fixa) / (1 - perc_total_deducoes)
    
    # Regra de Teto Shopee
    if teto and (preco * comissao) > teto:
        preco = (custo + frete + taxa_fixa + teto) / (1 - (imposto / 100) - (markup / 100))
    
    comissao_valor = min(preco * comissao, teto) if teto else (preco * comissao)
    lucro = preco - custo - (preco * (imposto/100)) - comissao_valor - taxa_fixa - frete
    return round(preco, 2), round(lucro, 2)

st.set_page_config(page_title="Gestão de Precificação", layout="wide")
st.title("🚀 Precificador Pro: Gestão de Portfólio")

# --- NOVO: VISUALIZAÇÃO DE TAXAS POR CATEGORIA ---
with st.sidebar:
    st.header("📊 Tabela de Taxas")
    st.write("Confira as comissões aplicadas:")
    df_taxas = pd.DataFrame.from_dict(CATEGORIAS_DATA, orient='index')
    df_taxas.columns = ['ML Clássico', 'ML Premium', 'Shopee Base']
    # Formata como porcentagem para visualização
    st.dataframe(df_taxas.style.format("{:.1%}"))
    st.info("Nota: Shopee + Frete Grátis adiciona 6% às taxas acima.")

# --- ÁREA DE ENTRADA ---
with st.expander("➕ Adicionar Novo Produto", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nome = st.text_input("Nome do Produto", placeholder="Ex: Teclado Mecânico")
        categoria = st.selectbox("Categoria do Produto", list(CATEGORIAS_DATA.keys()))
        custo = st.number_input("Custo de Aquisição (R$)", min_value=0.0, value=50.0)
    with col2:
        markup = st.slider("Margem de Lucro Desejada %", 1, 50, 15)
        imposto = st.number_input("Imposto (%)", value=4.0)
        frete = st.number_input("Custo de Frete (R$)", value=0.0)
    with col3:
        st.write("**Configurações de Canal:**")
        anuncio_ml = st.radio("ML: Tipo de Anúncio", ["Clássico", "Premium"])
        frete_shopee = st.checkbox("Participa do Frete Grátis Shopee?")

    if st.button("Calcular e Adicionar à Lista"):
        if custo <= 0 or nome == "":
            st.error("Preencha o nome e o custo do produto.")
        else:
            # Lógica ML
            taxa_ml = CATEGORIAS_DATA[categoria]["ml_classico" if anuncio_ml == "Clássico" else "ml_premium"]
            fixa_ml = 6.75 if (custo + frete) < 79 else 0
            p_ml, l_ml = calcular_venda(custo, markup, imposto, taxa_ml, fixa_ml, frete)

            # Lógica Shopee
            taxa_shopee = 0.20 if frete_shopee else 0.14
            p_shopee, l_shopee = calcular_venda(custo, markup, imposto, taxa_shopee, 4.0, frete, teto=103.0)

            if p_ml == 0 or p_shopee == 0:
                st.warning("⚠️ Erro: As taxas + lucro desejado somam 100% ou mais. Reduza a margem ou o imposto.")
            else:
                st.session_state.lista_produtos.append({
                    "Produto": nome,
                    "Categoria": categoria,
                    "Custo": custo,
                    "Preço ML": p_ml,
                    "Lucro ML": l_ml,
                    "Preço Shopee": p_shopee,
                    "Lucro Shopee": l_shopee,
                    "Vantagem": "Mercado Livre" if l_ml > l_shopee else "Shopee"
                })
                st.rerun()

# --- GRID VISUAL ---
st.subheader("📋 Grid de Precificação Ativa")
if st.session_state.lista_produtos:
    df_grid = pd.DataFrame(st.session_state.lista_produtos)
    
    # Formatação para destacar o lucro
    st.dataframe(
        df_grid.style.highlight_max(axis=1, subset=['Lucro ML', 'Lucro Shopee'], color='#b7e4c7'),
        use_container_width=True
    )

    # --- EXPORTAÇÃO ---
    st.divider()
    col_exp1, col_exp2 = st.columns(2)
    
    csv = df_grid.to_csv(index=False).encode('utf-8-sig') # utf-8-sig para abrir direto no Excel
    col_exp1.download_button(
        label="📥 Exportar para Excel/CSV",
        data=csv,
        file_name='meus_precos.csv',
        mime='text/csv',
    )
    
    if col_exp2.button("🗑️ Limpar Tudo"):
        st.session_state.lista_produtos = []
        st.rerun()
else:
    st.info("Nenhum produto na lista. Utilize o formulário acima para calcular.")
