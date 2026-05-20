# DISTRIBUTED MAZE SYSTEM - FASE 2
## Guia Técnico Detalhado para Defesa

**Repositório:** https://github.com/jarmela5/Distributed-Maze-System  
**Branch:** goncalo  
**Data:** 2025-05-20

---

## ÍNDICE

1. Resumo Executivo da Fase 2
2. Arquitetura Geral do Sistema
3. Ponto 2.1 - Sistema MQTT Distribuído
4. Ponto 2.2 - MongoDB Replica Set
5. Ponto 2.3 - MySQL Local e Persistência
6. Ponto 2.4 - State Engine
7. Ponto 2.5 - Migration Worker
8. Ponto 2.6 - Alert Engine
9. Ponto 2.7 - Decision Engine
10. Ponto 2.8 - Config Manager
11. Ponto 2.9 - Backend PHP Android
12. Ponto 2.10 - MQTT Listener
13. Ponto 2.11 - Event Processor
14. Ponto 2.12 - Docker Infrastructure
15. Acesso ao MySQL
16. Acesso ao MongoDB
17. Defesa - Resumo de Implementação

---

## 1. RESUMO EXECUTIVO DA FASE 2

A Fase 2 do projeto Distributed Maze System implementa uma arquitetura completamente distribuída e escalável, utilizando:

- **Dois PCs independentes** com roles específicos (PC1: Processamento + MongoDB | PC2: MySQL Writer)
- **MQTT como protocolo de comunicação** entre componentes
- **MongoDB Replica Set** para alta disponibilidade
- **MySQL local** para armazenamento persistente final
- **Engines de processamento** em tempo real (State, Alert, Decision)
- **Migration automática** de dados entre bases de dados
- **Backend PHP** para integração com aplicação Android

O sistema foi desenhado para tolerância a falhas, com capacidade de recuperação automática quando um nó cai, garantindo que os dados não se percam e o processamento continue sem interrupções.

---

## 2. ARQUITETURA GERAL DO SISTEMA

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│                      SENSORES (MQTT)                             │
│                   Temperatura | Som | Movimento                  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                    MQTT Broker (EMQX)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
   ┌────▼─────────────────────┐        ┌─────────▼──────────────┐
   │    PC1: LISTENER +         │        │   PC2: MYSQL WRITER    │
   │    PROCESSING              │        │                        │
   │                            │        │   - Subscreve MQTT     │
   │ • MQTT Listener            │        │   - Insere em MySQL    │
   │ • State Engine             │        │   - Publica Confirmação│
   │ • Alert Engine             │        │                        │
   │ • Decision Engine          │        └──────────┬─────────────┘
   │ • Event Processor          │                   │
   │ • Migration Worker         │                   │
   │                            │                   │
   │    MongoDB (Local)         │           MySQL (Local)
   │    - temperature_events    │           - Temperatura
   │    - sound_events          │           - Som
   │    - movement_events       │           - MedicoesPassagens
   │    - room_occupancy        │           - OcupacaoLabirinto
   │    - system_events         │           - Mensagens
   │                            │           - Simulacao
   └────────────────────────────┘           
