from flask import Flask, render_template, jsonify, request
import mysql.connector
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bd_movilidad"
    )

def obtener_datos_estadisticas():
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener datos de la tabla 'estadisticas'
    cursor.execute("""
        SELECT u.nombre, e.promedio_duracion, e.total_sesiones, e.fuerza_categoria
        FROM estadisticas e
        JOIN usuario u ON e.id_usuario = u.id_usuario
    """)
    resultados_estadisticas = cursor.fetchall()
    
    # Obtener datos de la tabla 'movilidad' incluyendo la velocidad promedio
    cursor.execute("""
        SELECT u.nombre, SUM(m.Movimiento_Izquierda), SUM(m.Movimiento_Derecha), 
               SUM(m.Movimiento_Arriba), SUM(m.Movimiento_Abajo), AVG(m.Velocidad_Promedio)
        FROM movilidad m
        JOIN usuario u ON m.id_usuario = u.id_usuario
        GROUP BY u.nombre
    """)
    resultados_movilidad = cursor.fetchall()
    
    # Obtener datos de la tabla 'fuerza'
    cursor.execute("""
        SELECT u.nombre, AVG(f.fuerza_estimado), f.categoria_fuerza
        FROM fuerza f
        JOIN usuario u ON f.id_usuario = u.id_usuario
        GROUP BY u.nombre
    """)
    resultados_fuerza = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return resultados_estadisticas, resultados_movilidad, resultados_fuerza

@app.route('/')
def index():
    return render_template('timeReal.html')

@app.route('/datos_grafico', methods=['GET'])
def datos_grafico():
    resultados_estadisticas, resultados_movilidad, resultados_fuerza = obtener_datos_estadisticas()

    # Gráficos
    trace1 = go.Bar(x=[row[0] for row in resultados_estadisticas], y=[row[1] for row in resultados_estadisticas], name='Promedio Duración')
    trace2 = go.Bar(x=[row[0] for row in resultados_estadisticas], y=[row[2] for row in resultados_estadisticas], name='Número Total de Sesiones')
    trace3 = go.Bar(x=[row[0] for row in resultados_movilidad], y=[row[5] for row in resultados_movilidad], name='Velocidad Promedio')
    trace4 = go.Bar(x=[row[0] for row in resultados_fuerza], y=[row[2] for row in resultados_fuerza], name='Categoría de Fuerza')
    trace5 = go.Bar(x=[row[0] for row in resultados_fuerza], y=[row[1] for row in resultados_fuerza], name='Fuerza Estimada Promedio')
    
    layout = go.Layout(
        title=f'Estadísticas de Jugadores - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        xaxis_title='Usuarios',
        yaxis_title='Valores',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    fig = go.Figure(data=[trace1, trace2, trace3, trace4, trace5], layout=layout)
    graph_json = pio.to_json(fig)

    return jsonify(graph_json)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
