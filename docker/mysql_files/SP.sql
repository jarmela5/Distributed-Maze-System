-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: maze_local
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping routines for database 'maze_local'
--
/*!50003 DROP PROCEDURE IF EXISTS `CancelarJogo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `CancelarJogo`(IN p_idJogo INT)
BEGIN

    UPDATE Simulacao
    SET Estado='Cancelado'
    WHERE IDSimulacao=p_idJogo
      AND Estado='Agendado';

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CriarJogo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `CriarJogo`(IN `p_dados` JSON, OUT `id_jogo_criado` INT)
BEGIN

    DECLARE v_email VARCHAR(50);
    DECLARE v_starttime TIMESTAMP;
    DECLARE v_descricao TEXT;

    SET v_email = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Email'));
    SET v_starttime = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.StartTime'));
    SET v_descricao = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Descricao'));

    INSERT INTO Simulacao (Descricao, Equipa, DataHoraInicio, Estado)
    VALUES (v_descricao, 6, v_starttime, 'Agendado');

    SET id_jogo_criado = LAST_INSERT_ID();

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `CriarUtilizador` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `CriarUtilizador`(IN `p_dados` JSON)
BEGIN

    DECLARE v_email VARCHAR(50);
    DECLARE v_nome VARCHAR(100);
    DECLARE v_telemovel VARCHAR(12);
    DECLARE v_tipo VARCHAR(10);
    DECLARE v_password VARCHAR(255);
    DECLARE v_role VARCHAR(10);

    SET v_email     = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Email'));
    SET v_nome      = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Nome'));
    SET v_telemovel = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Telemovel'));
    SET v_tipo      = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Tipo'));
    SET v_password  = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Password'));

    IF v_tipo NOT IN ('Jog','Adm','Mig') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT='Tipo de utilizador inválido';
    END IF;

    IF EXISTS (SELECT 1 FROM Utilizador WHERE Email=v_email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT='Email já existe';
    END IF;

    INSERT INTO Utilizador (Nome,Telemovel,Tipo,Email,Equipa,Password)
    VALUES (v_nome,v_telemovel,v_tipo,v_email,6, v_password);

    SELECT LAST_INSERT_ID() AS IDUtilizadorCriado;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `EditarJogo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `EditarJogo`(IN p_id_jogo INT, IN p_dados JSON)
BEGIN

    DECLARE v_estado_atual VARCHAR(20);
    DECLARE v_novo_estado VARCHAR(20);
    DECLARE v_nova_data TIMESTAMP;
    DECLARE v_nova_desc TEXT;

    SELECT Estado INTO v_estado_atual
    FROM Simulacao
    WHERE IDSimulacao=p_id_jogo;

    SET v_novo_estado = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Estado'));
    SET v_nova_data = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.DataHoraInicio'));
    SET v_nova_desc = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Descricao'));

    UPDATE Simulacao
    SET
        DataHoraInicio = COALESCE(v_nova_data,DataHoraInicio),
        Descricao = COALESCE(v_nova_desc,Descricao),
        Estado = COALESCE(v_novo_estado,Estado)
    WHERE IDSimulacao=p_id_jogo;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `EditarUtilizador` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `EditarUtilizador`(IN p_dados JSON)
BEGIN

    DECLARE v_email_alvo VARCHAR(50);
    DECLARE v_nome VARCHAR(100);
    DECLARE v_telemovel VARCHAR(12);
    DECLARE v_password VARCHAR(255);
    DECLARE v_tipo_caller VARCHAR(10);
    DECLARE v_email_caller VARCHAR(50);

    -- Lê o email do JSON (necessário para admins)
    SET v_email_caller = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.EmailCaller'));
    
    -- Se não fornecido, usa o próprio CURRENT_USER() para mapear email da tabela
    IF v_email_caller IS NULL THEN
        SET v_email_caller = SUBSTRING_INDEX(CURRENT_USER(),'@',1);
    END IF;

    -- Tipo do utilizador
    SELECT Tipo INTO v_tipo_caller
    FROM Utilizador
    WHERE Email=v_email_caller;

    -- Define o Email alvo
    IF v_tipo_caller='Adm' AND JSON_EXTRACT(p_dados,'$.Email') IS NOT NULL THEN
        SET v_email_alvo = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Email'));
    ELSE
        SET v_email_alvo = v_email_caller;
    END IF;

    -- Verifica se o alvo existe
    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE Email=v_email_alvo) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Utilizador não encontrado';
    END IF;

    -- Ler campos do JSON
    SET v_nome      = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Nome'));
    SET v_telemovel = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Telemovel'));
    SET v_password  = JSON_UNQUOTE(JSON_EXTRACT(p_dados,'$.Password'));

    -- Atualizar tabela
    UPDATE Utilizador
    SET
        Nome = COALESCE(v_nome, Nome),
        Telemovel = COALESCE(v_telemovel, Telemovel)
    WHERE Email=v_email_alvo;

    -- Atualizar password MySQL se fornecida
    IF v_password IS NOT NULL THEN
        SET @sql = CONCAT('ALTER USER ''', v_email_alvo, '''@''%'' IDENTIFIED BY ''', v_password, '''');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        FLUSH PRIVILEGES;
    END IF;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `IniciarJogo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `IniciarJogo`(IN p_idJogo INT)
BEGIN

    IF EXISTS (SELECT 1 FROM Simulacao WHERE Estado='Ativo') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT='Já existe um jogo ativo';
    END IF;

    UPDATE Simulacao
    SET Estado='Ativo',
        DataHoraInicio=NOW()
    WHERE IDSimulacao=p_idJogo;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `RemoverUtilizador` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_unicode_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `RemoverUtilizador`(IN p_email VARCHAR(50))
BEGIN

    IF NOT EXISTS (SELECT 1 FROM Utilizador WHERE Email=p_email) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT='Utilizador não encontrado';
    END IF;

    DELETE FROM Utilizador
    WHERE Email=p_email;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-14 18:34:43