```

### Componentes-Chave

| Componente | Localização | Linguagem | Função |
|-----------|------------|----------|--------|
| **PC1** | PC1 Local | Python | Processamento de eventos + MongoDB |
| **PC2** | PC2 Local | Python | Escrita em MySQL + MQTT |
| **MQTT Listener** | PC1 | Python | Subscrição de eventos sensoriais |
| **State Engine** | PC1 | Python | Validação e processamento de movimento |
| **Event Processor** | PC1 | Python | Orquestração de eventos |
| **Alert Engine** | PC1 | Python | Geração de alertas e controlo de atuadores |
| **Decision Engine** | PC1 | Python | Lógica de jogo e equilíbrio |
| **Migration Worker** | PC1 | Python | Transferência MongoDB → MySQL via MQTT |
| **MySQL Writer** | PC2 | Python | Persistência em MySQL |
| **Config Manager** | PC1 | Python | Leitura de configurações |
| **Backend PHP** | Docker | PHP | API REST para Android |
| **MongoDB** | Docker | NoSQL | Base de dados intermediária |
| **MySQL** | Docker | SQL | Base de dados final |

---

## 3. PONTO 2.1 - SISTEMA MQTT DISTRIBUÍDO

### Descrição

A Fase 2 implementa um sistema totalmente distribuído em que dois PCs independentes comunicam através do protocolo MQTT (Message Queuing Telemetry Transport). Este protocolo foi escolhido porque é leve, eficiente e adequado para sistemas IoT e distribuídos.

**PC1 - Listener e Processamento:**
- Subscreve aos tópicos MQTT de sensores (temperatura, som, movimento)
- Processa eventos em tempo real utilizando a State Engine
- Armazena dados no MongoDB
- Executa lógica de alertas (Alert Engine)
- Executa lógica de jogo (Decision Engine)
- Migra dados para PC2 via MQTT quando processados

**PC2 - MySQL Writer:**
- Subscreve apenas ao tópico de migração (pisid_migrate_all)
- Insere dados processados no MySQL local
- Publica confirmação de inserção (pisid_migrate_confirm)
- Não possui conexão com MongoDB, apenas MySQL

### Tópicos MQTT Utilizados

| Tópico | Publicador | Subscritor | Payload |
|--------|-----------|-----------|---------|
| `pisid_mazemov_<player_id>` | Sensores | PC1 | `{"marsami": int, "roomOrigin": int, "roomDestiny": int, "status": int}` |
| `pisid_mazetemp_<player_id>` | Sensores | PC1 | `{"temperature": float, "hour": timestamp}` |
| `pisid_mazesound_<player_id>` | Sensores | PC1 | `{"sound": float, "hour": timestamp}` |
| `pisid_mazeact` | PC1 (Alert/Decision) | Atuadores | `{"Type": string, "Player": int, ...}` |
| `pisid_migrate_all` | PC1 (Migration Worker) | PC2 | JSON com evento processado |
| `pisid_migrate_confirm` | PC2 | PC1 (Migration Worker) | `{"seq": int, "success": bool}` |

### Broker MQTT

- **Servidor**: broker.emqx.io (público)
- **Porta**: 1883 (padrão)
- **Qualidade de Serviço (QoS)**: 1 (entrega garantida pelo menos uma vez)

### Arquivos Relevantes

- **PC1**: `main_pc1.py` → Listener + Processing + Migration
- **PC2**: `main_pc2.py` → MySQL Writer
- **MQTT Listener**: `mqtt/mqtt_listener.py` → Subscrição de eventos
- **Migration Worker**: `persistance/migration_worker.py` → Publicação para PC2

### Como Executar

**Terminal 1 - PC1:**
```bash
cd /caminho/para/projeto
python main_pc1.py
```

**Terminal 2 - PC2:**
```bash
cd /caminho/para/projeto
python main_pc2.py
```

**Comportamento esperado:**
- PC1 mostra `[CONNECTED] MQTT` e lista de tópicos subscritos
- PC2 mostra `[MySQLWriter] CONNECT rc=0` e aguarda mensagens
- Ambos iniciam seus componentes e ficam à escuta

---

## 4. PONTO 2.2 - MONGODB REPLICA SET

### Descrição

MongoDB é utilizado como base de dados intermediária em PC1 para armazenar eventos sensoriais em tempo real. A implementação utiliza um **Replica Set com 3 nós** para garantir alta disponibilidade e tolerância a falhas.

Um Replica Set é um conjunto de instâncias MongoDB que se sincronizam automaticamente:
- **mongo1 (27017)** → PRIMARY (recebe todas as escritas)
- **mongo2 (27018)** → SECONDARY (cópia automática)
- **mongo3 (27019)** → SECONDARY (cópia automática)

Se o PRIMARY cair, um dos SECONDARY é eleito automaticamente como novo PRIMARY.

### Características de Tolerância a Falhas

O código Python em `MongoRepository` deteta automaticamente mudanças de PRIMARY e reconecta:

```python
def _connect(self):
    """Encontra o PRIMARY entre os 3 nós e liga-se a ele."""
    for port in self.ports:
        try:
            client = pymongo.MongoClient(
                f"mongodb://localhost:{port}/?directConnection=true",
                serverSelectionTimeoutMS=2000
            )
            info = client.admin.command("isMaster")
            if info.get("ismaster"):
                self.client = client
                self.db = client[self.db_name]
                print(f"[MongoDB] PRIMARY encontrado na porta {port}")
                return
            client.close()
        except Exception:
            continue
    raise Exception("[MongoDB] Não foi possível encontrar nenhum PRIMARY")
```

Se a conexão falhar durante uma operação, o sistema tenta reconectar automaticamente até 5 vezes com intervalo de 3 segundos.

### Coleções Utilizadas

| Coleção | Descrição |
|---------|-----------|
| `temperature_events` | Eventos de temperatura com timestamp e validação |
| `sound_events` | Eventos de som/ruído com nível |
| `movement_events` | Movimentos dos Marsamis entre salas |
| `room_occupancy` | Estado de ocupação das salas (odd/even) |
| `system_events` | Alertas e eventos do sistema |

Cada documento tem um campo `seq` (sequência) e `migrated` (boolean) para controlar a migração.

### Indexes Criados Automaticamente

```python
# temperature_events
- seq
- player
- migrated

# sound_events
- seq
- player
- migrated

# movement_events
- seq
- player
- marsami_id
- migrated

# room_occupancy
- seq
- migrated
- room_id

