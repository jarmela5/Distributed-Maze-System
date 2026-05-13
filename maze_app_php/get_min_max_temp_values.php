<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

$response = array('success' => false, 'message' => '', 'data' => null);

$username = $_REQUEST['username'] ?? '';
$password = $_REQUEST['password'] ?? '';
$database = $_REQUEST['database'] ?? '';

$host = '194.210.86.10'; // No Docker use o nome do serviço
$username= 'aluno';
$password= 'aluno';
$database= 'maze';


$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    $response['message'] = "Erro de ligação: " . $conn->connect_error;
    echo json_encode($response);
    exit;
}

$stmt = $conn->prepare("SELECT
            normaltemperature,
            temperaturevarhightoleration,
            temperaturevarlowtoleration
        FROM setupmaze
        ORDER BY ID DESC
        LIMIT 1");

if ($stmt) {
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();

    $normalTemperature = ($row && $row['normaltemperature'] !== null) ? (float)$row['normaltemperature'] : 0.0;
    $highToleration = ($row && $row['temperaturevarhightoleration'] !== null) ? (float)$row['temperaturevarhightoleration'] : 10.0;
    $lowToleration = ($row && $row['temperaturevarlowtoleration'] !== null) ? (float)$row['temperaturevarlowtoleration'] : 10.0;

    $response['success'] = true;
    $response['message'] = '';
    $response['data'] = array(
        "minimo" => round($normalTemperature - $lowToleration, 2),
        "maximo" => round($normalTemperature + $highToleration, 2)
    );
    $stmt->close();
} else {
    $response['message'] = "Erro na preparação da query: " . $conn->error;
}

$conn->close();
echo json_encode($response);