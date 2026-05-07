<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');
require_once __DIR__ . '/simulation_context.php';

// Estrutura padrão para o Android não crashar
$response = array('success' => false, 'message' => '', 'data' => array());

$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos.';
    echo json_encode($response);
    exit;
}

// Configuração Docker
$host = 'mysql'; 
$db_user = $username; 
$db_pass = $password; 

// Usando mysqli para consistência
$conn = new mysqli($host, $db_user, $db_pass, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão: " . $conn->connect_error;
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
        IDTemperatura AS idtemperatura,
        Temperatura   AS temperatura,
        Hora          AS hora,
        IDJogo        AS idjogo
        FROM Temperatura
        WHERE is_active = 1
          AND is_valid = 1
          AND IDJogo = ?
        ORDER BY IDTemperatura ASC");

if ($stmt) {
    $stmt->bind_param("i", $activeSimulationId);
    $stmt->execute();
    $result = $stmt->get_result();
    $tempData = array();
    while ($row = $result->fetch_assoc()) {
        $tempData[] = $row;
    }

    $response['success'] = true;
    $response['active_simulation_id'] = $activeSimulationId;
    $response['data'] = $tempData;
    $response['message'] = 'Dados de temperatura carregados com sucesso.';
    $stmt->close();
} else {
    $response['message'] = "Erro na preparação da query: " . $conn->error;
}

$conn->close();
echo json_encode($response);
?>