# system_events
- seq
- migrated
```

### Configuração Passo a Passo

**Passo 1 - Editar hosts (Windows com permissões de Administrador):**
1. Carregar Windows + tipo "Notepad"
2. Clicar direito → "Run as administrator"
3. File → Open
4. Navegar para `C:\Windows\System32\drivers\etc`
5. Mudar filtro de "Text Documents" para "All Files"
6. Abrir ficheiro `hosts`
7. Adicionar na última linha: `127.0.0.1 mongo1 mongo2 mongo3`
8. File → Save

**Passo 2 - Arrancar os containers:**
```bash
docker compose up -d
```

Aguardar 10-15 segundos para containers iniciarem.

**Passo 3 - Inicializar o Replica Set (apenas uma vez):**
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

**Passo 4 - Verificar estado do Replica Set:**
```bash
docker exec -it mongo1 mongosh --eval "rs.status().members.map(m => ({name: m.name, state: m.stateStr}))"
```

Resultado esperado:
```
mongo1:27017 → PRIMARY
mongo2:27017 → SECONDARY
mongo3:27017 → SECONDARY
```

---

## 15. ACESSO AO MYSQL

### Opção 1: phpMyAdmin (Interface Web - Recomendado)

**Acesso:**
```
http://localhost:9001
```

**Credenciais:**
- Utilizador: `root`
- Password: `root`

**Passo a Passo:**
1. Abrir browser
2. Navegar para `http://localhost:9001`
3. Na página de login, preencher:
   - Server: `mysql` (nome do container)
   - Username: `root`
   - Password: `root`
4. Clicar "Go"
5. Selecionar database `maze_local` na coluna esquerda

**Operações possíveis:**
- Ver tabelas: Expandir `maze_local` no painel esquerdo
- Ver dados: Clicar em nome da tabela
- Executar queries: Clicar em "SQL" no topo

---

## 16. ACESSO AO MONGODB

### Opção 1: Mongo Compass (Interface Gráfica - Recomendado)

**Download:**
Descarregar Mongo Compass de: https://www.mongodb.com/try/download/compass

**Configurar Conexão:**

**Método 1 - ReplicaSet (Recomendado):**
```
mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0
```

1. Abrir Mongo Compass
2. Na caixa "Paste a connection string", colar a string acima
3. Clicar "Connect"

**Navegação:**
- Expandir `distributed_maze` na coluna esquerda
- Expandir colecções (temperature_events, etc)
- Clicar em colecção para ver documentos

### Opção 2: mongosh (Linha de Comando)

**Acesso ao container mongo1:**
```bash
docker exec -it mongo1 mongosh
```

**Comandos úteis:**

Ver databases:
```javascript
show dbs
```

Usar database:
```javascript
use distributed_maze
```

Ver coleções:
```javascript
show collections
```

Contar documentos:
```javascript
db.temperature_events.countDocuments()
```

Ver documentos não migrados:
```javascript
db.temperature_events.find({"migrated": false})
```

---

## 17. DEFESA - RESUMO DE IMPLEMENTAÇÃO

### Checklist de Demonstração

#### Pré-Requisitos
- [ ] Docker instalado e rodando
- [ ] Ficheiro `hosts` editado
- [ ] Dependências Python instaladas: `pip install -r requirements.txt`

#### Setup Infraestrutura
- [ ] Executar: `docker compose up -d`
- [ ] Aguardar 15 segundos para containers iniciarem
- [ ] Verificar MongoDB ReplicaSet

#### Execução da Aplicação
- [ ] Terminal 1: `python main_pc1.py`
- [ ] Terminal 2: `python main_pc2.py`

#### Verificações Finais

**MongoDB Compass:**
- [ ] Ligar a `mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0`
- [ ] Ver documentos em `distributed_maze`

**phpMyAdmin:**
- [ ] Ir para `http://localhost:9001`
- [ ] Ver dados em `maze_local`

### Pontos-Chave para Mencionar na Defesa

#### Arquitetura
- Dois PCs independentes com MQTT como middleware
- Separação de responsabilidades: PC1 (processamento) vs PC2 (persistência)
- Comunicação assíncrona = maior escalabilidade

#### Tolerância a Falhas
- MongoDB ReplicaSet com 3 nós → quórum de eleição
- Reconexão automática quando PRIMARY cai
- Migration Worker com retry automático (5 tentativas)
- Documentos não perdem-se mesmo com PC2 down

#### Processamento em Tempo Real
- State Engine valida eventos conforme chegam
- Alert Engine reage a temperatura/som com latência mínima
- Decision Engine detecta equilíbrios antes da confirmação (predição)

#### Escalabilidade Futura
- Adicionar mais Players: apenas criar novos tópicos MQTT
- Distribuir PC2 em múltiplos servidores
- Usar Kafka/RabbitMQ em vez de MQTT para volumes maiores

---

**Fim do Documento**

Repositório: https://github.com/jarmela5/Distributed-Maze-System  
Branch: goncalo  
Data de Última Atualização: 2025-05-20