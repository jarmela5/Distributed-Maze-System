-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Tempo de geração: 26-Fev-2026 às 10:19
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

-- --------------------------------------------------------

--
-- Estrutura da tabela `MedicoesPassagens`
--

CREATE TABLE `MedicoesPassagens` (
  `IDMedicao` int NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `SalaOrigem` int DEFAULT NULL,
  `SalaDestino` int DEFAULT NULL,
  `Marsami` int DEFAULT NULL,
  `Status` int DEFAULT NULL
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
  `HoraEscrita` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `OcupacaoLabirinto`
--

CREATE TABLE `OcupacaoLabirinto` (
  `IDJogo` int NOT NULL,
  `Sala` int NOT NULL,
  `NumeroMarsamisOdd` int NOT NULL DEFAULT '0',
  `NumeroMarsamisEven` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Simulacao`
--

CREATE TABLE `Simulacao` (
  `IDSimulacao` int NOT NULL,
  `Descricao` text,
  `Equipa` int NOT NULL,
  `DataHoraInicio` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Som`
--

CREATE TABLE `Som` (
  `IDSom` int NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `Som` varchar(12) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Temperatura`
--

CREATE TABLE `Temperatura` (
  `IDTemperatura` int NOT NULL,
  `Hora` timestamp NULL DEFAULT NULL,
  `Temperatura` varchar(12) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Estrutura da tabela `Utilizador`
--

CREATE TABLE `Utilizador` (
  `IDUtilizador` int NOT NULL,
  `Nome` varchar(100) NOT NULL,
  `Telemovel` varchar(12) DEFAULT NULL,
  `Tipo` varchar(3) DEFAULT NULL,
  `Email` varchar(50) DEFAULT NULL,
  `DataNascimento` date DEFAULT NULL,
  `Equipa` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Índices para tabelas despejadas
--

--
-- Índices para tabela `MedicoesPassagens`
--
ALTER TABLE `MedicoesPassagens`
  ADD PRIMARY KEY (`IDMedicao`);

--
-- Índices para tabela `Mensagens`
--
ALTER TABLE `Mensagens`
  ADD PRIMARY KEY (`ID`);

--
-- Índices para tabela `OcupacaoLabirinto`
--
ALTER TABLE `OcupacaoLabirinto`
  ADD PRIMARY KEY (`IDJogo`,`Sala`);

--
-- Índices para tabela `Simulacao`
--
ALTER TABLE `Simulacao`
  ADD PRIMARY KEY (`IDSimulacao`);

--
-- Índices para tabela `Som`
--
ALTER TABLE `Som`
  ADD PRIMARY KEY (`IDSom`);

--
-- Índices para tabela `Temperatura`
--
ALTER TABLE `Temperatura`
  ADD PRIMARY KEY (`IDTemperatura`);

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
  MODIFY `IDSimulacao` int NOT NULL AUTO_INCREMENT;

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
  MODIFY `IDUtilizador` int NOT NULL AUTO_INCREMENT;

--
-- Restrições para despejos de tabelas
--

--
-- Limitadores para a tabela `OcupacaoLabirinto`
--
ALTER TABLE `OcupacaoLabirinto`
  ADD CONSTRAINT `fk_ocupacao_simulacao` FOREIGN KEY (`IDJogo`) REFERENCES `Simulacao` (`IDSimulacao`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
