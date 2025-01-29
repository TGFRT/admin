import streamlit as st
import requests
import pandas as pd

# URL de la API de Google Sheets
API_URL = 'https://apisheetsdb.vercel.app/api/sheets'

# Obtener datos de la hoja de Google Sheets
def fetch_data():
    response = requests.get(f'{API_URL}?range=A1:O100')
    if response.status_code == 200:
        return response.json()['data']
    else:
        st.error('Error al obtener los datos.')
        return []

# Actualizar el estado de un usuario
def update_user_state(range, values):
    response = requests.put(API_URL, json={
        "range": range,
        "values": values
    })
    if response.status_code == 200:
        st.success("Estado actualizado exitosamente")
    else:
        st.error("Error al actualizar el estado")

# Mostrar el panel de administración
def admin_dashboard():
    data = fetch_data()
    if not data:
        return

    # Convertir los datos a un DataFrame para mejor visualización
    df = pd.DataFrame(data[1:], columns=data[0])

    # Mostrar los datos
    st.write(df)

    # Filtros
    dni_filter = st.text_input("Filtrar por DNI")
    name_filter = st.text_input("Filtrar por Nombre")
    state_filter = st.selectbox("Filtrar por Estado", ["Todos", "Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"])

    # Aplicar filtros
    filtered_data = df
    if dni_filter:
        filtered_data = filtered_data[filtered_data['dni'].str.contains(dni_filter)]
    if name_filter:
        filtered_data = filtered_data[filtered_data['nombreCompleto'].str.contains(name_filter)]
    if state_filter != "Todos":
        filtered_data = filtered_data[filtered_data['estado'] == state_filter]

    # Mostrar datos filtrados
    if not filtered_data.empty:
        st.write(filtered_data)

        # Seleccionar usuario para modificar su estado
        user_to_modify = st.selectbox("Seleccionar usuario para modificar estado", filtered_data['nombreCompleto'])
        
        if user_to_modify:
            # Mostrar detalles del usuario
            user_data = filtered_data[filtered_data['nombreCompleto'] == user_to_modify].iloc[0]
            st.write(user_data)

            # Cambiar el estado
            new_state = st.selectbox("Nuevo Estado", ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"])
            
            if st.button("Actualizar Estado"):
                # Rango de la fila a actualizar (en este caso, 'A2:O2' es solo un ejemplo)
                range = f"'Hoja 1'!A{filtered_data[filtered_data['nombreCompleto'] == user_to_modify].index[0] + 2}:O{filtered_data[filtered_data['nombreCompleto'] == user_to_modify].index[0] + 2}"
                
                # Actualizar solo la columna "estado"
                values = [[user_data['nombreCompleto'], user_data['numeroCelular'], user_data['dni'], user_data['fechaNacimiento'], user_data['tipoEmpleo'],
                           user_data['rucEmpresa'], user_data['enPlanilla'], user_data['enInfocorp'], user_data['montoPrestamo'], user_data['montoCuota'],
                           user_data['frecuenciaPago'], user_data['plazoPrestamo'], new_state, user_data['razonRechazo'], user_data['contrasena'], user_data['creditos pagados'], user_data['datos']]]
                
                # Enviar solicitud para actualizar el estado
                update_user_state(range, values)
    else:
        st.write("No se encontraron resultados con los filtros aplicados.")

# Mostrar el panel de administración
def main():
    st.title("Panel de Administración")
    admin_dashboard()

if __name__ == "__main__":
    main()

