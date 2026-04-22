-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Tempo de geração: 21-Abr-2026 às 12:50
-- Versão do servidor: 8.0.45
-- versão do PHP: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de dados: `maze_local`
--

DELIMITER $$
--
-- Procedimentos
--
CREATE DEFINER=`root`@`%` PROCEDURE `AdicionarUtilizador` (IN `p_Nome` VARCHAR(50), IN `p_Telemovel` VARCHAR(12), IN `p_Tipo` VARCHAR(5), IN `p_Email` VARCHAR(50), IN `p_DataNascimento` DATE, IN `p_Password` VARCHAR(100), IN `p_Username` VARCHAR(50))   BEGIN

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro ao criar utilizador';
    END;

    START TRANSACTION;

    -- verificar se já existe
    IF EXISTS (SELECT 1 FROM Utilizador WHERE Username = p_Username) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Username já existe';
    END IF;

    -- criar utilizador MySQL
    SET @sql = CONCAT(
        'CREATE USER IF NOT EXISTS \'', p_Username, '\'@\'%\' IDENTIFIED BY \'', p_Password, '\''
    );
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- permissões diretas (substitui roles)
    IF LOWER(p_Tipo) = 'admin' THEN

        -- permissões na BD
        SET @sql2 = CONCAT(
            'GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON maze_local.* TO \'', p_Username, '\'@\'%\''
        );

        PREPARE stmt2 FROM @sql2;
        EXECUTE stmt2;
        DEALLOCATE PREPARE stmt2;

        -- permissões globais (CRÍTICO para DROP USER)
        SET @sql3 = CONCAT(
            'GRANT CREATE USER ON *.* TO \'', p_Username, '\'@\'%\''
        );

        PREPARE stmt3 FROM @sql3;
        EXECUTE stmt3;
        DEALLOCATE PREPARE stmt3;

    ELSE

        -- user normal
        SET @sql2 = CONCAT(
            'GRANT SELECT, INSERT, UPDATE, EXECUTE ON maze_local.* TO \'', p_Username, '\'@\'%\''
        );

        PREPARE stmt2 FROM @sql2;
        EXECUTE stmt2;
        DEALLOCATE PREPARE stmt2;

    END IF;

    -- aplicar privilégios
    FLUSH PRIVILEGES;

    -- inserir na tabela
    INSERT INTO Utilizador (Nome, Telemovel, Tipo, Email, DataNascimento, Equipa, Username)
    VALUES (p_Nome, p_Telemovel, p_Tipo, p_Email, p_DataNascimento, 6, p_Username);

    COMMIT;

END$$

CREATE DEFINER=`root`@`%` PROCEDURE `ApagarJogo` (IN `p_idJogo` INT)   BEGIN

    DECLARE v_username VARCHAR(100);
    DECLARE v_idUtilizador INT;
    DECLARE v_owner INT;
    DECLARE v_estado VARCHAR(20);
    DECLARE v_tipo VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro ao apagar jogo';
    END;

    START TRANSACTION;

    -- obter utilizador atual
    SET v_username = SUBSTRING_INDEX(USER(), '@', 1);

    SELECT IDUtilizador, Tipo INTO v_idUtilizador, v_tipo
    FROM Utilizador
    WHERE Username = v_username
    LIMIT 1;

    IF v_idUtilizador IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador inválido';
    END IF;

    -- obter info do jogo
    SELECT IDUtilizador, Estado INTO v_owner, v_estado
    FROM Simulacao
    WHERE IDSimulacao = p_idJogo
    LIMIT 1;

    IF v_owner IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Jogo não existe';
    END IF;

    -- verificar permissões (dono OU admin)
    IF v_owner != v_idUtilizador AND v_tipo != 'admin' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não tens permissão para apagar este jogo';
    END IF;

    -- regra opcional (mantive a tua)
    IF v_estado = 'Ativo' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não é possível apagar um jogo ativo';
    END IF;

    -- apagar
    DELETE FROM Simulacao
    WHERE IDSimulacao = p_idJogo;

    COMMIT;

END$$

