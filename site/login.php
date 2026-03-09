<?php

session_start();

//nome do container da base de dados
$host = "mysql";
$user = "root";
$password = "root";
$database = "maze_local";

$conn = new mysqli($host, $user, $password, $database);

if ($conn->connect_error) {
    die("Erro na ligação: " . $conn->connect_error);
}


$email = $_POST['email'];
$password = md5($_POST['password']);


$sql = "SELECT * FROM Utilizador WHERE Email='$email' AND password='$password' AND Tipo='user'";

$result = $conn->query($sql);


if ($result->num_rows == 1) {

    $_SESSION['email'] = $email;

    header("Location: dashboard.php");
    exit();

} else {

    echo "Login inválido";

}

$conn->close();

?>
