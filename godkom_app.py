# 1. Importar as dependências
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import fundamentus
import numpy as np
import warnings
from datetime import timedelta
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.grid import grid

warnings.filterwarnings("ignore")

#################################################################
st.set_page_config(
    page_title="Ðashboard ƒinanceiro", page_icon="LogoGodkom.ico", layout="wide"
)
#################################################################
### referência ao arquivo com todo script CSS

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    ##################################################################
    ## se refere aos botões dividendos, valuation...

    st.markdown(
        """
    <style>

	.stTabs [data-baseweb="tab-list"] {
		gap: 14px;
    }

	.stTabs [data-baseweb="tab"] {
		height: 42px;
        white-space: pre-wrap;
		background-color: #BBC4C4;
		border-radius: 5px 5px 5px 5px;
		gap: 1px;
		padding-top: 10px;
		padding-bottom: 10px;
    }

	.stTabs [aria-selected="true"] {
  		background-color: #FFE4B5;    
	}

</style>""",
        unsafe_allow_html=True,
    )

hide_decoration_bar_style = """
    <style>
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

#################################################################
##### criando o SIDEBAR


def build_sidebar():
    st.image("LogoGodkom.ico")
    ticker_list = pd.read_csv("tickers_ibra.csv", index_col=0)
    tickers = st.multiselect(
        label="Selecione as empresas",
        options=ticker_list,
        default=("POMO3", "UGPA3", "PETR4", "PLPL3", "PINE4", "VLID3"),
    )
    tickers = [t + ".SA" for t in tickers]

    ##### Manipulando a data com datetime
    year = timedelta(365)
    start = st.date_input("Data inicial", value=pd.to_datetime("today") - year)
    end = st.date_input("Data final", value=pd.to_datetime("today"))

    st.sidebar.link_button(
        "TradingView VXEWZ",
        type="secondary",
        use_container_width=True,
        url=("https://br.tradingview.com/chart/vLEBjw5p/"),
    )

    st.sidebar.link_button(
        "Opções .NET",
        type="secondary",
        url=("https://opcoes.net.br/opcoes/estrategias"),
        use_container_width=True,
    )

    st.sidebar.link_button(
        "OP LAB",
        type="secondary",
        url="https://go.oplab.com.br/",
        use_container_width=True,
    )

    st.sidebar.link_button(
        "Calculadora Probabilidades",
        type="primary",
        url="https://calculadora-probabilidade.streamlit.app/",
        use_container_width=True,
    )

    st.sidebar.link_button(
        "Status Invest",
        type="secondary",
        url="https://statusinvest.com.br/acoes/busca-avancada/1cb763ac-15c9-486a-b7d0-230730b88759",
        use_container_width=True,
    )

    st.sidebar.link_button(
        "Google Sheets",
        type="secondary",
        url="https://docs.google.com/spreadsheets/d/1ZCAIxrGrMd6QYgJrpdljrN-ZllPYvxbJ2G_8_4Smsmc/edit#gid=0",
        use_container_width=True,
    )

    st.sidebar.link_button(
        "Google Colab",
        type="secondary",
        use_container_width=True,
        url=(
            "https://colab.research.google.com/drive/17iKalZQs-kz4iBd7MvaiYW3iKZs4_9si?usp=sharing"
        ),
    )
    #########################################################
    if tickers:
        prices = yf.download(tickers, start=start, end=end)["Adj Close"]
        if len(tickers) == 1:
            prices = prices.to.frame()
            prices.columns = [tickers[0].rstrip(".SA")]
        prices.columns = prices.columns.str.rstrip(".SA")

        prices["IBOV"] = yf.download("^BVSP", start=start, end=end)["Adj Close"]
        return tickers, prices
    return None, None


######################################################
####### criando o MAIN (BODY)


def build_main(tickers, prices):  # construa a estrutura principal com tickers & prices

    weights = np.ones(len(tickers)) / len(tickers)  # MESMOS PESOS
    prices["portifolio"] = prices.drop("IBOV", axis=1) @ weights
    norm_prices = 100 * prices / prices.iloc[0]
    returns = prices.pct_change()[1:]  # excluindo a primeira linha q não tem valor
    vols = returns.std() * np.sqrt(252)
    rets = (norm_prices.iloc[-1] - 100) / 100

    mygrid = grid(3, 3, 3, 6, vertical_align="top")
    for t in prices.columns:
        c = mygrid.container(border=True)
        c.subheader(t, divider="red")
        colA, colB, colC = c.columns(3)
        if t == "portifolio":
            colA.image("LogoGodkom.ico", width=135)
        elif t == "IBOV":
            colA.image("pie-chart-svgrepo-com.svg", width=85)
        else:
            colA.image(
                f"https://raw.githubusercontent.com/thefintz/icones-b3/main/icones/{t}.png",
                width=85,
            )
        colB.metric(label="retorno", value=f"{rets[t]:.0%}")
        colC.metric(label="volatilidade", value=f"{vols[t]:.0%}")
        style_metric_cards(
            background_color="#FFE4B5", box_shadow=True, border_left_color="#d67b64"
        )
    ############################################
    ###### GRÁFICOS
    col1, col2 = st.columns(2, gap="large")
    with col1:  ###  primeiro gráfico
        st.subheader("Desempenho Relativo")
        st.line_chart(norm_prices, height=500)

    with col2:  ###  segundo gráfico
        st.subheader("Risco Retorno")
        fig = px.scatter(
            x=vols,
            y=rets,
            text=vols.index,
            color=rets / vols,
            color_continuous_scale=px.colors.sequential.Bluered_r,
        )
        fig.update_traces(
            textfont_color="white",
            marker=dict(size=45),
            textfont_size=10,
        )
        fig.layout.yaxis.title = "Retorno Total"
        fig.layout.xaxis.title = "Volatilidade (anualizada)"
        fig.layout.height = 500
        fig.layout.xaxis.tickformat = ".0%"
        fig.layout.yaxis.tickformat = ".0%"
        fig.layout.coloraxis.colorbar.title = "Sharpe"
        st.plotly_chart(fig, use_container_width=True)
    ######################################################################
    ######################################################################
    ### MAIN (BODY) segunda parte
    # Recarregando as variáveis de início e fim do período
    year = timedelta(365)
    start = pd.to_datetime("today") - year
    end = pd.to_datetime("today")

    tickers = st.text_input(
        "Dados Fundamentalistas Yahoo Finance yƒ | escolha o Ticker: ",
        "PETR4",
    )
    tickers = yf.Ticker(f"{tickers}.SA")  ###  Esta função do YF é espetacular
    tickerDF = tickers.history(period="1d", start=start, end=end)
    tickerDF.index = tickerDF.index.date

    ####################################
    ### DELTA
    ult_atualizacao = tickerDF.index.max()  # Data da última atualização
    ult_cotacao = round(
        tickerDF.loc[tickerDF.index.max(), "Close"], 2
    )  # Última cotação encontrada
    menor_cotacao = round(tickerDF["Close"].min(), 2)  # Menor cotação do período
    maior_cotacao = round(tickerDF["Close"].max(), 2)  # Maior cotação do período
    prim_cotacao = round(
        tickerDF.loc[tickerDF.index.min(), "Close"], 2
    )  # Última cotação do período
    delta = round(
        ((ult_cotacao - prim_cotacao) / prim_cotacao) * 100, 2
    )  # A variação da cotação no período

    ###########################################################
    ### LINHA UM dados do .info do Yahoo Finance
    col1, col2, col3, col4, col5, col6 = st.columns([2.4, 2.3, 1.4, 1, 1, 0.7])
    with col1:
        st.markdown(f"**Empresa :** {tickers.info['longName']}")
    with col2:
        st.markdown(f"**Mercado :** {tickers.info['industryDisp']}")
    with col3:
        st.markdown(f"**Ðiv. ¥ield** : {tickers.info['dividendYield']*100}")
    with col4:
        st.markdown(f"**Beta (ß)** : {tickers.info['beta']}")
    with col5:
        st.markdown(f"**ROE** : {tickers.info['returnOnEquity'] * 100}")
    with col6:
        st.markdown("Risco Retorno")
    ###############################
    ### LINHA DOIS dados manipulados do dataframe TicketDF:
    with col1:
        st.metric(
            f"**Preço Atual : {ult_atualizacao}**",
            "R$ {:,.2f}".format(ult_cotacao),
            f"{delta}%",
        )
    with col2:
        st.metric("**Menor cotação do período**", "R$ {:,.2f}".format(menor_cotacao))
    with col3:
        st.metric("**Maior cotação do período**", "R$ {:,.2f}".format(maior_cotacao))
    with col4:
        retorno_anual = (
            (tickerDF["Close"] / tickerDF["Close"].shift(1) - 1).mean() * 252 * 100
        )
        st.metric("**Retorno Anual** ", "{:,.2f}%".format(retorno_anual))
    with col5:
        stdev = np.std(tickerDF["Close"] / tickerDF["Close"].shift(1) - 1) * np.sqrt(
            252
        )
        st.metric("**Volatilidade ↑ ↓**", "{:,.2f}%".format(stdev * 100))
    with col6:
        st.metric(
            "**Risco ¤ Retorno**", "{:,.2f}".format(retorno_anual / (stdev * 100))
        )

    ##################################################################
    ### b a r r a   d e   e s t u d o s   m ú l t i p l o s

    dividendos, valuation, fundamentos, historia, carteira, carteira2 = st.tabs(
        [
            "**Dividendos**",
            "**Valuation**",
            "**Fundamentos**",
            "**[N]úmeros**",
            "**Carteira 2023**",
            "**Carteira 2024**",
        ]
    )
    ###########################################################
    with dividendos:
        st.subheader("Maiores Pagadoras de Dividendos")
        st.subheader("Dividend Yield maior que 6 %")
        funds = fundamentus.get_resultado()
        funds = funds.drop(
            [
                "psr",
                "pa",
                "pcg",
                "pebit",
                "mrgliq",
                "pacl",
                "evebitda",
                "mrgebit",
                "liqc",
                "liq2m",
                "c5y",
            ],
            axis=1,
        )
        funds = funds[
            funds["pl"] < 10
        ]  ## em outros estudos "Sabbius", por ex.: usava o PL < que 15
        funds = funds[funds["roe"] > 0]
        funds = funds[funds["evebit"] > 0]
        funds = funds[funds["roic"] > 0]
        funds = funds[funds["divbpatr"] < 1]
        funds = funds[funds["pl"] > 0]
        funds = funds[funds["dy"] > 0]
        funds = funds.sort_values("dy", ascending=False)

        #'dy'
        div = funds.iloc[1:37, 3]  # Filtro sobre as maiores pagadoras dividendos
        # a partir da 5ª linha até 19ª e somente a coluna 3 'dy'  (alt 166 ª)

        fig = st.bar_chart(
            div, color="#4D909A", width=1200, height=400, use_container_width=False
        )
        st.dataframe(div.head(37), width=200, height=1400)

        #####################################################################

    with valuation:
        st.subheader("Valuation")
        st.subheader("Fórmula de Graham Boas e Baratas")
        tabela = fundamentus.get_resultado()
        tabela = tabela.drop(
            [
                "psr",
                "pa",
                "pcg",
                "pebit",
                "mrgliq",
                "pacl",
                "evebitda",
                "mrgebit",
                "evebit",
                "roic",
                "roe",
                "divbpatr",
                "liq2m",
                "c5y",
            ],
            axis=1,
        )

        ### V A L U A T I O N     &&& G R A H A M &&&
        tabela["Valores_in"] = np.sqrt(22.5 * tabela["pvp"] * tabela["liqc"])
        tabela["Margem30"] = tabela["Valores_in"] * 0.30
        tabela["Preco_Teto"] = tabela["Valores_in"] - tabela["Margem30"]
        tabela["Valuation"] = tabela["cotacao"] < tabela["Preco_Teto"]
        tabela = tabela[tabela["cotacao"] < tabela["Preco_Teto"]]
        tabela = tabela.sort_values("dy", ascending=False)
        valu = tabela.iloc[6:32]  # Filtro sobre as maiores pagadoras dividendos
        # a partir da 26ª linha até 42ª e somente a coluna 3 (alt 166 ª)
        fig = st.bar_chart(
            valu, height=500
        )  ## , color="#4D909A", height=400, use_container_width=False
        st.dataframe(valu.head(11), width=1300, height=500)

    ##################################################################
    with fundamentos:
        st.subheader("Múltiplos & Rankings")
        st.subheader(" Sabbius | fundamentus.com.br | google.sheets | Godkom Invest")
        tabela2 = fundamentus.get_resultado()
        tabela2 = tabela2.drop(
            [
                "psr",
                "pa",
                "pcg",
                "pebit",
                "mrgliq",
                "pacl",
                "evebitda",
                "mrgebit",
                "liqc",
                "liq2m",
                "c5y",
                "patrliq",
                "cotacao",
                "divbpatr",
                "pvp",
                "dy",
            ],
            axis=1,
        )

        tabela2["pl"] = tabela2["pl"].replace(".", "")
        tabela2["pl"] = tabela2["pl"].replace(",", ".")
        tabela2["pl"] = tabela2["pl"].astype(float)
        tabela2["evebit"] = tabela2["evebit"].replace(".", "")
        tabela2["evebit"] = tabela2["evebit"].replace(",", ".")
        tabela2["evebit"] = tabela2["evebit"].astype(float)
        tabela2["roic"] = tabela2["roic"].replace("%", "")
        tabela2["roic"] = tabela2["roic"].replace(".", "")
        tabela2["roic"] = tabela2["roic"].replace(",", ".")
        tabela2["roic"] = tabela2["roic"].astype(float)

        # Eliminando as empresas com múliplos negativos
        tabela2 = tabela2[tabela2["pl"] < 10]
        tabela2 = tabela2[tabela2["roe"] > 0]
        tabela2 = tabela2[tabela2["evebit"] > 0]
        tabela2 = tabela2[tabela2["roic"] > 0]
        tabela2 = tabela2[tabela2["pl"] > 0]
        tabela2["roic"] = tabela2["roic"].rank(ascending=False)
        tabela2["class_pl"] = tabela2["pl"].rank(ascending=False)
        tabela2["class_roe"] = tabela2["roe"].rank(ascending=True)
        tabela2["ranking_plroe"] = tabela2["class_pl"] + tabela2["class_roe"]
        tabela2["class_ev_ebit"] = tabela2["evebit"].rank(ascending=False)
        tabela2["class_roic"] = tabela2["roic"].rank(ascending=True)
        tabela2["ranking_ev_roic"] = tabela2["class_ev_ebit"] + tabela2["class_roic"]
        tabela2["ranking_ev_roic"] = tabela2["ranking_ev_roic"].rank(ascending=True)
        # Filtrando empresas com movimentação diária acima de R$ 150.000,00
        # Indexando os múltiplos: P/L e EV/EBIT (decrescente) e ROE e ROIC (ascendentes)
        # tabela2 = tabela2.sort_values("dy", ascending=False)
        tabela2 = tabela2.sort_values("ranking_ev_roic", ascending=False)
        div = tabela2.iloc[55:75]  # Filtro sobre as maiores pagadoras dividendos
        # a partir da 5ª linha até 19ª e somente a coluna 3 'dy'  (alt 166 ª)
        fig = st.bar_chart(div, width=1400, height=600, use_container_width=False)

        st.dataframe(div, width=1200, height=800)

    with historia:

        st.subheader("Receita Líquida")
        st.subheader("Taxa de crescimento | MAIOR ROE MELHOR | 5 anos c5y |")
        tabela3 = fundamentus.get_resultado()
        tabela3 = tabela3.drop(
            [
                "psr",
                "pa",
                "pcg",
                "pebit",
                "pacl",
                "evebitda",
                "mrgebit",
                "roic",
                "liqc",
                "divbpatr",
                "liq2m",
                "evebit",
                "pvp",
                "pl",
                "patrliq",
                "mrgliq",
            ],
            axis=1,
        )
        tabela3 = tabela3[tabela3["roe"] > 0]
        hist = tabela3.iloc[
            260:287, 2:4
        ]  # Filtro sobre as maiores pagadoras dividendos
        # a partir da 5ª linha até 19ª e somente a coluna 3 'dy'  (alt 166 ª)
        hist = hist[hist["roe"] > 0]
        fig = st.bar_chart(hist, width=800, height=400, use_container_width=False)

        st.dataframe(hist, height=1000)

    ####################################################
    with carteira:
        st.subheader("Carteira Recomendada 2023")
        st.subheader("Múltiplos em evidência P/L < 15 ")
        cart = pd.read_csv("CarteiraGodkom.csv")
        ####### Gráfico
        cart["P/L"] = cart["P/L"].rank(ascending=False)
        fig = st.bar_chart(
            cart,
            x="TICKER",
            y="P/L",
            color="#4D909A",
            width=800,
            height=400,
            use_container_width=False,
        )

        st.table(cart)
    ###########################################################
    ####################################################
    with carteira2:
        st.subheader("Carteira Recomendada 2024")
        st.subheader("Múltiplos em evidência P/L < 15")
        cart2 = pd.read_csv("carteira2.csv")
        ####### Gráfico
        cart2["P/L"] = cart2["P/L"].rank(ascending=False)
        fig = st.bar_chart(
            cart2,
            x="TICKER",
            y="P/L",
            color="#4D909A",
            width=800,
            height=500,
            use_container_width=False,
        )

        st.table(cart2)


#############################
with st.sidebar:
    tickers, prices = build_sidebar()


if tickers:
    build_main(tickers, prices)
