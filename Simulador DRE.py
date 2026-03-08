import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE DESIGN ---
st.set_page_config(page_title="CFO Hub | Inteligência Financeira", layout="wide")

st.markdown("""
    <style>
    .stMetric { border-radius: 12px; background-color: white; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #f0f2f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f9fa; border-radius: 4px 4px 0px 0px; gap: 1px; padding-left: 20px; padding-right: 20px; }
    .stTabs [aria-selected="true"] { background-color: #ffffff; border-bottom: 2px solid #27ae60; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ESTRUTURA DE CATEGORIAS ---
ESTRUTURA = {
    "Pessoal": ["Folha CLT", "Folha PJ", "Outras Pessoal", "Bonus/Dividendos"],
    "Administrativas": ["Aluguel", "Condomínio e IPTU", "Conselho", "Materiais e Limpeza", "Vagas Garagem sócios", "Viagem e Hospedagem", "Manutenções", "Desp. De representação", "Outras adm"],
    "Serv. Terceiro": ["Contabilidade/Juridico", "Tecnologia", "Outros"],
    "Marketing": ["Eventos", "Marketing", "Patrocínio"],
    "Outras": ["Ativo Fixo", "Financeiras", "Parcelamentos", "Impostos"]
}

tab_simulador, tab_didatica = st.tabs(["📊 **Simulador Estratégico**", "📚 **Manual de Instruções**"])

# =====================================================
# ABA 1: SIMULADOR (OPERAÇÃO)
# =====================================================
with tab_simulador:
    st.sidebar.header("📥 Configuração de Receitas")
    venda_mensal = st.sidebar.number_input("Novas Vendas Mensais (R$)", value=10000.0, step=1000.0)
    n_parcelas = st.sidebar.slider("Prazo Médio de Recebimento (Meses)", 1, 12, 4)
    crescimento = st.sidebar.slider("Crescimento Mensal (%)", 0, 20, 5) / 100

    st.sidebar.divider()
    st.sidebar.header("📤 Planejamento de Saídas")
    gastos_por_cat = {}
    for cat, subs in ESTRUTURA.items():
        with st.sidebar.expander(f"📂 {cat}"):
            soma = 0
            for s in subs:
                v = st.number_input(f"{s} (R$)", value=0.0, key=f"v_{cat}_{s}")
                soma += v
            gastos_por_cat[cat] = soma

    # Lógica de Cálculo
    datas = pd.date_range(start="2026-03-01", end="2026-06-30", freq="MS")
    rec_mes = {d.strftime("%m/%Y"): 0.0 for d in datas}

    for i, data_venda in enumerate(datas):
        valor_venda = venda_mensal * ((1 + crescimento) ** i)
        valor_p = valor_venda / n_parcelas
        for p in range(n_parcelas):
            m_p = data_venda + pd.DateOffset(months=p)
            m_k = m_p.strftime("%m/%Y")
            if m_k in rec_mes: rec_mes[m_k] += valor_p

    dados_dre = []
    for m in rec_mes.keys():
        linha = {"Mês": m, "(+) RECEITA (CAIXA)": rec_mes[m]}
        t_s = 0
        for cat, val in gastos_por_cat.items():
            linha[f"(-) {cat}"] = -val
            t_s += val
        linha["(=) RESULTADO LÍQUIDO"] = rec_mes[m] - t_s
        dados_dre.append(linha)

    df_dre = pd.DataFrame(dados_dre).set_index("Mês").T

    # --- MÉTRICAS COM CORES DINÂMICAS ---
    t_rec = df_dre.loc["(+) RECEITA (CAIXA)"].sum()
    t_luc = df_dre.loc["(=) RESULTADO LÍQUIDO"].sum()
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Receita Total Projetada", f"R$ {t_rec:,.2f}")
    
    # Cor do Saldo Final
    cor_saldo = "normal" if t_luc >= 0 else "inverse"
    col_m2.metric("Resultado Líquido Acumulado", f"R$ {t_luc:,.2f}", delta=f"{((t_luc/t_rec)*100 if t_rec > 0 else 0):.1f}% (Margem)", delta_color=cor_saldo)
    col_m3.metric("Ponto de Equilíbrio (Média)", f"R$ {abs(t_rec - t_luc)/len(datas):,.2f}/mês")

    st.divider()
    
    # --- TABELA DRE COM FORMATAÇÃO CONDICIONAL ---
    st.subheader("📑 Demonstrativo de Resultado (DRE)")
    
    def color_negative_red(val):
        if isinstance(val, (int, float)):
            color = '#e74c3c' if val < 0 else '#27ae60'
            return f'color: {color}'
        return ''

    st.dataframe(
        df_dre.style.format("R$ {:,.2f}")
        .applymap(color_negative_red)
        .highlight_max(axis=1, subset=pd.IndexSlice[["(+) RECEITA (CAIXA)"], :], color="#f0fdf4")
        , use_container_width=True
    )

# =====================================================
# ABA 2: MANUAL DIDÁTICO (PERFEIÇÃO VISUAL)
# =====================================================
with tab_didatica:
    st.title("📚 Guia de Utilização do Sistema")
    st.write("Entenda os conceitos financeiros aplicados neste simulador para uma gestão de alta performance.")
    
    st.markdown("---")

    # --- CARD: EXEMPLO PRÁTICO ---
    st.subheader("🎯 O Efeito Escada no Fluxo de Caixa")
    st.success("""
    **Exemplo Prático de Parcelamento:** Imagine que você realizou uma venda de **R$ 10.000,00** em Março, parcelada em **4 vezes**. No regime de caixa, esse valor não entra integralmente de uma só vez:
    
    * **Março:** R$ 2.500,00  
    * **Abril:** R$ 2.500,00 (da venda de Março) + parcela da venda de Abril  
    * **Maio:** R$ 2.500,00 (da venda de Março) + parcelas das vendas anteriores...
    
    O gráfico de evolução mostrará o faturamento subindo em **'degraus'** a cada mês. Esse crescimento gradual ocorre até que o sistema atinja o **platô**, momento em que o volume de parcelas antigas se estabiliza com as novas.
    """)
    

    # --- SEÇÃO DE CONCEITOS ---
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.info("### 📋 Regime de Caixa\nÉ o registro dos eventos financeiros no momento em que o dinheiro **entra ou sai** efetivamente da conta bancária. É a visão real da sobrevivência financeira da empresa.")
    
    with col_c2:
        st.warning("### 📈 Margem Líquida\nIndica qual porcentagem de cada real vendido restou após o pagamento de todas as despesas. É o principal indicador de eficiência operacional.")

    # --- DETALHAMENTO DE CATEGORIAS ---
    st.markdown("### 🗂️ Estrutura de Contas")
    with st.expander("💼 **Gestão de Pessoal**"):
        st.write("Engloba todos os custos diretos e indiretos com a equipe, incluindo salários CLT, contratos PJ, premiações e a distribuição de dividendos aos sócios.")

    with st.expander("🏠 **Despesas Administrativas**"):
        st.write("Custos fixos necessários para manter a estrutura física e jurídica, como aluguéis, taxas de conselho, softwares de gestão e manutenções preventivas.")

    with st.expander("📣 **Marketing e Crescimento**"):
        st.write("Investimentos destinados à aquisição de novos clientes, patrocínios de eventos e campanhas digitais.")

st.markdown('<div style="text-align: center; color: #bdc3c7; padding: 20px;">CFO Hub Intelligence © 2026 | Desenvolvido para Alta Performance</div>', unsafe_allow_html=True)