import os
import network
import machine
from machine import ADC, Pin
from secrets import secrets  # Archivo separado para las credenciales Wi-Fi
from Wifi_lib import wifi_init, get_html  # Librerías externas
import time
import urequests as requests
import ujson

# Inicializar la conexión Wi-Fi
wifi_init()

class Board:
    class BoardType:
        PICO_W = 'Raspberry Pi Pico W'
        PICO = 'Raspberry Pi Pico'
        RP2040 = 'RP2040'
        ESP8266 = 'ESP8266'
        ESP32 = 'ESP32'
        UNKNOWN = 'Unknown'

    def __init__(self):
        self.type = self.detect_board_type()
        self.setup_pins()

    def detect_board_type(self):
        sysname = os.uname().sysname.lower()
        machine_name = os.uname().machine.lower()
        # Detectar Raspberry Pi Pico W y Pico
        if sysname == 'rp2' and 'pico w' in machine_name:
            return self.BoardType.PICO_W
        elif sysname == 'rp2' and 'pico' in machine_name:
            return self.BoardType.PICO
        elif sysname == 'rp2' and 'rp2040' in machine_name:
            return self.BoardType.RP2040
        # Detectar ESP8266
        elif sysname == 'esp8266':
            return self.BoardType.ESP8266
        # Detectar ESP32
        elif sysname == 'esp32' and 'esp32' in machine_name:
            return self.BoardType.ESP32
        # Desconocido
        else:
            return self.BoardType.UNKNOWN
        
# Detectar tipo de placa
BOARD_TYPE = Board().type
print("Tarjeta Detectada: " + BOARD_TYPE)        

# Configuración de los pines según la tarjeta detectada
if BOARD_TYPE == Board.BoardType.PICO_W:
    # Configuración específica para la Pico W
    # Puedes agregar pines específicos aquí si es necesario
    pass

elif BOARD_TYPE == Board.BoardType.PICO or BOARD_TYPE == Board.BoardType.RP2040:
    # Configuración específica para Pico y RP2040
    # Puedes agregar pines específicos aquí si es necesario
    pass

elif BOARD_TYPE == Board.BoardType.ESP8266:
    # Configuración de pines para el ESP8266
    # Puedes agregar pines específicos aquí si es necesario
    pass

elif BOARD_TYPE == Board.BoardType.ESP32:
    # Configuración de los pines del joystick
    VRx = ADC(Pin(32))  # Conectado a D32
    VRy = ADC(Pin(33))  # Conectado a D33
    VRx.atten(ADC.ATTN_11DB)  # Configura el rango de voltaje
    VRy.atten(ADC.ATTN_11DB)

    # Configuración del pin del botón con resistencia pull-up
    SW = Pin(25, Pin.IN, Pin.PULL_UP)  # Botón conectado a D25

else:
    print("Placa desconocida, no se configuraron pines específicos.")

# Inicialización de variables
movimiento_arriba = 0
movimiento_abajo = 0
movimiento_izquierda = 0
movimiento_derecha = 0
movimiento_centro = 0  # Nueva variable para contar movimientos en el centro
duracion_inicio = 0
duracion_uso = 0

# Definir rangos para el joystick
RANGO_CENTRO = (1800, 1900)  # Rango para el centro
RANGO_IZQUIERDA = (0, 100)    # Rango para movimiento izquierda
RANGO_DERECHA = (3900, 4095)  # Rango para movimiento derecha
RANGO_ARRIBA = (0, 100)       # Rango para movimiento arriba
RANGO_ABAJO = (3900, 4095)    # Rango para movimiento abajo

url = "http://192.168.86.25/PicoEspInsercionDatos.php"  # Reemplaza con la URL correcta

def ingresar_datos_usuario():
    # Pedir nombre y correo antes de iniciar el ejercicio
    nombre = input("Por favor, ingresa tu nombre: ")
    correo = input("Por favor, ingresa tu correo: ")
    return nombre, correo

def mostrar_menu():
    print("\n--- Menú ---")
    print("1. Iniciar ejercicio")
    print("2. Iniciar ejercicio por tiempo limitado")
    print("3. Salir")
    opcion = input("Selecciona una opción: ")
    return opcion

def iniciar_sesion(url, nombre, correo):
        global movimiento_arriba, movimiento_abajo, movimiento_izquierda, movimiento_derecha, movimiento_centro, duracion_inicio, duracion_uso
        movimiento_arriba = 0
        movimiento_abajo = 0
        movimiento_izquierda = 0
        movimiento_derecha = 0
        movimiento_centro = 0  # Reiniciar contador de centro
        duracion_inicio = time.time()

        print("Iniciando ejercicio de control del joystick...")
        try:
            while True:
                # Leer valores del joystick
                x = VRx.read()  # Lee el valor de VRx
                y = VRy.read()  # Lee el valor de VRy

                # Evaluar frecuencia de uso
                if RANGO_IZQUIERDA[0] <= x <= RANGO_IZQUIERDA[1]:  # Movimiento a la izquierda
                    movimiento_izquierda += 1
                elif RANGO_DERECHA[0] <= x <= RANGO_DERECHA[1]:  # Movimiento a la derecha
                    movimiento_derecha += 1
                elif RANGO_CENTRO[0] <= x <= RANGO_CENTRO[1] and RANGO_CENTRO[0] <= y <= RANGO_CENTRO[1]:
                    movimiento_centro += 1  # Contar como movimiento en el centro
                elif RANGO_ABAJO[0] <= y <= RANGO_ABAJO[1]:  # Movimiento hacia abajo
                    movimiento_abajo += 1
                elif RANGO_ARRIBA[0] <= y <= RANGO_ARRIBA[1]:  # Movimiento hacia arriba
                    movimiento_arriba += 1

                # Calcular la duración de uso
                duracion_uso = time.time() - duracion_inicio
                
                # Mostrar los valores en consola
                print("X:", x, "Y:", y)
                print("Movimiento Izquierda:", movimiento_izquierda, "Movimiento Derecha:", movimiento_derecha)
                print("Movimiento Arriba:", movimiento_arriba, "Movimiento Abajo:", movimiento_abajo)
                print("Movimiento Centro:", movimiento_centro)  # Mostrar conteo de centro
                print("Duración de Uso (s):", round(duracion_uso, 2))
                
                # Crear el JSON con los datos generados, incluyendo nombre y correo
                data = {
                    "Nombre": nombre,
                    "Correo": correo,
                    "Movimiento_Izquierda": movimiento_izquierda,
                    "Movimiento_Derecha": movimiento_derecha,
                    "Movimiento_Arriba": movimiento_arriba,
                    "Movimiento_Abajo": movimiento_abajo,
                    "Movimiento_Centro": movimiento_centro,
                    "Duracion_uso": round(duracion_uso, 2)
                }

                # Convertir el JSON en una cadena y enviarlo al servidor
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, data=ujson.dumps(data), headers=headers)

                # Verificar la respuesta del servidor
                print("Datos enviados:", data)
                print("Respuesta del servidor:", response.text)
                response.close()

                time.sleep(0.5)  # Espera 0.5 segundos antes de la siguiente lectura

        except KeyboardInterrupt:
            # Finaliza la sesión y muestra un mensaje
            print("Sesión finalizada")
            mostrar_resumen()

