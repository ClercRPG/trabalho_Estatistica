import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Dashboard do Trabalho", layout="wide")

st.title("📊 Dashboard de Análise de Vendas")
st.write("Resumo visual dos tópicos 1 a 5 do trabalho.")

# =========================
# CARREGAR BASE
# =========================
arquivo = "Trabalho Análise Exploratória (1).xlsx"
aba = "Trabalho_Banco de Dados"

try:
    df = pd.read_excel(arquivo, sheet_name=aba)
except Exception as e:
    st.error("Erro ao abrir a planilha.")
    st.write(e)
    st.stop()

df.columns = df.columns.str.strip()

# Criar Total_Sale
df["Total_Sale"] = df["Quantity"] * df["UnitPrice"]

st.success("Base carregada com sucesso!")

# =========================
# TÓPICO 1
# =========================
st.header("1. Criação da variável Total_Sale")
st.code("Total_Sale = Quantity × UnitPrice")

col1, col2, col3 = st.columns(3)
col1.metric("Faturamento total", f"{df['Total_Sale'].sum():,.2f}")
col2.metric("Total de registros", len(df))
col3.metric("Transações únicas", df["InvoiceNo"].nunique())

st.divider()

# =========================
# TÓPICO 2
# =========================
st.header("2. Tabelas de Frequência")

colA, colB = st.columns(2)

with colA:
    st.subheader("2.1 Frequência por Continente")
    freq_cont = df["Continent"].value_counts().reset_index()
    freq_cont.columns = ["Continent", "Frequência Absoluta"]
    freq_cont["Frequência Relativa (%)"] = (
        freq_cont["Frequência Absoluta"] / freq_cont["Frequência Absoluta"].sum() * 100
    )
    st.dataframe(freq_cont, use_container_width=True)

with colB:
    st.subheader("2.2 Frequência por Categoria")
    freq_cat = df["Product_Category"].value_counts().reset_index()
    freq_cat.columns = ["Product_Category", "Frequência Absoluta"]
    freq_cat["Frequência Relativa (%)"] = (
        freq_cat["Frequência Absoluta"] / freq_cat["Frequência Absoluta"].sum() * 100
    )
    st.dataframe(freq_cat, use_container_width=True)

st.subheader("2.3 Vendas por mês")
vendas_mes_tabela = df.groupby("Month")["Total_Sale"].sum().reset_index()
st.dataframe(vendas_mes_tabela, use_container_width=True)

st.subheader("2.4 Top 10 países por número de transações")
top10_trans = df["Country"].value_counts().head(10).reset_index()
top10_trans.columns = ["Country", "Número de Transações"]
st.dataframe(top10_trans, use_container_width=True)

st.divider()

# =========================
# TÓPICO 3
# =========================
st.header("3. Tabelas Cruzadas")

st.subheader("3.1 Product_Category × Continent")
st.dataframe(pd.crosstab(df["Product_Category"], df["Continent"]), use_container_width=True)

st.subheader("3.2 Continent × Month")
st.dataframe(pd.crosstab(df["Continent"], df["Month"]), use_container_width=True)

st.subheader("3.3 Product_Category × Month")
st.dataframe(pd.crosstab(df["Product_Category"], df["Month"]), use_container_width=True)

st.divider()

# =========================
# TÓPICO 4
# =========================
st.header("4. Medidas Descritivas")

def medidas(coluna):
    coluna = pd.to_numeric(coluna, errors="coerce").dropna()
    moda = coluna.mode()

    return pd.Series({
        "Média": coluna.mean(),
        "Mediana": coluna.median(),
        "Moda": moda.iloc[0] if len(moda) > 0 else "Amodal",
        "Mínimo": coluna.min(),
        "Máximo": coluna.max(),
        "Amplitude": coluna.max() - coluna.min(),
        "Variância": coluna.var(),
        "Desvio padrão": coluna.std(),
        "Coeficiente de variação": coluna.std() / coluna.mean(),
        "Q1": coluna.quantile(0.25),
        "Q2 / Mediana": coluna.quantile(0.50),
        "Q3": coluna.quantile(0.75),
        "IQR": coluna.quantile(0.75) - coluna.quantile(0.25)
    })

medidas_gerais = pd.DataFrame({
    "Quantity": medidas(df["Quantity"]),
    "UnitPrice": medidas(df["UnitPrice"]),
    "Total_Sale": medidas(df["Total_Sale"])
})

