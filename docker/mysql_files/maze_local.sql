SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS maze_local;
USE maze_local;

-- --------------------------------------------------------
-- Tabela Simulacao
-- --------------------------------------------------------

CREATE TABLE Simulacao (
  IDSimulacao INT AUTO_INCREMENT PRIMARY KEY,
  Descricao TEXT,
  Equipa INT NOT NULL,
  DataHoraInicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Estado VARCHAR(20) DEFAULT 'Ativo'
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- MedicoesPassagens
-- --------------------------------------------------------

CREATE TABLE MedicoesPassagens (
  IDMedicao INT AUTO_INCREMENT PRIMARY KEY,
  Hora TIMESTAMP NULL,
  SalaOrigem INT,
  SalaDestino INT,
  Marsami INT,
  Status INT,
  is_valid BOOLEAN DEFAULT TRUE,
  IDJogo INT NOT NULL,
  FOREIGN KEY (IDJogo) REFERENCES Simulacao(IDSimulacao) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- Temperatura
-- --------------------------------------------------------

CREATE TABLE Temperatura (
  IDTemperatura INT AUTO_INCREMENT PRIMARY KEY,
  Hora TIMESTAMP NULL,
  Temperatura DECIMAL(6,2),
  is_valid BOOLEAN DEFAULT TRUE,
  IDJogo INT NOT NULL,
  FOREIGN KEY (IDJogo) REFERENCES Simulacao(IDSimulacao) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- Som
-- --------------------------------------------------------

CREATE TABLE Som (
  IDSom INT AUTO_INCREMENT PRIMARY KEY,
  Hora TIMESTAMP NULL,
  Som DECIMAL(6,2),
  is_valid BOOLEAN DEFAULT TRUE,
  IDJogo INT NOT NULL,
  FOREIGN KEY (IDJogo) REFERENCES Simulacao(IDSimulacao) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- OcupacaoLabirinto
-- --------------------------------------------------------

CREATE TABLE OcupacaoLabirinto (
  IDJogo INT NOT NULL,
  Sala INT NOT NULL,
  NumeroMarsamisOdd INT DEFAULT 0,
  NumeroMarsamisEven INT DEFAULT 0,
  PRIMARY KEY (IDJogo, Sala),
  FOREIGN KEY (IDJogo) REFERENCES Simulacao(IDSimulacao) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- Mensagens
-- --------------------------------------------------------

CREATE TABLE Mensagens (
  ID BIGINT AUTO_INCREMENT PRIMARY KEY,
  Hora TIMESTAMP NULL,
  Sala INT,
  Sensor VARCHAR(10),
  Leitura DECIMAL(6,2),
  TipoAlerta VARCHAR(50),
  Msg VARCHAR(100),
  HoraEscrita TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  IDJogo INT NOT NULL,
  FOREIGN KEY (IDJogo) REFERENCES Simulacao(IDSimulacao) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- Alertas
-- --------------------------------------------------------

CREATE TABLE Alertas (
  ID BIGINT PRIMARY KEY,
  FOREIGN KEY (ID) REFERENCES Mensagens(ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- --------------------------------------------------------
-- Utilizador
-- --------------------------------------------------------

CREATE TABLE Utilizador (
  IDUtilizador INT AUTO_INCREMENT PRIMARY KEY,
  Nome VARCHAR(100) NOT NULL,
  Telemovel VARCHAR(12),
  Tipo VARCHAR(10),
  Email VARCHAR(50),
  Password VARCHAR(255),
  DataNascimento DATE,
  Equipa INT NOT NULL,
  IDJogo INT NOT NULL,
  FOREIGN KEY (IDJogo) REFERENCES Simulacao(IDSimulacao) ON DELETE CASCADE
);

COMMIT;