<?php
session_start();
require_once 'config.php'; // Garante que este ficheiro só tem a função connectToDatabase

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $inputUser = $_POST['username'];
    $inputPass = $_POST['password'];

    // Tenta ligar ao MySQL com os dados do formulário
    $pdo = connectToDatabase($inputUser, $inputPass);

    if ($pdo) {
        try {
            // Procura o ID desse utilizador na tabela
            $sql = "SELECT IDUtilizador FROM maze_local.Utilizador WHERE username = :user LIMIT 1";
            $stmt = $pdo->prepare($sql);
            $stmt->execute(['user' => $inputUser]);
            $resultado = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($resultado) {
                // Login completo: MySQL aceitou e utilizador existe na tabela
                $_SESSION['IDUtilizador'] = $resultado['IDUtilizador'];
                $_SESSION['username'] = $inputUser;
                $_SESSION['mysql_user'] = $inputUser;
                $_SESSION['mysql_pass'] = $inputPass;

                header("Location: dashboard.php");
                exit();
            } else {
                // MySQL aceitou, mas o nome não existe na tabela 'Utilizador'
                header("Location: login.php?erro=tabela");
                exit();
            }
        } catch (PDOException $e) {
            // Erro de SQL (ex: tabela não existe)
            header("Location: login.php?erro=db");
            exit();
        }
    } else {
        // O MySQL rejeitou o Username/Password
        header("Location: login.php?erro=1");
        exit();
    }
} else {
    header("Location: login.php");
    exit();
}