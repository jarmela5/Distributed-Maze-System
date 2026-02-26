#!/usr/bin/env bash
docker exec -i mysql mysql -u root -proot < mysql_files/maze_local.sql
echo "✅ Base de dados criada/importada com sucesso."