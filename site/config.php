<?php


function connectToDatabase($user, $pass) {
    $host = 'mysql';
    $dbname = 'maze_local';

    try {
        // Tenta a ligação com as credenciais recebidas do formulário
        $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);

        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

        return $pdo;

    } catch (PDOException $e) {
        // Se falhar, retorna null (ou podes lançar uma exceção personalizada)
        return null;
    }
}
?>