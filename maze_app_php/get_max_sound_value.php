<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');
require_once __DIR__ . '/simulation_context.php';

// Estrutura padrão para o seu Android processar sem erros
$response = array('success' => false, 'message' => '', 'data' => null);

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

// Conexão mysqli
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
    $response['data'] = null;
    $conn->close();
    echo json_encode($response);
    exit;
}

$stmt = $conn->prepare("SELECT
            AVG(so.Som) AS media,
            MAX(COALESCE(s.OutlierNoiseThreshold, c.DefaultNoiseThreshold)) AS threshold
        FROM ConfiguracaoSistema c
        LEFT JOIN Simulacao s ON s.IDSimulacao = ?
        LEFT JOIN Som so ON so.is_valid = 1 AND so.is_active = 1 AND so.IDJogo = ?
        WHERE c.is_active = 1");

if ($stmt) {
    $stmt->bind_param("ii", $activeSimulationId, $activeSimulationId);
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();

    $media = $row['media'] !== null ? (float)$row['media'] : 0.0;
    $threshold = $row['threshold'] !== null ? (float)$row['threshold'] : 15.0;

    $response['success'] = true;
    $response['active_simulation_id'] = $activeSimulationId;
    $response['message'] = 'Configuração de som carregada.';
    $response['data'] = array(
        // Som só tem limite superior (ruído abaixo da média não é problema)
        "maximo" => round($media + $threshold, 2)
    );
    $stmt->close();
} else {
    $response['message'] = 'Erro na preparação da query: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>