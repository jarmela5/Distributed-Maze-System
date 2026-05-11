<?php
session_start();
require_once 'config.php';

// 1. Verificar se o utilizador tem sessão iniciada
if (!isset($_SESSION['IDUtilizador']) || !isset($_SESSION['mysql_user']) || !isset($_SESSION['mysql_pass'])) {
    header("Location: login.php");
    exit();
}

$IDUtilizador = $_SESSION['IDUtilizador'];
$username = $_SESSION['username'];

// 2. IMPORTANTE: Criar a ligação $pdo nesta página usando os dados da sessão
$pdo = connectToDatabase($_SESSION['mysql_user'], $_SESSION['mysql_pass']);

if (!$pdo) {
    die("Erro ao ligar à base de dados. Por favor, faça login novamente.");
}


// procurar equipa do user
try {
    $sqlUser = "SELECT Equipa FROM Utilizador WHERE IDUtilizador = :id";
    $stmtUser = $pdo->prepare($sqlUser);
    $stmtUser->execute([':id' => $IDUtilizador]);

    $userData = $stmtUser->fetch();

    if (!$userData) {
        die("Utilizador não encontrado.");
    }

    $equipa = $userData['Equipa'];

} catch (PDOException $e) {
    die("Erro ao buscar equipa: " . $e->getMessage());
}

//formulario
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['btn_criar'])) {

    $descricao = trim($_POST['descricao']);
    $temp = !empty($_POST['temp_max']) ? $_POST['temp_max'] : null;
    $som  = !empty($_POST['som_max'])  ? $_POST['som_max']  : null;

    try {
        $sql = "CALL CriarJogo(:equipa, :desc, NOW(), 'iniciada', :temp_max, :som_max, @p_idJogo)";

        $stmt = $pdo->prepare($sql);

        $stmt->bindParam(':equipa',   $equipa,    PDO::PARAM_STR);
        $stmt->bindParam(':desc',     $descricao, PDO::PARAM_STR);
        $stmt->bindParam(':temp_max', $temp,      PDO::PARAM_INT);
        $stmt->bindParam(':som_max',  $som,       PDO::PARAM_INT);

        $stmt->execute();

        header("Location: dashboard.php?sucesso=1");
        exit();

    } catch (PDOException $e) {
        $erro_msg = "Erro ao criar jogo: " . $e->getMessage();
    }

}
try {
    $sqlConfig = "SELECT DefaultTempThreshold, DefaultNoiseThreshold FROM ConfiguracaoSistema LIMIT 1";
    $stmtConfig = $pdo->query($sqlConfig);
    $config = $stmtConfig->fetch();

    $defaultTemp = $config['DefaultTempThreshold'] ?? '';
    $defaultNoise = $config['DefaultNoiseThreshold'] ?? '';

} catch (PDOException $e) {
    $defaultTemp = '';
    $defaultNoise = '';
}
?>
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Criar Novo Jogo</title>

<style>

*{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body, html{
    width: 100%;
    height: 100%;
    font-family: Arial, Helvetica, sans-serif;
}

/* Container principal ocupando toda a página */
.container{
    display: flex;
    width: 100%;
    height: 100%;
    background: #f4f6f7;
}

/* Sidebar */
.sidebar{
    width: 220px;
    background: #2c3e50;
    color: white;
    padding: 20px;
}

.sidebar a{
    display: block;
    color: white;
    text-decoration: none;
    margin: 15px 0;
}

.sidebar a:hover{
    color: #1abc9c;
}

.main{
    flex: 1;
    display: flex;
    flex-direction: column;
}

.topbar{
    background: white;
    padding: 15px 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}

/* Área do formulário ocupa toda a tela disponível */
.content{
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Formulário ocupa grande parte da tela */
.form-card{
    background: white;
    padding: 30px;
    width: 70%;
    max-width: 600px;
    border-radius: 8px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
}

.form-card h2{
    margin-bottom: 20px;
}

label{
    display: block;
    margin-top: 15px;
    font-weight: bold;
}

input, textarea{
    width: 100%;
    padding: 10px;
    margin-top: 5px;
}

textarea{
    resize: vertical;
}

.buttons{
    margin-top: 25px;
    display: flex;
    gap: 10px;
}

button{
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.btn-create{
    background: #2ecc71;
    color: white;
}

.btn-cancel{
    background: #e74c3c;
    color: white;
}

button:hover{
    opacity: 0.85;
}

</style>
</head>

<body>

<div class="container">
    <div class="sidebar">
        <h2>Menu</h2>
        <a href="dashboard.php">Dashboard</a>
        <a href="simulacao.php">Os seus jogos</a>
        <a href="#"><strong>Criar jogo</strong></a>
        <a href="logout.php">Logout</a>
    </div>

    <div class="main">
        <div class="topbar">
            <div><strong>Criar Novo Jogo</strong></div>
            <div>Utilizador: <?php echo htmlspecialchars($username); ?></div>
        </div>

        <div class="content">
            <div class="form-card">
                <h2>Novo jogo</h2>

                <?php if(isset($erro_msg)) echo "<p style='color:red'>$erro_msg</p>"; ?>

                <form method="POST" action="">

                    <label>Descrição</label>
                    <textarea name="descricao" rows="4" placeholder="Descrição do jogo" required></textarea>

                    <label>Variação máxima de Temperatura (°C)</label>
                    <input type="number" name="temp_max" placeholder="Ex: 5" value="<?php echo htmlspecialchars($defaultTemp); ?>">

                    <label>Variação máxima de Som (dB)</label>
                    <input type="number" name="som_max" placeholder="Ex: 10" value="<?php echo htmlspecialchars($defaultNoise); ?>">

                    <div class="buttons">
                        <button type="submit" name="btn_criar" class="btn-create">Criar jogo</button>
                        <button class="btn-cancel" type="button" onclick="window.location.href='dashboard.php'">Cancelar</button>
                    </div>

                </form>
            </div>
        </div>
    </div>
</div>

</body>
</html>