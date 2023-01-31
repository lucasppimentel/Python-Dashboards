import streamlit as st

# Data and plot libraries
import sqlite3
import pandas as pd
import plotly.express as px


# ---------------- Data gathering ----------------
df = pd.read_csv("data2.TXT", sep=";")
df = df.drop(["Temp1-18B20 (°C)", "Conc. gas-MQ135 (ppm)"], axis=1)
df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
df.index = df["Data/Hora"]

# The data I'm using seems to be consistent only between 05-13-2021 and 05-31-2021
# Filter days before
def FiltrarDiaB(df, dia, mes, ano):
    return df.loc[df.index <= pd.Timestamp("{}-{}-{}".format(ano, mes, dia))]

# Filter days after
def FiltrarDiaA(df, dia, mes, ano):
    return df.loc[df.index >= pd.Timestamp("{}-{}-{}".format(ano, mes, dia))]

df = FiltrarDiaA(df, 13, 5, 2021)
df = FiltrarDiaB(df, 31, 5, 2021)
# ------------------------------------------------


#st.set_page_config(layout = "wide")


# Page selection on the sidebar
st.sidebar.title("Sidebar Title")
page = st.sidebar.selectbox(label="Seleção de página",
                            options=["Consumo", "PEE", "Sistema"])



# Page development
def RenderPageConsumo():
    col1, col2 = st.columns([1, 4])

    # Dictionary relating the selection box value to
    # the column name at the data frame
    yAxis = {'Temperature (ºC)': "Temp2-18B20 (°C)",
            'Luminosity (LUX)': "Luminosidade (lux)",
            'CO2 (ppm)': "Conc. CO2 (ppm)",
            'Humidity (%)': "Umid2-dht22 (%)",
            'AC Use (A)': ["Corrente1 (A)", "Corrente2 (A)"]}

    # At the first container
    with st.container():
        # col1 = selection box
        with col1:
            st.text("")
            st.text("")
            st.text("")
            variable = st.selectbox(label="",
                                    options=["Temperature (ºC)", 
                                            "Luminosity (LUX)", 
                                            "CO2 (ppm)", 
                                            "Humidity (%)", 
                                            "AC Use (A)"])
            slider_val = st.slider(label="Date filter",
                                min_value=min(df.index.day), 
                                max_value=max(df.index.day),
                                value=(min(df.index.day), max(df.index.day)), 
                                step=1)
        
        # col2 = graph
        # Data Frame filtered by date slider
        df2 = FiltrarDiaA(df, slider_val[0], 5, 2021)
        df2 = FiltrarDiaB(df2, slider_val[1], 5, 2021)

        with col2:
            fig = px.line(df2, y=yAxis[variable], x="Data/Hora")
            st.plotly_chart(fig)
    
    return 0



match page:
    case "Consumo":
        st.title("Essa é a pagina 2")
        RenderPageConsumo()
    case "Page2":
        st.title("Essa é a pagina 2")
    case "Page3":
        st.title("Essa é a pagina 3")