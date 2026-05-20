<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: application/json');

require_once __DIR__ . '/db.php';

$response = ['success' => false, 'message' => '', 'data' => null];
$conn = getConnection();

$stmt = $conn->prepare("SELECT normaltemperature, temperaturevarhightoleration, temperaturevarlowtoleration FROM setupmaze ORDER BY ID DESC LIMIT 1");

if ($stmt) {
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();

    $normalTemperature = (float)($row['normaltemperature']            ?? 0.0);
    $highToleration    = (float)($row['temperaturevarhightoleration'] ?? 10.0);
    $lowToleration     = (float)($row['temperaturevarlowtoleration']  ?? 10.0);

    $response['success'] = true;
    $response['message'] = '';
    $response['data']    = [
        'minimo' => round($normalTemperature - $lowToleration, 2),
        'maximo' => round($normalTemperature + $highToleration, 2)
    ];
    $stmt->close();
} else {
    $response['message'] = 'Erro na preparação da query: ' . $conn->error;
}

$conn->close();
echo json_encode($response);