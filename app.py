import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DE CATEGORIAS E TAXAS ---
# Aqui você pode adicionar as categorias reais de cada marketplace
CATEGORIAS_DATA = {
    "Eletrônicos": {"ml_classico": 0.12, "ml_premium": 0.17, "shopee_base": 0.14},
    "Acessórios Automotivos": {"ml_classico": 0.14, "ml_premium": 0.19, "shopee_base": 0.14},
    "Casa e Decoração": {"ml_classico": 0.11, "ml_premium": 0.16, "shopee_base": 0.14},
    "Moda/Vestuário": {"ml_classico": 0.15, "ml_premium": 0.20, "shopee_base": 0.14},
    "Outros": {"ml_classico": 0.13, "ml_premium": 0.18, "shopee_base": 0.14},
}

# Inicializa o "Banco de Dados" na sessão do usuário
if 'lista_produtos' not in st.session_state:
    st.session_state.lista_produtos = []

def calcular_venda(custo, markup, imposto, comissao, taxa_fixa, frete, teto=None):
    denominador = 1 - (imposto / 100) - comissao - (markup / 100)
    if denominador <= 0: return 0, 0
    preco = (custo + frete + taxa_fixa) / denominador
    
    # Regra de Teto Shopee
    if teto and (preco * comissao) > teto:
        preco = (custo + frete + taxa_fixa + teto) / (1 - (imposto / 100) - (markup / 100))
    
    lucro = preco - custo - (preco * (imposto/100)) - (preco * comissao) - taxa_fixa - frete
    return round(preco, 2), round(lucro, 2)

st.title("🚀 Precificador Pro: Gestão de Portfólio")

# --- ÁREA DE ENTRADA ---
with st.expander("➕ Adicionar Novo Produto", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nome = st.text_input("Nome do Produto", placeholder="Ex: Teclado Mecânico")
        categoria = st.selectbox("Categoria do Produto", list(CATEGORIAS_DATA.keys()))
        custo = st.number_input("Custo de Aquisição (R$)", min_value=0.01, value=50.0)
    with col2:
        markup = st.slider("Margem de Lucro Alvo %", 5, 50, 15)
        imposto = st.number_input("Imposto (%)", value=4.0)
        frete = st.number_input("Custo de Frete (R$)", value=0.0)
    with col3:
        st.write("**Simular para:**")
        anuncio_ml = st.radio("ML: Tipo de Anúncio", ["Clássico", "Premium"])
        frete_shopee = st.checkbox("Participa do Frete Grátis Shopee? (+6%)")

    if st.button("Calcular e Adicionar à Lista"):
        # Lógica ML
        taxa_ml = CATEGORIAS_DATA[categoria]["ml_classico" if anuncio_ml == "Clássico" else "ml_premium"]
        fixa_ml = 6.75 if (custo + frete) < 79 else 0
        p_ml, l_ml = calcular_venda(custo, markup, imposto, taxa_ml, fixa_ml, frete)

        # Lógica Shopee
        taxa_shopee = 0.20 if frete_shopee else 0.14
        p_shopee, l_shopee = calcular_venda(custo, markup, imposto, taxa_shopee, 4.0, frete, teto=103.0)

        # Salva no estado da sessão
        st.session_state.lista_produtos.append({
            "Produto": nome,
            "Categoria": categoria,
            "Custo": custo,
            "Preço ML": p_ml,
            "Lucro ML": l_ml,
            "Preço Shopee": p_shopee,
            "Lucro Shopee": l_shopee,
            "Melhor Canal": "Mercado Livre" if l_ml > l_shopee else "Shopee"
        })
        st.success(f"Produto {nome} adicionado!")

# --- GRID VISUAL ---
st.subheader("📋 Grid de Precificação")
if st.session_state.lista_produtos:
    df = pd.DataFrame(st.session_state.lista_produtos)
    
    # Exibe a tabela com formatação
    st.dataframe(df.style.highlight_max(axis=1, subset=['Lucro ML', 'Lucro Shopee'], color='#d4edda'), use_container_width=True)

    # --- EXPORTAÇÃO ---
    st.divider()
    col_exp1, col_exp2 = st.columns(2)
    
    csv = df.to_csv(index=False).encode('utf-8')
    col_exp1.download_button(
        label="📥 Baixar Planilha (CSV)",
        data=csv,
        file_name='precificacao_produtos.csv',
        mime='text/csv',
    )
    
    if col_exp2.button("Limpar Lista"):
        st.session_state.lista_produtos = []
        st.rerun()
else:
    st.info("Sua lista está vazia. Adicione um produto acima para começar.")
