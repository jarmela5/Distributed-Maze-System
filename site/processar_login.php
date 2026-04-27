<?php
session_start();
require_once 'config.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $user = $_POST['username'];

    try {
        // procura o utilizador pelo nome
        $stmt = $pdo->prepare("SELECT IDUtilizador, username FROM Utilizador WHERE username = :user");
        $stmt->execute(['user' => $user]);
        $utilizador = $stmt->fetch();

        // verifica se ha utilizador
        if ($utilizador) {

            // guarda dados na sessao
            $_SESSION['IDUtilizador'] = $utilizador['IDUtilizador'];
            $_SESSION['username'] = $utilizador['username'];

            // redireciona para a dashboard
            header("Location: dashboard.php");
            exit();
        } else {

            header("Location: login.php?erro=1");
            exit();
        }

    } catch (PDOException $e) {
        die("Erro ao processar login: " . $e->getMessage());
    }
}
?>