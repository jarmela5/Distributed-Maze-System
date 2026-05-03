<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

$response = array('success' => false, 'message' => '', 'data' => null);

$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

$host = 'mysql'; // No Docker use o nome do serviço

if (empty($username) || empty($password) || empty($database)) {
    $response['message'] = 'Preencha todos os campos.';
    echo json_encode($response);
    exit;
}

$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de ligação: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

$sql = "SELECT 
            AVG(t.Temperatura) AS media,
            MAX(c.DefaultTempThreshold) AS threshold
        FROM ConfiguracaoSistema c
        LEFT JOIN Temperatura t ON t.is_valid = 1
        WHERE c.is_active = 1";

$result = $conn->query($sql);

if ($result && $row = $result->fetch_assoc()) {
    $media = $row['media'] !== null ? (float)$row['media'] : 0.0;
    $threshold = $row['threshold'] !== null ? (float)$row['threshold'] : 10.0;

    $response['success'] = true;
    $response['message'] = '';
    $response['data'] = array(
        "minimo" => round($media - $threshold, 2),
        "maximo" => round($media + $threshold, 2)
    );
} else {
    $response['message'] = "Não foram encontrados limites na tabela.";
}

$conn->close();
echo json_encode($response);