DELIMITER $$
CREATE DEFINER=`root`@`%` PROCEDURE `AdicionarUtilizador`(IN `p_Nome` VARCHAR(50), IN `p_Telemovel` VARCHAR(12), IN `p_Tipo` VARCHAR(5), IN `p_Email` VARCHAR(50), IN `p_DataNascimento` DATE, IN `p_Password` VARCHAR(100), IN `p_Username` VARCHAR(50))
BEGIN
    -- criar utilizador MySQL
    SET @sql = CONCAT(
        'CREATE USER IF NOT EXISTS \'', p_Username, '\'@\'%\' IDENTIFIED BY \'', p_Password, '\''
    );
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- permissoes do utilizador, se o tipo for adm tambem consegue dar DELETE
    IF p_Tipo = 'admin' THEN
    SET @sql2 = CONCAT(
        'GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON maze_local.* TO \'', p_Username, '\'@\'%\''
    );
ELSE
    SET @sql2 = CONCAT(
        'GRANT SELECT, INSERT, UPDATE, EXECUTE ON maze_local.* TO \'', p_Username, '\'@\'%\''
    );
END IF;

    PREPARE stmt2 FROM @sql2;
    EXECUTE stmt2;
    DEALLOCATE PREPARE stmt2;

    -- flush para aplicar os grants
    FLUSH PRIVILEGES;

    -- inserir na tabela utilizador
    INSERT INTO Utilizador (Nome, Telemovel, Tipo, Email, DataNascimento, Equipa, Username)
    VALUES (p_Nome, p_Telemovel, p_Tipo, p_Email, p_DataNascimento, 6, p_Username);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`%` PROCEDURE `EditarUtilizador`(IN `p_Nome` VARCHAR(50), IN `p_Telemovel` VARCHAR(12), IN `p_Tipo` VARCHAR(5), IN `p_Email` VARCHAR(50), IN `p_DataNascimento` DATE, IN `p_Username` VARCHAR(50))
BEGIN
    DECLARE v_tipo VARCHAR(50);
    -- obter o tipo do utilizador atual
    SELECT Tipo INTO v_tipo
    FROM Utilizador
    WHERE Username = SUBSTRING_INDEX(USER(), '@', 1);
    -- permitir se for o próprio utilizador ou se for admin
    IF SUBSTRING_INDEX(USER(), '@', 1) = p_Username OR v_tipo = 'admin' THEN
        UPDATE Utilizador
        SET
            Nome            = COALESCE(NULLIF(p_Nome, ''), Nome),
            Telemovel       = COALESCE(NULLIF(p_Telemovel, ''), Telemovel),
            -- permite alterar o tipo de utilizador de outra pessoa so e apenas se for admin
            Tipo            = CASE WHEN v_tipo = 'admin' THEN COALESCE(NULLIF(p_Tipo, ''), Tipo) ELSE Tipo END,
            Email           = COALESCE(NULLIF(p_Email, ''), Email),
            DataNascimento  = COALESCE(p_DataNascimento, DataNascimento)
        WHERE Username = p_Username;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Não tens permissão para editar este utilizador';
    END IF;
END$$
DELIMITER ;
