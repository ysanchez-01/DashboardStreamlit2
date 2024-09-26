import pandas as pd
import streamlit as st
import plotly.express as px
from openai import OpenAI

# Constants
DATA_URL = 'https://raw.githubusercontent.com/ysanchez-01/Dashbord-Streamlit/refs/heads/main/Datos_proyecto_limpio.csv'

# Helper functions
@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)

def filter_data(data, industry, country, size):
    return data[(data['Industry'] == industry) & 
                (data['Country'] == country) & 
                (data['Company_Size'] == size)]

def calculate_financial_ratios(df):
    df['Current_Ratio'] = df['Current_Assets'] / df['Current_Liabilities']
    df['Debt_to_Equity_Ratio'] = (df['Short_Term_Debt'] + df['Long_Term_Debt']) / df['Equity']
    df['Interest_Coverage_Ratio'] = df['Total_Revenue'] / df['Financial_Expenses']
    return df

def create_chart(data, x, y, chart_type, title):
    if chart_type == 'bar':
        return px.bar(data, x=x, y=y, title=title)
    elif chart_type == 'line':
        return px.line(data, x=x, y=y, title=title)
    elif chart_type == 'pie':
        return px.pie(data, values=y, names=x, title=title)

def get_openai_response(prompt):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un financiero experto en solvencia que trabaja para la aseguradora patito. Responde en español con un máximo de 50 palabras."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al obtener respuesta de OpenAI: {e}")
        return None

# Main app
def main():
    st.set_page_config(page_title="Dashboard de Indicadores Financieros", layout="wide")

    st.markdown('<h1 style="color:navy;">Dashboard de Indicadores Financieros</h1>', unsafe_allow_html=True)
    st.markdown("Este proyecto es una aplicación web que permite a los usuarios evaluar ratios financieros por Industria, País y Tamaño.")

    data = load_data()

    # Sidebar for filters
    st.sidebar.header("Filtros")
    industry = st.sidebar.selectbox('Industria:', data['Industry'].unique())
    country = st.sidebar.selectbox('País:', data['Country'].unique())
    size = st.sidebar.selectbox('Tamaño de la Empresa:', data['Company_Size'].unique())

    filtered_data = filter_data(data, industry, country, size)
    filtered_data = calculate_financial_ratios(filtered_data)

    # Main content
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Datos filtrados")
        st.dataframe(filtered_data)

    with col2:
        st.subheader("Estadísticas básicas")
        st.dataframe(filtered_data.describe().T)

    # Charts
    st.header("Análisis gráfico")
    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        fig_liquidez = create_chart(filtered_data, 'Company_ID', 'Current_Ratio', 'bar', 'Ratio de Liquidez por Empresa')
        st.plotly_chart(fig_liquidez, use_container_width=True)

    with chart_col2:
        fig_deuda = create_chart(filtered_data, 'Company_ID', 'Debt_to_Equity_Ratio', 'line', 'Ratio Deuda a Patrimonio por Empresa')
        st.plotly_chart(fig_deuda, use_container_width=True)

    with chart_col3:
        fig_cobertura = create_chart(filtered_data, 'Company_ID', 'Interest_Coverage_Ratio', 'pie', 'Cobertura de Gastos Financieros')
        st.plotly_chart(fig_cobertura, use_container_width=True)

    # OpenAI integration
    st.header("Consulta con el asistente financiero")
    user_prompt = st.text_input("Escribe tu consulta financiera aquí:")
    if user_prompt:
        response = get_openai_response(user_prompt)
        if response:
            st.write(f"Respuesta: {response}")

if __name__ == "__main__":
    main()