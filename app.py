import streamlit as st
import pandas as pd

# --- CONFIGURAÇÕES DE TAXAS (Fácil Atualização) ---
CONFIG_TAXAS = {
    "Mercado Livre": {
        "Clássico": {"comissao": 0.12, "taxa_fixa": 6.75, "limite_taxa_fixa": 79.0},
        "Premium": {"comissao": 0.17, "taxa_fixa": 6.75, "limite_taxa_fixa": 79.0},
    },
    "Shopee": {
        "Padrao": {"comissao": 0.14, "taxa_fixa": 4.0, "teto_comissao": 100.0},
        "Frete Gratis": {"comissao": 0.20, "taxa_fixa": 4.0, "teto_comissao": 105.0},
    }
}

# --- FUNÇÕES DE CÁLCULO ---
def calcular_preco(custo_prod, markup, imposto, comissao_perc, taxa_fixa, frete, teto_comissao=None):
    """
    Calcula o preço de venda baseado na margem desejada sobre o faturamento (Margem Ebitda).
    Fórmula: Preço = (Custo + Frete + Taxa Fixa) / (1 - %Imposto - %Comissão - %Margem)
    """
    denominador = 1 - (imposto / 100) - comissao_perc - (markup / 100)
    
    if denominador <= 0:
        return 0, 0, 0

    preco_estimado = (custo_prod + frete + taxa_fixa) / denominador
    
    # Validação de Teto de Comissão (Shopee)
    comissao_valor = preco_estimado * comissao_perc
    if teto_comissao and comissao_valor > teto_comissao:
        # Se atingiu o teto, a comissão vira um custo fixo
        preco_estimado = (custo_prod + frete + taxa_fixa + teto_comissao) / (1 - (imposto / 100) - (markup / 100))
        comissao_valor = teto_comissao

    imposto_valor = preco_estimado * (imposto / 100)
    lucro_valor = preco_estimado - custo_prod - imposto_valor - comissao_valor - taxa_fixa - frete
    
    return round(preco_estimado, 2), round(lucro_valor, 2), round(comissao_valor + taxa_fixa, 2)

# --- INTERFACE ---
st.set_page_config(page_title="Calculadora de Preço E-commerce", layout="wide")
st.title("📊 Precificador Inteligente: ML vs Shopee")

with st.sidebar:
    st.header("1. Custos e Impostos")
    custo_aquisicao = st.number_input("Custo do Produto (R$)", min_value=0.0, value=50.0)
    markup_desejado = st.slider("Margem de Lucro Desejada (%)", 5, 50, 15)
    
    regime = st.selectbox("Regime Tributário", ["Simples Nacional", "Lucro Presumido", "MEI"])
    imposto_padrao = 4.0 if regime == "Simples Nacional" else 0.0
    aliquota_imposto = st.number_input("Alíquota de Imposto (%)", value=imposto_padrao)

    st.header("2. Logística")
    oferece_frete_gratis = st.toggle("Oferecer Frete Grátis?")
    custo_frete = 0.0
    if oferece_frete_gratis:
        custo_frete = st.number_input("Custo do Frete para você (R$)", value=20.0)

# --- CÁLCULOS POR PLATAFORMA ---
col1, col2 = st.columns(2)

# MERCADO LIVRE
with col1:
    st.subheader("📦 Mercado Livre")
    tipo_anuncio = st.selectbox("Tipo de Anúncio", ["Clássico", "Premium"])
    config_ml = CONFIG_TAXAS["Mercado Livre"][tipo_anuncio]
    
    # Regra: ML remove taxa fixa se preço > R$ 79
    # Fazemos uma pré-checagem simples
    taxa_fixa_ml = config_ml["taxa_fixa"] if (custo_aquisicao + custo_frete) < 79 else 0
    
    preco_ml, lucro_ml, taxas_ml = calcular_preco(
        custo_aquisicao, markup_desejado, aliquota_imposto, 
        config_ml["comissao"], taxa_fixa_ml, custo_frete
    )
    
    st.metric("Preço Sugerido", f"R$ {preco_ml}")
    st.write(f"**Lucro Líquido:** R$ {lucro_ml}")
    st.caption(f"Taxas ML: R$ {taxas_ml} | Imposto: {aliquota_imposto}%")
    if taxas_ml / preco_ml > 0.20:
        st.warning("⚠️ Alerta: Taxas corroendo mais de 20% do faturamento!")

# SHOPEE
with col2:
    st.subheader("🟠 Shopee")
    programa_frete = st.selectbox("Programa de Frete", ["Padrao", "Frete Gratis"])
    config_shp = CONFIG_TAXAS["Shopee"][programa_frete]
    
    preco_shp, lucro_shp, taxas_shp = calcular_preco(
        custo_aquisicao, markup_desejado, aliquota_imposto,
        config_shp["comissao"], config_shp["taxa_fixa"], custo_frete,
        teto_comissao=config_shp["teto_comissao"]
    )
    
    st.metric("Preço Sugerido", f"R$ {preco_shp}")
    st.write(f"**Lucro Líquido:** R$ {lucro_shp}")
    st.caption(f"Taxas Shopee: R$ {taxas_shp} | Imposto: {aliquota_imposto}%")

# --- COMPARATIVO ---
st.divider()
st.subheader("📈 Comparativo de Resultados")
dados_comp = {
    "Plataforma": ["Mercado Livre", "Shopee"],
    "Preço Sugerido (R$)": [preco_ml, preco_shp],
    "Lucro em R$": [lucro_ml, lucro_shp],
    "Margem Real (%)": [round((lucro_ml/preco_ml)*100,2), round((lucro_shp/preco_shp)*100,2)]
}
st.table(pd.DataFrame(dados_comp))