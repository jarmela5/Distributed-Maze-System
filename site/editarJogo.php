<?php
session_start();
require_once 'config.php';

if (!isset($_SESSION['IDUtilizador'])) {
    http_response_code(401);
    echo json_encode(['erro' => 'Não autenticado']);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $idJogo    = $_POST['idJogo']    ?? null;
    $descricao = $_POST['descricao'] ?? '';
    $estado    = $_POST['estado']    ?? '';

    if (!$idJogo) {
        echo json_encode(['erro' => 'ID do jogo em falta']);
        exit();
    }

    try {
        $stmt = $pdo->prepare("CALL EditarJogo(:idJogo, :descricao, NULL, :estado)");
        $stmt->execute([
            ':idJogo'    => $idJogo,
            ':descricao' => $descricao,
            ':estado'    => $estado,
        ]);

        echo json_encode(['sucesso' => true]);
    } catch (PDOException $e) {
        echo json_encode(['erro' => $e->getMessage()]);
    }
}
?>