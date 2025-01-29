import streamlit as st
import bcrypt
import requests
import pandas as pd

# Contraseña encriptada
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
            data = response.json()["data"]  # Extraer solo los datos

            # Obtener la primera fila como encabezados
            headers = data[0]
            records = data[1:]

            # Asegurar que cada fila tenga la misma cantidad de columnas que los encabezados
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

# Función para actualizar el estado en la API
def update_user_status(dni, new_state):
    url = "https://apisheetsdb.vercel.app/api/sheets"
    range = f"A2:Q100"  # Rango de celdas en donde se encuentran los datos, puede ajustarse según sea necesario.
    
    # Encuentra la fila que contiene el DNI del usuario a actualizar
    data = fetch_data()  # Esta función carga todos los datos
    user_row = None
    for idx, row in data.iterrows():
        if row['dni'] == dni:
            user_row = idx + 2  # Las filas de Google Sheets comienzan desde 1, por lo que hay que sumar 2
            break

    if user_row is not None:
        # Crear el cuerpo de la solicitud para actualizar solo la columna 'estado'
        range_to_update = f"A{user_row}:Q{user_row}"  # Actualiza la fila completa, puedes ajustar el rango a las columnas necesarias
        values = [[new_state]]  # Solo actualiza el estado

        # Realizar la petición PUT a la API
        response = requests.put(url, json={
            "range": range_to_update,
            "values": values
        })

        if response.status_code == 200:
            st.success(f"Estado del usuario con DNI {dni} actualizado a {new_state}")
        else:
            st.error(f"Error al actualizar el estado: {response.status_code}")
    else:
        st.error("No se encontró el usuario con ese DNI.")

# Mostrar detalles del usuario en una ventana emergente
def show_user_details(user):
    with st.expander(f"📌 {user['nombreCompleto']} - {user['dni']}"):
        st.write(f"📞 **Teléfono:** {user['numeroCelular']}")
        st.write(f"🎂 **Fecha de Nacimiento:** {user['fechaNacimiento']}")
        st.write(f"💼 **Tipo de Empleo:** {user['tipoEmpleo']}")
        st.write(f"🏢 **RUC Empresa:** {user['rucEmpresa']}")
        st.write(f"📜 **En Planilla:** {user['enPlanilla']}")
        st.write(f"⚠️ **En Infocorp:** {user['enInfocorp']}")
        st.write(f"💰 **Monto Préstamo:** S/. {user['montoPrestamo']}")
        st.write(f"📅 **Frecuencia de Pago:** {user['frecuenciaPago']}")
        st.write(f"⏳ **Plazo Préstamo:** {user['plazoPrestamo']} meses")
        st.write(f"📊 **Estado:** {user['estado']}")
        
        if user["estado"] == "Denegado":
            st.write(f"❌ **Razón de Rechazo:** {user['razonRechazo']}")

        # Selector para cambiar el estado
        new_state = st.selectbox("Actualizar Estado", ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"], index=["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"].index(user['estado']))

        if st.button(f"Actualizar estado de {user['nombreCompleto']}"):
            update_user_status(user['dni'], new_state)
        
        st.write(f"✅ **Créditos Pagados:** {user['creditos pagados']}")
        st.write(f"📄 **Datos adicionales:** {user['datos']}")

# Dashboard de administración con filtros después del login
def admin_dashboard():
    st.title("📊 Panel de Administración")

    # Cargar datos
    data = fetch_data()

    if not data.empty:
        # Filtros después del inicio de sesión
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
    password = st.sidebar.text_input("Contraseña", type="password", help="Ingresa tu contraseña")

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
