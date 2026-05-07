<?php

function getActiveSimulationId(mysqli $conn, string $username): ?int
{
    // Verificar se é admin
    $sqlTipo = "SELECT Tipo FROM Utilizador WHERE username = ? AND is_active = 1 LIMIT 1";
    $stmt = $conn->prepare($sqlTipo);
    if (!$stmt) return null;
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    $isAdmin = ($row && $row['Tipo'] === 'admin' || $row && $row['Tipo'] === 'android');

    if ($isAdmin) {
        // Admin vê a simulação ativa mais recente de qualquer utilizador
        $sql = "SELECT s.IDSimulacao
                FROM Simulacao s
                WHERE s.is_active = 1
                  AND s.Estado = 'Ativo'
                ORDER BY s.DataHoraInicio DESC, s.IDSimulacao DESC
                LIMIT 1";
        $stmt = $conn->prepare($sql);
        if (!$stmt) return null;
        $stmt->execute();
    } else {
        // Outros utilizadores só veem as suas próprias simulações
        $sql = "SELECT s.IDSimulacao
                FROM Simulacao s
                INNER JOIN Utilizador u ON u.IDUtilizador = s.IDUtilizador
                WHERE s.is_active = 1
                  AND u.is_active = 1
                  AND s.Estado = 'Ativo'
                  AND u.username = ?
                ORDER BY s.DataHoraInicio DESC, s.IDSimulacao DESC
                LIMIT 1";
        $stmt = $conn->prepare($sql);
        if (!$stmt) return null;
        $stmt->bind_param("s", $username);
        $stmt->execute();
    }

    $row = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if (!$row || !isset($row['IDSimulacao'])) return null;

    return (int)$row['IDSimulacao'];
}

?>