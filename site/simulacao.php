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

// 3. Agora a variável $pdo já existe e podes fazer o prepare
try {
    $stmt = $pdo->prepare("SELECT IDSimulacao, Descricao, DataHoraInicio, Estado, is_active, var_temp, var_som
                           FROM maze_local.simulacao
                           WHERE IDUtilizador = :IDUtilizador AND is_active=1
                           ORDER BY DataHoraInicio DESC");
    $stmt->execute(['IDUtilizador' => $IDUtilizador]);
    $simulacoes = $stmt->fetchAll();
} catch (PDOException $e) {
    die("Erro ao carregar jogos: " . $e->getMessage());
}

if (isset($_GET['eliminar'])) {
    $id_a_eliminar = $_GET['eliminar'];

    try {
        // Preparamos o update para desativar, garantindo que pertence ao utilizador logado
        $stmt_del = $pdo->prepare("UPDATE simulacao SET is_active = 0 WHERE IDSimulacao = :id AND IDUtilizador = :user_id");
        $stmt_del->execute([
            'id' => $id_a_eliminar,
            'user_id' => $IDUtilizador
        ]);

        // Redireciona para limpar o URL e atualizar a lista
        header("Location: simulacao.php");
        exit();
    } catch (PDOException $e) {
        die("Erro ao eliminar: " . $e->getMessage());
    }
}
?>
<!DOCTYPE html>
<html lang="pt">
<head>
    <link rel="stylesheet" href="styles.css">
    <meta charset="UTF-8">
    <title>Painel - Os seus jogos</title>
</head>
<body>

<div class="sidebar">
    <h2>Menu</h2>
    <a href="dashboard.php">Dashboard</a>
    <a href="simulacao.php"><strong>Os seus jogos</strong></a>
    <a href="criarJogo.php">Criar jogo</a>
    <a href="logout.php">Logout</a>
</div>

<div class="main">
    <div class="topbar">
        <div><strong>Painel</strong></div>
        <div class="username">Utilizador: <?php echo htmlspecialchars($username); ?></div>
    </div>

    <div class="content">
        <h2>Os seus jogos</h2>
        <table id="tabelaJogos">
            <thead>
                <tr>
                    <th>ID Simulacao</th>
                    <th>Descrição</th>
                    <th>Data</th>
                    <th>Estado</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                <?php if (count($simulacoes) > 0): ?>
                    <?php foreach ($simulacoes as $jogo): ?>
                        <tr>
                            <td><?php echo $jogo['IDSimulacao']; ?></td>
                            <td><?php echo htmlspecialchars($jogo['Descricao']); ?></td>
                            <td><?php echo date('d/m/Y - H:i', strtotime($jogo['DataHoraInicio'])); ?></td>
                            <td class="status-<?php echo strtolower($jogo['Estado']); ?>">
                                <?php echo $jogo['Estado']; ?>
                            </td>
                            <td>
                                <button class="btn-edit"
                                        data-id="<?php echo $jogo['IDSimulacao']; ?>"
                                        data-desc="<?php echo htmlspecialchars($jogo['Descricao']); ?>"
                                        data-temp="<?php echo $jogo['var_temp']; ?>"
                                        data-som="<?php echo $jogo['var_som']; ?>"
                                        data-estado="<?php echo $jogo['Estado']; ?>">
                                    Editar
                                </button>
                                <button class="btn-cancel"
                                    onclick="confirmarEliminar(<?php echo $jogo['IDSimulacao']; ?>)">
                                    Eliminar
                                </button>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr>
                        <td colspan="5" style="text-align:center;">Ainda não criou nenhum jogo.</td>
                    </tr>
                <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>

<div id="editModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Editar Jogo</h3>
            <span class="close">&times;</span>
        </div>

        <div class="aviso-concluido" id="avisoConcluido" style="display:none; color: red; margin-bottom: 10px;">
            Simulação concluída — apenas a descrição pode ser alterada.
        </div>

        <div class="campo">
            <label>Descrição</label>
            <textarea id="descricaoJogo" rows="4" style="width:100%"></textarea>
        </div>

        <div class="campo">
            <label id="labelVarTemp">Variação máxima de Temperatura (°C)</label>
            <input type="number" id="varTemp" style="width:100%">
        </div>

        <div class="campo">
            <label id="labelVarSom">Variação máxima de Som (dB)</label>
            <input type="number" id="varSom" style="width:100%">
        </div>

        <div class="modal-acoes" style="margin-top: 20px;">
            <button class="btn-secundario" id="btnCancelarModal">Cancelar</button>
            <button class="btn-primario" id="btnGuardar">Guardar</button>
        </div>
    </div>
</div>

<script>
const modal = document.getElementById("editModal");
const avisoConcluido = document.getElementById("avisoConcluido");
const campoTemp = document.getElementById("varTemp");
const campoSom = document.getElementById("varSom");
const closeBtn = document.querySelector(".close");

function abrirModal(concluido) {
    campoTemp.disabled = concluido;
    campoSom.disabled = concluido;
    avisoConcluido.style.display = concluido ? "block" : "none";
    modal.classList.add("active");
}

function fecharModal() {
    modal.classList.remove("active");
}

let jogoIdAtual = null;

document.querySelectorAll(".btn-edit").forEach((btn) => {
    btn.addEventListener("click", function () {
        jogoIdAtual = this.getAttribute("data-id"); // guarda o ID
        const desc   = this.getAttribute("data-desc");
        const temp   = this.getAttribute("data-temp");
        const som    = this.getAttribute("data-som");
        const estado = this.getAttribute("data-estado");

        document.getElementById("descricaoJogo").value = desc;
        campoTemp.value = temp;
        campoSom.value  = som;

        const concluido = (estado.toLowerCase() === "concluído" || estado.toLowerCase() === "concluido");
        abrirModal(concluido);
    });
});

document.getElementById("btnGuardar").addEventListener("click", function () {
    const descricao = document.getElementById("descricaoJogo").value;
    const estado    = "";

    fetch("editarJogo.php", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `idJogo=${jogoIdAtual}&descricao=${encodeURIComponent(descricao)}&estado=${encodeURIComponent(estado)}`
    })
    .then(r => r.json())
    .then(data => {
        if (data.sucesso) {
            fecharModal();
            location.reload();
        } else {
            alert("Erro: " + data.erro);
        }
    })
    .catch(() => alert("Erro de ligação ao servidor."));
});


if(closeBtn) closeBtn.onclick = fecharModal;
document.getElementById("btnCancelarModal").onclick = fecharModal;

window.onclick = function(event) {
    if (event.target == modal) fecharModal();
}
function confirmarEliminar(id) {
    if (confirm("Tem a certeza que deseja eliminar esta simulação?")) {
        window.location.href = "simulacao.php?eliminar=" + id;
    }
}
</script>

</body>
</html>