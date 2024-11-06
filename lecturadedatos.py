import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

# Configuración de la base de datos
db_config = {
    'host': 'localhost',  # Cambia esto si tu servidor MySQL está en otra dirección
    'user': 'root',       # Cambia esto por tu nombre de usuario MySQL
    'password': '',       # Cambia esto por tu contraseña MySQL
    'database': 'bd_movilidad' # Cambia esto por el nombre de tu base de datos
}

# Conectar a la base de datos MySQL
conn = mysql.connector.connect(**db_config)

# Consulta SQL para leer todos los datos de la tabla Movilidad, Fuerza y Estadisticas
query_movilidad = "SELECT * FROM Movilidad"
query_fuerza = "SELECT * FROM Fuerza"
query_estadisticas = "SELECT * FROM Estadisticas"

# Cargar los datos de las tres tablas
movilidad_data = pd.read_sql(query_movilidad, conn)
fuerza_data = pd.read_sql(query_fuerza, conn)
estadisticas_data = pd.read_sql(query_estadisticas, conn)

# Cerrar la conexión
conn.close()

# Mostrar los primeros registros para verificar que se han cargado correctamente
print("Datos de Movilidad:")
print(movilidad_data.head())
print("\nDatos de Fuerza:")
print(fuerza_data.head())
print("\nDatos de Estadísticas:")
print(estadisticas_data.head())

# Graficar los datos
plt.figure(figsize=(12, 8))

# Gráfico de los movimientos de la tabla Movilidad
plt.plot(movilidad_data['id_usuario'], movilidad_data['Movimiento_Izquierda'], label='Movimiento Izquierda', color='blue')
plt.plot(movilidad_data['id_usuario'], movilidad_data['Movimiento_Derecha'], label='Movimiento Derecha', color='orange')
plt.plot(movilidad_data['id_usuario'], movilidad_data['Movimiento_Arriba'], label='Movimiento Arriba', color='green')
plt.plot(movilidad_data['id_usuario'], movilidad_data['Movimiento_Abajo'], label='Movimiento Abajo', color='red')
plt.plot(movilidad_data['id_usuario'], movilidad_data['Movimiento_Centro'], label='Movimiento Centro', color='purple')

# Gráfico de la fuerza estimada de la tabla Fuerza
plt.plot(fuerza_data['id_usuario'], fuerza_data['fuerza_estimado'], label='Fuerza Estimada', color='cyan')

# Configuración del gráfico
plt.title('Comparación de Movimientos y Fuerza Estimada')
plt.xlabel('ID Usuario')
plt.ylabel('Valores')
plt.legend()
plt.grid(True)

# Mostrar el gráfico
plt.show()
