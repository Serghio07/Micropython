<?php
// Configuración de conexión a la base de datos
$host = 'localhost'; // Cambia esto por tu host de base de datos
$dbname = 'bd_movilidad'; // Nombre de la base de datos
$username = 'root'; // Usuario de la base de datos (por defecto en XAMPP es 'root')
$password = ''; // Contraseña de la base de datos (por defecto en XAMPP es vacío)

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo 'Error de conexión: ' . $e->getMessage();
    exit();
}

// Obtener los datos JSON enviados desde el Python
$inputData = json_decode(file_get_contents('php://input'), true);

// Extraer los datos recibidos
$movimientoIzquierda = $inputData['Movimiento_Izquierda'];
$movimientoDerecha = $inputData['Movimiento_Derecha'];
$movimientoArriba = $inputData['Movimiento_Arriba'];
$movimientoAbajo = $inputData['Movimiento_Abajo'];
$movimientoCentro = $inputData['Movimiento_Centro'];
$duracionUso = $inputData['Duracion_uso'];
$nombre = $inputData['Nombre'];
$correo = $inputData['Correo'];

// Calcular distancia total y fuerza estimada
$distanciaTotal = $movimientoIzquierda + $movimientoDerecha + $movimientoArriba + $movimientoAbajo + $movimientoCentro;
$fuerzaEstimado = ($distanciaTotal / $duracionUso);  // Fuerza aproximada por distancia/duración

// Categorizar fuerza
if ($fuerzaEstimado > 10) {
    $categoriaFuerza = "Alta";
} elseif ($fuerzaEstimado > 5) {
    $categoriaFuerza = "Media";
} else {
    $categoriaFuerza = "Baja";
}

// Insertar datos en la base de datos para el Usuario (si no existe, lo creamos)
$idUsuario = insertarUsuarioSiNoExiste($nombre, $correo); // Suponiendo que recibes el nombre y correo del usuario en el JSON

// Insertar en la tabla Movilidad
$query = "INSERT INTO Movilidad (id_usuario, Movimiento_Izquierda, Movimiento_Derecha, Movimiento_Arriba, Movimiento_Abajo, Movimiento_Centro, Duracion_uso) 
          VALUES (?, ?, ?, ?, ?, ?, ?)";
$stmt = $pdo->prepare($query);
$stmt->execute([$idUsuario, $movimientoIzquierda, $movimientoDerecha, $movimientoArriba, $movimientoAbajo, $movimientoCentro, $duracionUso]);

// Insertar en la tabla Fuerza
$query = "INSERT INTO Fuerza (id_usuario, fuerza_estimado, categoria_fuerza) 
          VALUES (?, ?, ?)";
$stmt = $pdo->prepare($query);
$stmt->execute([$idUsuario, $fuerzaEstimado, $categoriaFuerza]);

// Calcular promedios y otros valores para estadísticas
$totalSesiones = 1; // Suponiendo que es una nueva sesión
$promedioDuracion = $duracionUso; // Promedio en esta sesión (puedes cambiarlo para calcular el promedio de todas las sesiones)
$distanciaTotalPromedio = $distanciaTotal;

// Insertar en la tabla Estadísticas
$query = "INSERT INTO Estadisticas (id_usuario, promedio_duracion, distancia_total_promedio, total_sesiones, fuerza_categoria) 
          VALUES (?, ?, ?, ?, ?)";
$stmt = $pdo->prepare($query);
$stmt->execute([$idUsuario, $promedioDuracion, $distanciaTotalPromedio, $totalSesiones, $categoriaFuerza]);

echo "Datos insertados correctamente.";

// Función para insertar un nuevo usuario si no existe
function insertarUsuarioSiNoExiste($nombre, $correo) {
    global $pdo;
    
    // Verificar si el usuario ya existe por correo
    $query = "SELECT id_usuario FROM Usuario WHERE correo = ?"; // Comprobar por correo único
    $stmt = $pdo->prepare($query);
    $stmt->execute([$correo]);
    
    if ($stmt->rowCount() > 0) {
        // Si el usuario existe, retorna el ID del usuario
        return $stmt->fetchColumn();
    } else {
        // Si no existe, insertar nuevo usuario con la contraseña constante
        $contrasena = '12345';  // Contraseña constante
        $query = "INSERT INTO Usuario (nombre, correo, contrasena) VALUES (?, ?, ?)";
        $stmt = $pdo->prepare($query);
        $stmt->execute([$nombre, $correo, $contrasena]);
        // Retorna el ID del nuevo usuario
        return $pdo->lastInsertId();
    }
}
?>
