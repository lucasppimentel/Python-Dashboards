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



st.set_page_config(layout = "wide")

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
            fig = px.line(df2, y=yAxis[variable], x="Data/Hora", width=1000)
            st.plotly_chart(fig)
    
    col21, col22, col23, col24 = st.columns([1, 3, 1, 3])
    tempSelectDict = {'Door':'Temp3-18B20 (°C)','Window':'Temp4-18B20 (°C)','Center':'Temp2-18B20 (°C)'}
    HumSelectDict = {'Door':'Umid1-dht22 (%)','Window':'Umid2-dht22 (%)','Center':'Umid3-dht22 (%)'}

    
    with st.container():
        with col21:
            st.text("")
            st.text("")
            st.text("")
            tempSelect = st.multiselect(label="", options=["Door", "Center", "Window"])
            tempShow = [tempSelectDict[i] for i in tempSelect]
        
        with col22:
            tempFig = px.line(df2, y=tempShow, x="Data/Hora", width=500, height=400)
            st.plotly_chart(figure_or_data=tempFig)
        
        with col23:
            st.text("")
            st.text("")
            st.text("")
            HumSelect = st.multiselect(label="", options=["Door", "Center", "Window"], key="aaaaaaa")
            HumShow = [HumSelectDict[i] for i in HumSelect]
        
        with col24:
            humFig = px.line(df2, y=HumShow, x="Data/Hora", width=500, height=400)
            st.plotly_chart(figure_or_data=humFig)
    return 0


def RenderPagePEE():
    benef_con = sqlite3.connect("Saida.db")

    id_rad_ = 12
    query = f'''
    SELECT data, IlumA, ThermA, COALESCE (id_rad1, id_rad2) as id_radiuino FROM (
    (SELECT distinct data FROM beneficio_anualizado)
    
    LEFT JOIN 
    (SELECT data, id_radiuino as id_rad1, valor as IlumA 
    FROM beneficio_anualizado 
    WHERE tipo = 1 and id_radiuino = {id_rad_}) 
    USING (data)
    
    LEFT JOIN 
    (SELECT data, id_radiuino as id_rad2, valor as ThermA 
    FROM beneficio_anualizado 
    WHERE tipo = 2 and id_radiuino = {id_rad_}) 
    USING (data));
    '''

    df = pd.read_sql_query(sql=query, con=benef_con)

    col1, col2 = st.columns([1, 4])

    with col1:
        slider_val = st.slider(label="Date filter",
                                min_value=1, 
                                max_value=2,
                                value=1, 
                                step=1)
    
    with col2:
        rcb_fig = px.scatter(df, x="data", y=["IlumA", "ThermA"])
        st.plotly_chart(rcb_fig)

    return 0


match page:
    case "Consumo":
        st.title("Essa é a pagina 1")
        RenderPageConsumo()
    case "PEE":
        st.title("Essa é a pagina 2")
        RenderPagePEE()
    case "Sistema":
        st.title("Essa é a pagina 3")
