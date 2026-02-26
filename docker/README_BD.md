Assumindo que:

* Cada colega já tem o seu próprio Docker configurado
* Só precisa de colocar o `maze_local.sql` dentro da pasta `mysql_files`
* Criar manualmente a base de dados
* Importar o ficheiro via **phpMyAdmin**
---

# Distributed Maze System

## 🐳 Docker Setup & Database Import

Este guia explica como configurar o ambiente Docker e importar a base de dados **`maze_local`** utilizando o ficheiro `maze_local.sql` disponível no GitHub.

---

## 🚀 2️⃣ Entrar na tua pasta Docker

```bash
cd teulocaldodocker
```

---

## 🐳 3️⃣ Iniciar os Containers

```bash
docker-compose up -d
```

Isto vai iniciar:

* 🐬 **MySQL**
* 🍃 **MongoDB**
* 🌐 **phpMyAdmin**

---

## 🔍 4️⃣ Verificar se está tudo a correr

```bash
docker ps
```

Confirma que aparecem containers como:

* `mysql`
* `mongodb`
* `docker-phpmyadmin-1`

Verifica também a porta do phpMyAdmin, algo como:

```
0.0.0.0:9001->80/tcp
```

---

## 🗄️ 5️⃣ Criar a Base de Dados no MySQL

Entrar no MySQL dentro do container:

```bash
docker exec -it mysql mysql -u root -p
```

(Se pedir password, usar `root`)

Depois executar:

```sql
CREATE DATABASE maze_local;
USE maze_local;
```

Sair com:

```sql
exit;
```

---

## 🌐 6️⃣ Importar o ficheiro SQL via phpMyAdmin

Abrir no browser:

```
http://localhost:9001
```

*(Se a porta for diferente, usa a que aparece no `docker ps`)*

---

### 🔑 Login

* **Servidor:** `mysql`
* **Utilizador:** `root`
* **Password:** `root`

---

### 📥 Importar o ficheiro

1. Clicar em **`maze_local`**
2. Ir ao separador **Import**
3. Selecionar o ficheiro `maze_local.sql` (colocado no projeto na pasta /docker/mysql_files/)
4. Clicar em **Go**

---

## ✅ Verificar a Importação

Depois da importação, confirmar que existem as seguintes tabelas:

* **Simulacao**
* **Utilizador**
* **Temperatura**
* **Som**
* **MedicoesPassagens**
* **Mensagens**
* **OcupacaoLabirinto**

Se aparecerem, a base de dados foi importada com sucesso 🎉

---

## 🔄 Caso seja necessário reiniciar tudo

```bash
docker-compose down
docker-compose up -d
```

Depois repetir o processo de importação.

---

## 🎯 Setup Rápido (Resumo)

```bash
git pull
cd docker
docker-compose down
docker-compose up -d
docker exec -it mysql mysql -u root -p
```

Depois no MySQL:

```sql
CREATE DATABASE maze_local;
USE maze_local;
```

Depois importar o `maze_local.sql` no phpMyAdmin.

