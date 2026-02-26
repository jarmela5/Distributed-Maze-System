Create database atp;
use atp;
CREATE TABLE `atpplayers` (
  `PlayerName` varchar(100) DEFAULT NULL,
  `Born` varchar(100) DEFAULT NULL,
  `Height` varchar(100) DEFAULT NULL,
  `Hand` varchar(100) DEFAULT NULL,
  `Tournament` varchar(100) DEFAULT NULL,
  `Location` varchar(100) DEFAULT NULL,
  `Date` varchar(100) DEFAULT NULL,
  `Ground` varchar(100) DEFAULT NULL,
  `Prize` varchar(100) DEFAULT NULL,
  `WL` varchar(100) DEFAULT NULL,
  `Score` varchar(100) DEFAULT NULL,
  `Round` varchar(100) DEFAULT NULL,
  `OpponentRank` varchar(100) DEFAULT NULL,
  `Opponent` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
