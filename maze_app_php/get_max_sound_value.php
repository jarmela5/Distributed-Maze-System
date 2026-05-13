<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

// Estrutura padrão para o seu Android processar sem erros
$response = array('success' => false, 'message' => '', 'data' => null);

$host = '194.210.86.10'; 
$username= 'aluno';
$password= 'aluno';
$database= 'maze';

// Conexão mysqli
$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de conexão: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

$stmt = $conn->prepare("SELECT
            normalnoise,
            noisevartoleration
        FROM setupmaze
        ORDER BY ID DESC
        LIMIT 1");

if ($stmt) {
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();

    $normalNoise = ($row && $row['normalnoise'] !== null) ? (float)$row['normalnoise'] : 0.0;
    $noiseVarToleration = ($row && $row['noisevartoleration'] !== null) ? (float)$row['noisevartoleration'] : 15.0;

    $response['success'] = true;
    $response['message'] = 'Configuração de som carregada.';
    $response['data'] = array(
        "maximo" => round($normalNoise + $noiseVarToleration, 2)
    );
    $stmt->close();
} else {
    $response['message'] = 'Erro na preparação da query: ' . $conn->error;
}

$conn->close();
echo json_encode($response);
?>