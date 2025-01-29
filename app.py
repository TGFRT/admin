import streamlit as st
import requests

# URL de la API de SheetsDB
API_URL = "https://apisheetsdb.vercel.app/api/sheets"

# Información de inicio de sesión del administrador
ADMIN_USERNAME = "administrador"
ADMIN_PASSWORD = "perupaysergiorequena"

# Función para obtener los datos de la API
def fetch_data():
    response = requests.get(f"{API_URL}?range=A1:Z100")
    return response.json().get("data", [])

# Función de inicio de sesión
def login():
    st.sidebar.title("Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Iniciar sesión"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("¡Inicio de sesión exitoso!")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos.")

# Verificar si el usuario está autenticado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Si el usuario no está autenticado, mostrar el formulario de inicio de sesión
if not st.session_state.logged_in:
    login()

# Si el usuario está autenticado, mostrar el dashboard
else:
    st.title("Panel de Administración")

    # Filtros para filtrar por DNI, nombre y estado
    st.sidebar.header("Filtros")
    
    dni_filter = st.sidebar.text_input("Filtrar por DNI")
    name_filter = st.sidebar.text_input("Filtrar por Nombre")
    state_filter = st.sidebar.selectbox("Filtrar por Estado", ["Todos", "Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"])

    # Obtener los datos del usuario
    data = fetch_data()

    # Filtrar los datos basados en los filtros
    filtered_data = []
    for row in data:
        if dni_filter and dni_filter not in row[2]:
            continue
        if name_filter and name_filter.lower() not in row[0].lower():
            continue
        if state_filter != "Todos" and state_filter != row[12]:  # Asegúrate de que esta columna corresponda al estado
            continue
        filtered_data.append(row)

    if filtered_data:
        for user in filtered_data:
            st.subheader(f"Detalles del Usuario: {user[0]}")

            # Mostrar detalles del usuario
            st.write(f"Nombre: {user[0]}")
            st.write(f"Celular: {user[1]}")
            st.write(f"DNI: {user[2]}")
            st.write(f"Fecha de nacimiento: {user[3]}")
            st.write(f"Tipo de empleo: {user[4]}")
            st.write(f"RUC de empresa: {user[5]}")
            st.write(f"En planilla: {user[6]}")
            st.write(f"En Infocorp: {user[7]}")
            st.write(f"Monto del préstamo: {user[8]}")
            st.write(f"Monto de cuota: {user[9]}")
            st.write(f"Frecuencia de pago: {user[10]}")
            st.write(f"Plazo de préstamo: {user[11]}")
            st.write(f"Estado: {user[12]}")
            st.write(f"Razón de rechazo: {user[13]}")
            st.write(f"Contraseña: {user[14]}")
            st.write(f"Créditos pagados: {user[15]}")
            st.write(f"Datos: {user[16]}")
    else:
        st.write("No se encontraron usuarios con los filtros seleccionados.")


