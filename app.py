import streamlit as st
import bcrypt
import requests
import pandas as pd

# Configurar contraseña encriptada
hashed_password = bcrypt.hashpw("perupaysergiorequena".encode('utf-8'), bcrypt.gensalt())

# Función para verificar credenciales
def check_credentials(username, password):
    return username == "administrador" and bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Función para obtener datos de la API
def fetch_data():
    url = "https://apisheetsdb.vercel.app/api/sheets?range=A1:Z100"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()["data"]
            headers = data[0]  # La primera fila es el encabezado
            records = data[1:]  # Datos sin encabezados

            # Asegurar que cada fila tenga el mismo número de columnas
            fixed_data = [row + [None] * (len(headers) - len(row)) for row in records]

            # Convertir a DataFrame
            df = pd.DataFrame(fixed_data, columns=headers)

            return df
        else:
            st.error(f"Error al obtener datos: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error en la solicitud: {e}")
        return pd.DataFrame()

# Función para actualizar el estado en Google Sheets
def update_user_state(dni, new_state):
    update_url = "https://apisheetsdb.vercel.app/api/sheets/update"  # Endpoint de actualización

    payload = {
        "dni": dni,
        "estado": new_state
    }

    response = requests.post(update_url, json=payload)

    if response.status_code == 200:
        st.success(f"✅ Estado actualizado correctamente a **{new_state}**")
    else:
        st.error(f"❌ Error al actualizar el estado: {response.text}")

# Mostrar detalles del usuario con opción para editar estado
def show_user_details(user):
    with st.expander(f"📌 {user['nombreCompleto']} - {user['dni']}"):
        st.write(f"📞 **Teléfono:** {user['numeroCelular']}")
        st.write(f"💰 **Monto Préstamo:** S/. {user['montoPrestamo']}")
        st.write(f"📜 **Estado Actual:** {user['estado']}")

        new_state = st.selectbox(
            "Cambiar Estado",
            ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"],
            index=["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"].index(user["estado"]) if user["estado"] in ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"] else 0
        )

        if st.button(f"Actualizar Estado de {user['nombreCompleto']}"):
            update_user_state(user["dni"], new_state)

# Dashboard de administración con filtros
def admin_dashboard():
    st.title("📊 Panel de Administración")

    data = fetch_data()

    if not data.empty:
        st.subheader("🔍 Filtros de búsqueda")
        col1, col2, col3 = st.columns(3)

        dni_filter = col1.text_input("Buscar por DNI")
        name_filter = col2.text_input("Buscar por Nombre")
        state_filter = col3.selectbox("Filtrar por Estado", ["Todos", "Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"])

        # Aplicar filtros
        filtered_data = data
        if dni_filter:
            filtered_data = filtered_data[filtered_data["dni"].astype(str).str.contains(dni_filter, case=False, na=False)]
        if name_filter:
            filtered_data = filtered_data[filtered_data["nombreCompleto"].str.contains(name_filter, case=False, na=False)]
        if state_filter != "Todos":
            filtered_data = filtered_data[filtered_data["estado"] == state_filter]

        # Mostrar resultados filtrados
        st.subheader(f"Resultados ({len(filtered_data)})")
        for _, user in filtered_data.iterrows():
            show_user_details(user)
    else:
        st.warning("No se encontraron datos.")

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
