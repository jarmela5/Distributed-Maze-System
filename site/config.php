<?php
// Configurações da base de dados
$host = 'mysql';
$dbname = 'maze_local';
$username = 'PedroAdmin';
$password = 'Benfica05'; // No XAMPP por padrão é vazio

try {
    // Cria a conexão PDO
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);

    // Configura o PDO para lançar exceções em caso de erro
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Opcional: Define o modo de busca padrão para objetos ou arrays associativos
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);

} catch (PDOException $e) {
    // Se houver erro, para a execução e mostra a mensagem
    die("Erro na ligação: " . $e->getMessage());
}
?>