def iniciar_sesion_tiempo(duracion):
    global movimiento_arriba, movimiento_abajo, movimiento_izquierda, movimiento_derecha, movimiento_centro, duracion_inicio, duracion_uso
    movimiento_arriba = 0
    movimiento_abajo = 0
    movimiento_izquierda = 0
    movimiento_derecha = 0
    movimiento_centro = 0  # Reiniciar contador de centro
    duracion_inicio = time.time()

    print(f"Iniciando ejercicio de control del joystick durante {duracion} segundos...")
    try:
        while time.time() - duracion_inicio < duracion:
            # Leer valores del joystick
            x = VRx.read()  # Lee el valor de VRx
            y = VRy.read()  # Lee el valor de VRy

            # Evaluar frecuencia de uso
            if RANGO_IZQUIERDA[0] <= x <= RANGO_IZQUIERDA[1]:  # Movimiento a la izquierda
                movimiento_izquierda += 1
            elif RANGO_DERECHA[0] <= x <= RANGO_DERECHA[1]:  # Movimiento a la derecha
                movimiento_derecha += 1
            elif RANGO_CENTRO[0] <= x <= RANGO_CENTRO[1] and RANGO_CENTRO[0] <= y <= RANGO_CENTRO[1]:
                movimiento_centro += 1  # Contar como movimiento en el centro
            elif RANGO_ABAJO[0] <= y <= RANGO_ABAJO[1]:  # Movimiento hacia abajo
                movimiento_abajo += 1
            elif RANGO_ARRIBA[0] <= y <= RANGO_ARRIBA[1]:  # Movimiento hacia arriba
                movimiento_arriba += 1

            # Calcular la duración de uso
            duracion_uso = time.time() - duracion_inicio
            
            # Mostrar los valores en consola
            print("X:", x, "Y:", y)
            print("Movimiento Izquierda:", movimiento_izquierda, "Movimiento Derecha:", movimiento_derecha)
            print("Movimiento Arriba:", movimiento_arriba, "Movimiento Abajo:", movimiento_abajo)
            print("Movimiento Centro:", movimiento_centro)  # Mostrar conteo de centro
            print("Duración de Uso (s):", round(duracion_uso, 2))

            # Crear el JSON con los datos generados, incluyendo nombre y correo
            data = {
                "Nombre": nombre,
                "Correo": correo,
                "Movimiento_Izquierda": movimiento_izquierda,
                "Movimiento_Derecha": movimiento_derecha,
                "Movimiento_Arriba": movimiento_arriba,
                "Movimiento_Abajo": movimiento_abajo,
                "Movimiento_Centro": movimiento_centro,
                "Duracion_uso": round(duracion_uso, 2)
            }

            # Convertir el JSON en una cadena y enviarlo al servidor
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=ujson.dumps(data), headers=headers)

            # Verificar la respuesta del servidor
            print("Datos enviados:", data)
            print("Respuesta del servidor:", response.text)
            response.close()

            time.sleep(0.5)  # Espera 0.5 segundos antes de la siguiente lectura

        mostrar_resumen()
        
    except KeyboardInterrupt:
        # Finaliza la sesión y muestra un mensaje
        print("Sesión finalizada")
        mostrar_resumen()


def mostrar_resumen():
    print(f"Resumen final:")
    print(f"Movimientos a la izquierda: {movimiento_izquierda}")
    print(f"Movimientos a la derecha: {movimiento_derecha}")
    print(f"Movimientos hacia arriba: {movimiento_arriba}")
    print(f"Movimientos hacia abajo: {movimiento_abajo}")
    print(f"Movimientos en el centro: {movimiento_centro}")
    print(f"Duración de uso total: {round(duracion_uso, 2)} segundos")

# Obtener datos del usuario antes de iniciar
nombre, correo = ingresar_datos_usuario()

# Menú de opciones
while True:
    opcion = mostrar_menu()

    if opcion == '1':
        iniciar_sesion(url, nombre, correo)
    elif opcion == '2':
        duracion = int(input("Ingresa la duración del ejercicio (en segundos): "))
        iniciar_sesion_tiempo(duracion)
    elif opcion == '3':
        print("Saliendo...")
        break
    else:
        print("Opción no válida. Intenta de nuevo.")
