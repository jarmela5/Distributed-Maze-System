# Distributed Maze System

## 🐳 Docker Setup & Database Initialization

Este guia explica como configurar o ambiente Docker e criar a base de dados **`maze_local`** após fazer `git pull`.

---

## ⚠️ Importante Antes de Começar

Se já tiveres containers Docker a correr de outra localização do projeto, deves pará-los primeiro.

Vai para a pasta antiga onde tinhas o Docker e executa:

```bash
docker-compose down
```

Isto evita conflitos de portas e containers duplicados.

---

## 🚀 1️⃣ Entrar na pasta Docker deste projeto

```bash
cd docker
```

---

## 🐳 2️⃣ Iniciar os Containers

```bash
docker-compose up -d
```

Isto vai iniciar:

* 🐬 **MySQL**
* 🍃 **MongoDB**
* 🌐 **phpMyAdmin**
* 🐘 **PHP** (se aplicável)

---

## 🔍 3️⃣ Verificar se está tudo a correr

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

## 🧠 4️⃣ Criar a Base de Dados

Executa:

```bash
./init_db.sh
```

Se tudo correr bem, vais ver:

```
✅ Base de dados criada/importada com sucesso.
```

---

## 🌐 5️⃣ Aceder ao phpMyAdmin

Abre o browser e vai para:

```
http://localhost:9001
```

*(Se a porta for diferente, usa a que aparece no `docker ps`)*

---

## 🔑 Login no phpMyAdmin

* **Servidor:** `mysql`
* **Utilizador:** `root`
* **Password:** `root`

---

## 🗄️ Verificar a Base de Dados

Depois de entrar:

1. Clica em **`maze_local`**
2. Verifica se existem as tabelas:

* **Simulacao**
* **Utilizador**
* **Temperatura**
* **Som**
* **MedicoesPassagens**
* **Mensagens**
* **OcupacaoLabirinto**

Se aparecerem, estás totalmente sincronizado com o projeto ✅

---

## 🔄 Reinicializar a Base de Dados

Sempre que necessário:

```bash
./init_db.sh
```

---

## ⚠️ Notas Importantes

As seguintes pastas **não devem ser versionadas**:

```
docker/mysql_data/
docker/mongo_data/
```

Estas contêm dados locais do Docker e não devem ser partilhadas no Git.

---

## 🎯 Setup Rápido (Resumo)

```bash
git pull
cd docker
docker-compose down   # caso existam containers ativos
docker-compose up -d
./init_db.sh
```

Depois abre:

```
http://localhost:9001
```

---

