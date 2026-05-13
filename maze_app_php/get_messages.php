<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');
require_once __DIR__ . '/simulation_context.php';

// Estrutura de resposta idêntica ao login.php
$response = array('success' => false, 'message' => '', 'data' => array());

// Usamos $_REQUEST para suportar GET e POST
$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos (username, password, database).';
    echo json_encode($response);
    exit;
}

$host = 'mysql'; // Nome do serviço no docker
$db_user = $username; 
$db_pass = $password;  

// 1. Criar conexão usando mysqli (seguindo a lógica do seu primeiro ficheiro)
$conn = new mysqli($host, $db_user, $db_pass, $database);

// 2. Verificar conexão
if ($conn->connect_error) {
    $response['message'] = "Erro de conexão MySQL: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

$activeSimulationId = getActiveSimulationId($conn, $username);
if ($activeSimulationId === null) {
    $response['success'] = true;
    $response['message'] = 'Sem simulação ativa para este utilizador.';
    $response['active_simulation_id'] = null;
    $response['data'] = array();
    $conn->close();
    echo json_encode($response);
    exit;
}

$stmt = $conn->prepare("SELECT
        ID         AS id,
        TipoAlerta AS tipoalerta,
        Hora       AS hora,
        Msg        AS msg,
        Leitura    AS leitura,
        Sensor     AS sensor,
        Sala       AS sala,
        IDJogo     AS idjogo
        FROM Mensagens
        WHERE is_active = 1
          AND IDJogo = ?
        ORDER BY ID DESC");

if ($stmt) {
    $stmt->bind_param("i", $activeSimulationId);
    $stmt->execute();
    $result = $stmt->get_result();
    $messages = array();
    while ($row = $result->fetch_assoc()) {
        $messages[] = $row;
    }
    
    $response['success'] = true;
    $response['active_simulation_id'] = $activeSimulationId;
    $response['data'] = $messages; // As mensagens vão aqui dentro
    $response['message'] = 'Mensagens carregadas com sucesso.';
    $stmt->close();
} else {
    $response['message'] = 'Erro na preparação da query: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>
