<?php
session_start();

if (!isset($_SESSION['IDUtilizador'])) {
    header("Location: login.php");
    exit();
}


$username = $_SESSION['username'];
?>

<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Painel</title>

<style>

body{
    margin:0;
    font-family:Arial, Helvetica, sans-serif;
    display:flex;
}

/* Sidebar */

.sidebar{
    width:220px;
    background:#2c3e50;
    height:100vh;
    color:white;
    padding:20px;
}

.sidebar h2{
    margin-top:0;
}

.sidebar a{
    display:block;
    color:white;
    text-decoration:none;
    margin:15px 0;
}

.sidebar a:hover{
    color:#1abc9c;
}

/* Conteúdo principal */

.main{
    flex:1;
    background:#f4f6f7;
}

/* Barra superior */

.topbar{
    background:white;
    padding:15px 25px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    box-shadow:0px 2px 5px rgba(0,0,0,0.1);
}

.username{
    font-weight:bold;
}

/* Área de conteúdo */

.content{
    padding:25px;
}

.card{
    background:white;
    padding:20px;
    border-radius:8px;
    box-shadow:0px 0px 8px rgba(0,0,0,0.08);
    width:300px;
}

</style>

</head>

<body>



    <div class="sidebar">
        <h2>Menu</h2>
        <a href="#"><strong>Dashboard</strong></a>
        <a href="simulacao.php">Os seus jogos</a>
        <a href="criarJogo.php">Criar jogo</a>
        <a href="logout.php">Logout</a>
    </div>

<div class="main">

    <div class="topbar">
        <div><strong>Painel Principal</strong></div>
        <div class="username">
            Utilizador: <span id="username"><?php echo $username ?></span>
        </div>
    </div>

    <div class="content">

        <div class="card">
            <h3>Bem vindo <?php echo $username ?>!</h3>
            <p>Estás autenticado.</p>
        </div>



    </div>

</div>

</body>
</html>