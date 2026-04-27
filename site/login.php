
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="login-box">
        <h2>Login</h2>

        <?php
        // erro se nao ha credenciais correspondentes na bd
        if (isset($_GET['erro'])) {
            echo '<p style="color:red; text-align:center;">Utilizador ou senha incorretos!</p>';
        }
        ?>

        <form action="processar_login.php" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>