# MongoDB Replica Set — Guia de Configuração

Este guia explica como configurar o MongoDB em modo Replica Set usando Docker, permitindo que se um nó cair, outro assuma automaticamente.

---

## O que é um Replica Set?

Um Replica Set é um conjunto de 3 instâncias MongoDB que se sincronizam automaticamente:

- **mongo1** → Primário (recebe todas as escritas)
- **mongo2** → Secundário (cópia automática)
- **mongo3** → Secundário (cópia automática)

Se o primário cair, um dos secundários é eleito automaticamente como novo primário.

---

## Passo 1 — Ficheiro hosts (Windows)

Para que o Python e o Mongo Compass consigam resolver os nomes `mongo1`, `mongo2`, `mongo3`, é necessário adicioná-los ao ficheiro `hosts` do Windows.

### Como editar o ficheiro hosts

1. Carrega na tecla Windows e escreve **Notepad**
2. Clica com o botão direito → **Run as administrator**
3. No Notepad: **File → Open**
4. Na barra de endereço escreve: `C:\Windows\System32\drivers\etc`
5. Em baixo onde diz "Text Documents" muda para **All Files**
6. Abre o ficheiro **hosts**
7. Adiciona estas 3 linhas no fim do ficheiro:

```
127.0.0.1 mongo1
127.0.0.1 mongo2
127.0.0.1 mongo3
```

8. **File → Save**

---

## Passo 2 — docker-compose.yml

Substitui o `docker-compose.yml` pelo dentro desta pasta

## Passo 3 — Arrancar os contentores

Se já tinhas dados antigos, limpa-os primeiro:

```powershell
docker compose down
Remove-Item -Recurse -Force mongo_data1\*, mongo_data2\*, mongo_data3\*
ou se houver: Remove-Item -Recurse -Force mongo_data
```

Arrancar:

```bash
docker compose up -d
```

---

## Passo 4 — Inicializar o Replica Set (apenas uma vez)

Este comando só precisa de ser executado **uma única vez** após a primeira instalação:

```bash
docker exec -it mongo1 mongosh --eval "
rs.initiate({
  _id: 'rs0',
  members: [
    { _id: 0, host: 'mongo1:27017' },
    { _id: 1, host: 'mongo2:27017' },
    { _id: 2, host: 'mongo3:27017' }
  ]
})
"
```

Deves ver `{ ok: 1 }` no fim.

---

## Passo 5 — Verificar o estado do Replica Set

```bash
docker exec -it mongo1 mongosh --eval "rs.status()"
```

Deves ver:
- `mongo1` → `PRIMARY`
- `mongo2` → `SECONDARY`
- `mongo3` → `SECONDARY`

---



## Passo 6 — Mongo Compass

Para ligar ao Mongo Compass usa a seguinte connection string:

```
mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0
```

> **Requer** que o ficheiro `hosts` tenha sido editado (Passo 1), caso contrário o Compass não consegue resolver os nomes `mongo1`, `mongo2`, `mongo3`.

---

## Reiniciar do zero

Se precisares de apagar todos os dados do MongoDB e começar do zero:

```powershell
docker compose down
Remove-Item -Recurse -Force mongo_data1, mongo_data2, mongo_data3
docker compose up -d
```

E depois repete o **Passo 4** para inicializar o Replica Set novamente.

---

## Resumo dos portos

| Serviço      | Porto local | Acesso                        |
|--------------|-------------|-------------------------------|
| PHP          | 9000        | http://localhost:9000          |
| phpMyAdmin   | 9001        | http://localhost:9001          |
| MySQL        | 3306        | localhost:3306                 |
| mongo1       | 27017       | mongo1:27017 (primário)        |
| mongo2       | 27018       | mongo2:27017 (secundário)      |
| mongo3       | 27019       | mongo3:27017 (secundário)      |