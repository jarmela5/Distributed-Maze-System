<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

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

$sql = "SELECT 
            AVG(so.Som) AS media,
            MAX(c.DefaultNoiseThreshold) AS threshold
        FROM ConfiguracaoSistema c
        LEFT JOIN Som so ON so.is_valid = 1
        WHERE c.is_active = 1";

$result = $conn->query($sql);

if ($result && $row = $result->fetch_assoc()) {
    $media = $row['media'] !== null ? (float)$row['media'] : 0.0;
    $threshold = $row['threshold'] !== null ? (float)$row['threshold'] : 15.0;

    $response['success'] = true;
    $response['message'] = 'Configuração de som carregada.';
    $response['data'] = array(
        // Som só tem limite superior (ruído abaixo da média não é problema)
        "maximo" => round($media + $threshold, 2)
    );
} else {
    $response['message'] = 'Nenhuma configuração de som encontrada.';
}

$conn->close();
echo json_encode($response);
?>