st.subheader("Medidas gerais")
st.dataframe(medidas_gerais, use_container_width=True)

st.subheader("Total_Sale por Continente")
st.dataframe(df.groupby("Continent")["Total_Sale"].apply(medidas).unstack(), use_container_width=True)

st.subheader("Total_Sale por Categoria")
st.dataframe(df.groupby("Product_Category")["Total_Sale"].apply(medidas).unstack(), use_container_width=True)

st.divider()

# =========================
# TÓPICO 5
# =========================
st.header("5. Gráficos")

# 5.1 Histograma
st.subheader("5.1 Histograma de Quantity")
n = len(df["Quantity"].dropna())
k = math.ceil(1 + 3.322 * math.log10(n))

fig, ax = plt.subplots(figsize=(10, 4))
ax.hist(df["Quantity"].dropna(), bins=k)
ax.set_title("Histograma de Quantity")
ax.set_xlabel("Quantity")
ax.set_ylabel("Frequência")
st.pyplot(fig)

# 5.2 Boxplot
st.subheader("5.2 Boxplot de Quantity por Product_Category")
fig, ax = plt.subplots(figsize=(12, 5))
df.boxplot(column="Quantity", by="Product_Category", ax=ax, rot=45)
ax.set_title("Boxplot de Quantity por Product_Category")
ax.set_xlabel("Product_Category")
ax.set_ylabel("Quantity")
plt.suptitle("")
st.pyplot(fig)

# 5.3 Barras Categoria
st.subheader("5.3 Volume de vendas por Product_Category")
vendas_cat = (
    df.groupby("Product_Category")["Total_Sale"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

grafico_cat = alt.Chart(vendas_cat).mark_bar().encode(
    x=alt.X("Total_Sale:Q", title="Soma de Total_Sale"),
    y=alt.Y("Product_Category:N", sort="-x", title="Categoria"),
    tooltip=["Product_Category", "Total_Sale"]
).properties(height=350)

st.altair_chart(grafico_cat, use_container_width=True)

# 5.4 Barras Continente
st.subheader("5.4 Volume total de vendas por Continent")
vendas_cont = (
    df.groupby("Continent")["Total_Sale"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

grafico_cont = alt.Chart(vendas_cont).mark_bar().encode(
    x=alt.X("Total_Sale:Q", title="Soma de Total_Sale"),
    y=alt.Y("Continent:N", sort="-x", title="Continente"),
    tooltip=["Continent", "Total_Sale"]
).properties(height=300)

st.altair_chart(grafico_cont, use_container_width=True)

# 5.5 Top 10 países
st.subheader("5.5 Top 10 países com maior faturamento")
top10 = (
    df.groupby("Country")["Total_Sale"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

grafico_top10 = alt.Chart(top10).mark_bar().encode(
    x=alt.X("Total_Sale:Q", title="Faturamento total"),
    y=alt.Y("Country:N", sort="-x", title="País"),
    tooltip=["Country", "Total_Sale"]
).properties(height=400)

st.altair_chart(grafico_top10, use_container_width=True)
st.dataframe(top10, use_container_width=True)

# 5.6 Linha por mês
st.subheader("5.6 Evolução das vendas por Month")
vendas_mes = (
    df.groupby("Month")["Total_Sale"]
    .sum()
    .sort_index()
    .reset_index()
)

grafico_mes = alt.Chart(vendas_mes).mark_line(point=True).encode(
    x=alt.X("Month:O", title="Month"),
    y=alt.Y("Total_Sale:Q", title="Total_Sale agregado"),
    tooltip=["Month", "Total_Sale"]
).properties(height=350)

st.altair_chart(grafico_mes, use_container_width=True)

# 5.7 Pizza / Setores
st.subheader("5.7 Participação percentual por Continent")
pizza = (
    df.groupby("Continent")["Total_Sale"]
    .sum()
    .reset_index()
)

grafico_pizza = alt.Chart(pizza).mark_arc().encode(
    theta=alt.Theta("Total_Sale:Q"),
    color=alt.Color("Continent:N"),
    tooltip=["Continent", "Total_Sale"]
).properties(height=400)

st.altair_chart(grafico_pizza, use_container_width=True)

st.divider()

st.header("Conclusão")
st.write(
    "A análise mostra o comportamento das vendas por categoria, continente, país e mês. "
    "Também permite observar medidas descritivas como média, mediana, variância e desvio padrão."
)