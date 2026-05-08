<?php
session_start();
require_once 'config.php';

if (!isset($_SESSION['IDUtilizador'])) {
    http_response_code(401);
    echo json_encode(['erro' => 'Não autenticado']);
    exit();
}

$_SESSION = array();


if (ini_get("session.use_cookies")) {
    $params = session_get_cookie_params();
    setcookie(session_name(), '', time() - 42000,
        $params["path"], $params["domain"],
        $params["secure"], $params["httponly"]
    );
}


session_destroy();

//redirecionar
header("Location: login.php");
exit();
?>