<?php
session_start();
require_once 'config.php'; /

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $inputUser = $_POST['username'];
    $inputPass = $_POST['password'];


    $pdo = connectToDatabase($inputUser, $inputPass);

    if ($pdo) {
        try {
            // Procura o ID desse utilizador na tabela
            $sql = "SELECT IDUtilizador FROM maze_local.Utilizador WHERE username = :user LIMIT 1";
            $stmt = $pdo->prepare($sql);
            $stmt->execute(['user' => $inputUser]);
            $resultado = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($resultado) {

                $_SESSION['IDUtilizador'] = $resultado['IDUtilizador'];
                $_SESSION['username'] = $inputUser;
                $_SESSION['mysql_user'] = $inputUser;
                $_SESSION['mysql_pass'] = $inputPass;

                header("Location: dashboard.php");
                exit();
            } else {

                header("Location: login.php?erro=tabela");
                exit();
            }
        } catch (PDOException $e) {

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