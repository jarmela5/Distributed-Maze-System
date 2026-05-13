<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');
require_once __DIR__ . '/simulation_context.php';

$response = array('success' => false, 'message' => '');

// Usamos $_REQUEST para aceitar tanto GET (browser) quanto POST (Android)
$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos (username, password, database).';
    echo json_encode($response);
    exit;
}

$host = 'mysql'; // Nome do serviço no docker-compose
$db_user = $username;
$db_pass = $password;

// 1. Criar conexão
$conn = new mysqli($host, $db_user, $db_pass, $database);

// 2. Verificar conexão
if ($conn->connect_error) {
    $response['message'] = "Erro de conexão MySQL: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

// 3. Consulta ao utilizador aplicacional já autenticado no MySQL
$sql = "SELECT Equipa, Tipo FROM Utilizador WHERE username = ? AND is_active = 1 LIMIT 1";
$stmt = $conn->prepare($sql);

if ($stmt) {
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();

    if ($user) {
        $activeSimulationId = getActiveSimulationId($conn, $username);
        $response['success'] = true;
        $response['IDGrupo'] = (int)$user['Equipa'];
        $response['tipo'] = $user['Tipo'];
        $response['active_simulation_id'] = $activeSimulationId;
        $response['message'] = 'Login bem-sucedido.';
    } else {
        $response['message'] = 'Utilizador não encontrado na tabela Utilizador.';
    }
    $stmt->close();
} else {
    $response['message'] = 'Erro na preparação da query: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>