CREATE DEFINER=`root`@`%` PROCEDURE `ApagarUtilizador` (IN `p_username` VARCHAR(100))   BEGIN

    DECLARE v_current_user VARCHAR(100);
    DECLARE v_tipo VARCHAR(50);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro ao apagar utilizador';
    END;

    START TRANSACTION;

    -- utilizador atual
    SET v_current_user = SUBSTRING_INDEX(USER(), '@', 1);

    SELECT Tipo INTO v_tipo
    FROM Utilizador
    WHERE Username = v_current_user
    LIMIT 1;

    -- validar admin
    IF v_tipo IS NULL OR LOWER(v_tipo) != 'admin' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Apenas administradores podem apagar utilizadores';
    END IF;

    -- impedir apagar-se a si próprio
    IF v_current_user = p_username THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não podes apagar o teu próprio utilizador';
    END IF;

    -- validar existência
    IF NOT EXISTS (
        SELECT 1 FROM Utilizador WHERE Username = p_username
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador não existe';
    END IF;

    -- primeiro apagar da BD (seguro)
    DELETE FROM Utilizador
    WHERE Username = p_username;

    -- depois apagar user MySQL
    SET @sql = CONCAT('DROP USER IF EXISTS \'', p_username, '\'@\'%\'');
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    COMMIT;

END$$

CREATE DEFINER=`root`@`%` PROCEDURE `CriarJogo` (IN `p_equipa` INT, IN `p_descricao` VARCHAR(100), IN `p_dataHoraInicio` TIMESTAMP, IN `p_estado` VARCHAR(20), OUT `p_idJogo` INT)   BEGIN

    DECLARE v_username VARCHAR(100);
    DECLARE v_idUtilizador INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro ao criar jogo';
    END;

    START TRANSACTION;

    -- normalizar timestamp
    SET p_dataHoraInicio = COALESCE(p_dataHoraInicio, NOW());

    -- obter username do MySQL
    SET v_username = SUBSTRING_INDEX(USER(), '@', 1);

    -- obter ID do utilizador
    SELECT IDUtilizador INTO v_idUtilizador
    FROM Utilizador
    WHERE username = v_username
    LIMIT 1;

    IF v_idUtilizador IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador não registado na aplicação';
    END IF;

    -- validar timestamp duplicado
    IF EXISTS (
        SELECT 1 FROM Simulacao
        WHERE DataHoraInicio = p_dataHoraInicio
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Já existe uma simulação com este timestamp';
    END IF;

    -- insert
    INSERT INTO Simulacao (
        Descricao,
        Equipa,
        DataHoraInicio,
        Estado,
        IDUtilizador
    )
    VALUES (
        p_descricao,
        p_equipa,
        p_dataHoraInicio,
        COALESCE(p_estado, 'Ativo'),
        v_idUtilizador
    );

    SET p_idJogo = LAST_INSERT_ID();

    COMMIT;

END$$

CREATE DEFINER=`root`@`%` PROCEDURE `EditarJogo` (IN `p_idJogo` INT, IN `p_descricao` VARCHAR(100), IN `p_dataHoraInicio` TIMESTAMP, IN `p_estado` VARCHAR(20))   BEGIN

    DECLARE v_username VARCHAR(100);
    DECLARE v_idUtilizador INT;
    DECLARE v_owner INT;
    DECLARE v_tipo VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro ao editar jogo';
    END;

    START TRANSACTION;

    -- obter utilizador atual
    SET v_username = SUBSTRING_INDEX(USER(), '@', 1);

    SELECT IDUtilizador, Tipo INTO v_idUtilizador, v_tipo
    FROM Utilizador
    WHERE Username = v_username
    LIMIT 1;

    IF v_idUtilizador IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador inválido';
    END IF;

    -- obter dono do jogo
    SELECT IDUtilizador INTO v_owner
    FROM Simulacao
    WHERE IDSimulacao = p_idJogo
    LIMIT 1;

    IF v_owner IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Jogo não existe';
    END IF;

    -- verificar permissões (dono OU admin)
    IF v_owner != v_idUtilizador AND v_tipo != 'admin' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não tens permissão para editar este jogo';
    END IF;

    -- validar timestamp duplicado (se fornecido)
    IF p_dataHoraInicio IS NOT NULL AND EXISTS (
        SELECT 1 FROM Simulacao
        WHERE DataHoraInicio = p_dataHoraInicio
          AND IDSimulacao != p_idJogo
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Já existe uma simulação com este timestamp';
    END IF;

    -- update
    UPDATE Simulacao
    SET
        Descricao = COALESCE(NULLIF(p_descricao, ''), Descricao),
        DataHoraInicio = COALESCE(p_dataHoraInicio, DataHoraInicio),
        Estado = COALESCE(NULLIF(p_estado, ''), Estado)
    WHERE IDSimulacao = p_idJogo;

    COMMIT;

END$$

CREATE DEFINER=`root`@`%` PROCEDURE `EditarUtilizador` (IN `p_Nome` VARCHAR(50), IN `p_Telemovel` VARCHAR(12), IN `p_Tipo` VARCHAR(5), IN `p_Email` VARCHAR(50), IN `p_DataNascimento` DATE, IN `p_Username` VARCHAR(50))   BEGIN

    DECLARE v_tipo VARCHAR(50);
    DECLARE v_current_user VARCHAR(100);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro ao alterar utilizador';
    END;

    START TRANSACTION;

    SET v_current_user = SUBSTRING_INDEX(USER(), '@', 1);

    SELECT Tipo INTO v_tipo
    FROM Utilizador
    WHERE Username = v_current_user
    LIMIT 1;

    IF v_tipo IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador atual inválido';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM Utilizador WHERE Username = p_Username
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador não existe';
    END IF;

    IF v_current_user = p_Username OR LOWER(v_tipo) = 'admin' THEN

        UPDATE Utilizador
        SET
            Nome = COALESCE(NULLIF(p_Nome, ''), Nome),
            Telemovel = COALESCE(NULLIF(p_Telemovel, ''), Telemovel),
            Tipo = CASE 
                      WHEN LOWER(v_tipo) = 'admin' 
                      THEN COALESCE(NULLIF(p_Tipo, ''), Tipo) 
                      ELSE Tipo 
                   END,
            Email = COALESCE(NULLIF(p_Email, ''), Email),
            DataNascimento = COALESCE(p_DataNascimento, DataNascimento)
        WHERE Username = p_Username;

    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não tens permissão para editar este utilizador';
    END IF;

    COMMIT;

END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estrutura da tabela `MedicoesPassagens`
--

CREATE TABLE `MedicoesPassagens` (
  `IDMedicao` int NOT NULL,
  `seq` bigint NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `SalaOrigem` int DEFAULT NULL,
  `SalaDestino` int DEFAULT NULL,
  `Marsami` int DEFAULT NULL,
  `Status` int DEFAULT NULL,
  `IDJogo` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Mensagens`
--

CREATE TABLE `Mensagens` (
  `ID` bigint NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `Sala` int DEFAULT NULL,
  `Sensor` varchar(10) DEFAULT NULL,
  `Leitura` decimal(6,2) DEFAULT NULL,
  `TipoAlerta` varchar(50) DEFAULT NULL,
  `Msg` varchar(100) DEFAULT NULL,
  `HoraEscrita` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `IDJogo` int NOT NULL,
  `seq` bigint NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `OcupacaoLabirinto`
--

CREATE TABLE `OcupacaoLabirinto` (
  `IDJogo` int NOT NULL,
  `Sala` int NOT NULL,
  `NumeroMarsamisOdd` int DEFAULT '0',
  `NumeroMarsamisEven` int DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Simulacao`
--

CREATE TABLE `Simulacao` (
  `IDSimulacao` int NOT NULL,
  `Descricao` text,
  `Equipa` int NOT NULL,
  `DataHoraInicio` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `Estado` varchar(20) DEFAULT 'Ativo',
  `IDUtilizador` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `OutlierTempThreshold` DECIMAL(6,2) NOT NULL,
  `OutlierNoiseThreshold` DECIMAL(6,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Som`
--

CREATE TABLE `Som` (
  `IDSom` int NOT NULL,
  `seq` bigint NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `Som` decimal(6,2) DEFAULT NULL,
  `IDJogo` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_valid` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Temperatura`
--

CREATE TABLE `Temperatura` (
  `IDTemperatura` int NOT NULL,
  `seq` bigint NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `Temperatura` decimal(6,2) DEFAULT NULL,
  `IDJogo` int NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_valid` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Utilizador`
--

-- MUDAR O TIPO PARA ENUM
CREATE TABLE `Utilizador` (
  `IDUtilizador` int NOT NULL,
  `Nome` varchar(100) NOT NULL,
  `Telemovel` varchar(12) DEFAULT NULL,
  `Tipo` varchar(10) DEFAULT NULL,  
  `Email` varchar(50) DEFAULT NULL,
  `DataNascimento` date DEFAULT NULL,
  `Equipa` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Extraindo dados da tabela `Utilizador`
--

INSERT INTO `Utilizador` (`IDUtilizador`, `Nome`, `Telemovel`, `Tipo`, `Email`, `DataNascimento`, `Equipa`, `username`, `is_active`) VALUES
(16, 'admin', '999999999', 'admin', 'admin@email.pt', '1999-01-01', 6, 'admin', 0),
(18, 'maria', '123456789', 'user', 'maria@email.pt', '1999-01-01', 6, 'maria', 0);

-- --------------------------------------------------------

--
-- Estrutura da tabela `ConfiguracaoSistema`
--

CREATE TABLE `ConfiguracaoSistema` (
    `ID` INT PRIMARY KEY AUTO_INCREMENT,
    `DefaultTempThreshold` DECIMAL(6,2) NOT NULL,
    `DefaultNoiseThreshold` DECIMAL(6,2) NOT NULL,
    `DataAtualizacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO ConfiguracaoSistema (DefaultTempThreshold, DefaultNoiseThreshold)
VALUES (2.5, 5.0);

--
-- Índices para tabelas despejadas
--

--
-- Índices para tabela `MedicoesPassagens`
--
ALTER TABLE `MedicoesPassagens`
  ADD PRIMARY KEY (`IDMedicao`),
  ADD UNIQUE KEY `uq_medicoes_seq_jogo` (`seq`,`IDJogo`),
  ADD KEY `IDJogo` (`IDJogo`);

--
-- Índices para tabela `Mensagens`
--
ALTER TABLE `Mensagens`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `uq_mensagens_seq_jogo` (`seq`,`IDJogo`),
  ADD KEY `IDJogo` (`IDJogo`);

--
-- Índices para tabela `OcupacaoLabirinto`
--
ALTER TABLE `OcupacaoLabirinto`
  ADD PRIMARY KEY (`IDJogo`,`Sala`);

--
-- Índices para tabela `Simulacao`
--
ALTER TABLE `Simulacao`
  ADD PRIMARY KEY (`IDSimulacao`),
  ADD KEY `simulacao_ibfk_1` (`IDUtilizador`);

--
-- Índices para tabela `Som`
--
ALTER TABLE `Som`
  ADD PRIMARY KEY (`IDSom`),
  ADD UNIQUE KEY `uq_som_seq_jogo` (`seq`,`IDJogo`),
  ADD KEY `IDJogo` (`IDJogo`);

--
-- Índices para tabela `Temperatura`
--
ALTER TABLE `Temperatura`
  ADD PRIMARY KEY (`IDTemperatura`),
  ADD UNIQUE KEY `uq_temperatura_seq_jogo` (`seq`,`IDJogo`),
  ADD KEY `IDJogo` (`IDJogo`);

--
-- Índices para tabela `Utilizador`
--
ALTER TABLE `Utilizador`
  ADD PRIMARY KEY (`IDUtilizador`);

--
-- AUTO_INCREMENT de tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `MedicoesPassagens`
--
ALTER TABLE `MedicoesPassagens`
  MODIFY `IDMedicao` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `Mensagens`
--
ALTER TABLE `Mensagens`
  MODIFY `ID` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `Simulacao`
--
ALTER TABLE `Simulacao`
  MODIFY `IDSimulacao` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de tabela `Som`
--
ALTER TABLE `Som`
  MODIFY `IDSom` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `Temperatura`
--
ALTER TABLE `Temperatura`
  MODIFY `IDTemperatura` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `Utilizador`
--
ALTER TABLE `Utilizador`
  MODIFY `IDUtilizador` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Restrições para despejos de tabelas
--

--
-- Limitadores para a tabela `MedicoesPassagens`
--
ALTER TABLE `MedicoesPassagens`
  ADD CONSTRAINT `medicoespassagens_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `Simulacao` (`IDSimulacao`) ON DELETE CASCADE;

--
-- Limitadores para a tabela `Mensagens`
--
ALTER TABLE `Mensagens`
  ADD CONSTRAINT `mensagens_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `Simulacao` (`IDSimulacao`) ON DELETE CASCADE;

--
-- Limitadores para a tabela `OcupacaoLabirinto`
--
ALTER TABLE `OcupacaoLabirinto`
  ADD CONSTRAINT `ocupacaolabirinto_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `Simulacao` (`IDSimulacao`) ON DELETE CASCADE;

--
-- Limitadores para a tabela `Simulacao`
--
ALTER TABLE `Simulacao`
  ADD CONSTRAINT `simulacao_ibfk_1` FOREIGN KEY (`IDUtilizador`) REFERENCES `Utilizador` (`IDUtilizador`) ON DELETE CASCADE ON UPDATE RESTRICT;

--
-- Limitadores para a tabela `Som`
--
ALTER TABLE `Som`
  ADD CONSTRAINT `som_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `Simulacao` (`IDSimulacao`) ON DELETE CASCADE;

--
-- Limitadores para a tabela `Temperatura`
--
ALTER TABLE `Temperatura`
  ADD CONSTRAINT `temperatura_ibfk_1` FOREIGN KEY (`IDJogo`) REFERENCES `Simulacao` (`IDSimulacao`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
