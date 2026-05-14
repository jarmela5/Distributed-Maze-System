    CREATE TRIGGER `before_insert_utilizador` BEFORE INSERT ON `Utilizador`
 FOR EACH ROW BEGIN
    DECLARE v_tipo VARCHAR(20);
    DECLARE v_user VARCHAR(100);

    SET v_user = SUBSTRING_INDEX(USER(), '@', 1);

    SELECT Tipo INTO v_tipo
    FROM Utilizador
    WHERE Username = v_user
    LIMIT 1;

    -- Permite se for root OU se for admin na tabela
    IF v_user <> 'root' AND (v_tipo IS NULL OR LOWER(v_tipo) <> 'admin') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Apenas admins podem inserir utilizadores';
    END IF;
END

CREATE TRIGGER `before_update_simulacao` BEFORE UPDATE ON `Simulacao`
 FOR EACH ROW BEGIN
    DECLARE v_user VARCHAR(100);
    DECLARE v_idUtilizador INT;
    DECLARE v_tipo VARCHAR(20);

    -- obter username atual
    SET v_user = SUBSTRING_INDEX(USER(), '@', 1);

    -- obter ID e tipo do utilizador atual
    SELECT IDUtilizador, Tipo INTO v_idUtilizador, v_tipo
    FROM Utilizador
    WHERE Username = v_user
    LIMIT 1;

    -- utilizador normal só pode alterar as suas próprias simulações
    -- admins passam diretamente
    IF LOWER(v_tipo) <> 'admin' THEN
        IF OLD.IDUtilizador <> v_idUtilizador THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Só podes alterar as tuas próprias simulações';
        END IF;
    END IF;
END

CREATE TRIGGER `before_update_utilizador` BEFORE UPDATE ON `Utilizador`
 FOR EACH ROW BEGIN
    DECLARE v_tipo VARCHAR(50);
    DECLARE v_current_user VARCHAR(100);

    SET v_current_user = SUBSTRING_INDEX(USER(), '@', 1);

    SELECT Tipo INTO v_tipo
    FROM Utilizador
    WHERE Username = v_current_user
    LIMIT 1;

    IF v_tipo IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Utilizador atual inválido';
    END IF;

    IF LOWER(v_tipo) <> 'admin' THEN

        IF v_current_user <> OLD.Username THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Não podes editar outros utilizadores';
        END IF;

        IF NEW.Tipo <> OLD.Tipo THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Não podes alterar o tipo de utilizador';
        END IF;

        IF NEW.Username <> OLD.Username THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Não podes alterar o username';
        END IF;

        IF NEW.Equipa <> OLD.Equipa THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Não podes alterar a equipa';
        END IF;

    END IF;

END

CREATE TRIGGER `before_insert_simulacao` BEFORE INSERT ON `Simulacao`
 FOR EACH ROW BEGIN
    DECLARE v_user VARCHAR(100);
    DECLARE v_idUtilizador INT;

    -- obter username atual
    SET v_user = SUBSTRING_INDEX(USER(), '@', 1);

    -- obter ID do utilizador atual
    SELECT IDUtilizador INTO v_idUtilizador
    FROM Utilizador
    WHERE Username = v_user
    LIMIT 1;

    -- verificar se o IDUtilizador inserido corresponde ao utilizador atual
    IF NEW.IDUtilizador <> v_idUtilizador THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Só podes inserir simulações com o teu próprio ID';
    END IF;
END
