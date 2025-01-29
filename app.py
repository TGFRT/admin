import streamlit as st
import bcrypt
import requests
import pandas as pd

# Contraseña encriptada
hashed_password = bcrypt.hashpw("perupaysergiorequena".encode('utf-8'), bcrypt.gensalt())

# Función para verificar las credenciales
def check_credentials(username, password):
    return username == "administrador" and bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Sidebar para el inicio de sesión
def login_sidebar():
    st.sidebar.title("Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Ingresar"):
        if check_credentials(username, password):
            st.session_state.authenticated = True
            st.sidebar.success("Inicio de sesión exitoso")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")

# Función para obtener los datos de la API
def fetch_data():
    url = "https://apisheetsdb.vercel.app/api/sheets?range=A1:Z100"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            st.error(f"Error al obtener datos: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error en la solicitud: {e}")
        return pd.DataFrame()

# Dashboard de administración
def admin_dashboard():
    st.title("📊 Panel de Administración")
    st.write("Bienvenido al panel de control. Aquí están los datos de la API:")

    data = fetch_data()
    
    if not data.empty:
        st.dataframe(data)
    else:
        st.warning("No se encontraron datos.")

# Lógica principal
def main():
    st.set_page_config(page_title="Admin Dashboard", layout="wide")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    login_sidebar()

    if st.session_state.authenticated:
        admin_dashboard()
    else:
        st.warning("Por favor, inicia sesión en la barra lateral.")

if __name__ == "__main__":
    main()
