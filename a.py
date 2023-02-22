import streamlit as st

# Data and plot libraries
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np


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


# SQL Queries and connector
sql_con = sqlite3.connect("Simulacao.db")
benef_con = sqlite3.connect("Saida.db")

id_rad_ = 12
benef_query = f'''
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

demanda_query = f'''
SELECT data, dem_ilum, dem_therm, COALESCE (id_rad1, id_rad2) as id_radiuino FROM (
(SELECT Data as data, demanda as dem_ilum, id_radiuino as id_rad1 FROM demanda_ilum_5)

LEFT JOIN
(SELECT data, demanda as dem_therm, id_radiuino as id_rad2 FROM demanda_therm_5)
USING (data));
'''

df_dem = pd.read_sql_query(con=sql_con, sql=demanda_query)
df_dem.index = pd.to_datetime(df_dem["data"])
df_dem = df_dem.groupby(df_dem.index.date).sum()
# ------------------------------------------------



st.set_page_config(layout = "wide")

# Page selection on the sidebar
st.sidebar.title("GeniIoT Dashboard")
page = st.sidebar.selectbox(label="Seleção de página",
                            options=["Consumo", "PEE", "Sistema"])


# Page development
def RenderPageConsumo():
    yAxis_dem = {"Demanda das Lâmpadas": "dem_ilum",
                'Demanda do Ar-Condicionado': "dem_therm"}

    col11, col12 = st.columns([1, 4])
    with st.container():
        with col11:
            st.text("")
            st.text("")
            st.text("")
            demSelect = st.multiselect(label="Selecione o Aparelho", 
                                       options=["Demanda das Lâmpadas", "Demanda do Ar-Condicionado"])
        
        demShow = [yAxis_dem[i] for i in demSelect]
        with col12:
            dem_fig = px.line(data_frame=df_dem, x=df_dem.index, y=demShow)
            st.plotly_chart(dem_fig)
            

    # Dictionary relating the selection box value to
    # the column name at the data frame
    yAxis = {'Temperature (ºC)': "Temp2-18B20 (°C)",
            'Luminosity (LUX)': "Luminosidade (lux)",
            'CO2 (ppm)': "Conc. CO2 (ppm)",
            'Humidity (%)': "Umid2-dht22 (%)",
            'AC Use (A)': ["Corrente1 (A)", "Corrente2 (A)"]}


    col1, col2 = st.columns([1, 4])
    # At the first container
    with st.container():
        # col1 = selection box
        with col1:
            st.text("")
            st.text("")
            st.text("")
            variable = st.selectbox(label="Selectione a Variável",
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
            tempSelect = st.multiselect(label="Selecione o Sensor de Temperatura", 
                                        options=["Door", "Center", "Window"])
            tempShow = [tempSelectDict[i] for i in tempSelect]
        
        with col22:
            tempFig = px.line(df2, y=tempShow, x="Data/Hora", width=500, height=400)
            st.plotly_chart(figure_or_data=tempFig)
        
        with col23:
            st.text("")
            st.text("")
            st.text("")
            HumSelect = st.multiselect(label="Selecione o Sensor de Umidade", 
                                       options=["Door", "Center", "Window"], key="aaaaaaa")
            HumShow = [HumSelectDict[i] for i in HumSelect]
        
        with col24:
            humFig = px.line(df2, y=HumShow, x="Data/Hora", width=500, height=400)
            st.plotly_chart(figure_or_data=humFig)
    return 0


def RenderPagePEE():
    df = pd.read_sql_query(sql=benef_query, con=sql_con)

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
        st.title("Visualização da Sala e Demanda")
        RenderPageConsumo()
    case "PEE":
        st.title("Evolução de PEE")
        RenderPagePEE()
    case "Sistema":
        st.title("Visualização do Sistema")
