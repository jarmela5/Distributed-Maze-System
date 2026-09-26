# Distributed Maze System

## Project objective

This project was developed in the context of the Distributed Information Systems coursework and aims to implement a solution that includes:

- distributed data across at least two computers;
- storage in two different technologies: MySQL (relational) and MongoDB (non-relational);
- fault tolerance caused by crashes in databases, computers, and software;
- incremental data migration between databases;
- use of the MQTT protocol for receiving sensor data and transmitting data between computers;
- detection of outliers and "dirty" data originating from sensors;
- real-time actuation in the system, with second-level granularity;
- use of Python, PHP, and Android Studio;
- management of requirements in an academic project context.

---

## Resources provided by the professor and support material from the assignment

The project brief and the base infrastructure were provided by the professor to support the development of the solution. This includes:

- executables and tools for maze simulation;
- initial Docker configuration and infrastructure services;
- SQL files and database scripts;
- documentation and integration examples for the system;
- support material for running the project environment.

In the repository, these elements appear in folders such as:

- `docker/`
- `docker_file/`
- `servers/`
- `site/`
- `maze_app_php/`

These files are part of the context of the work, but they do not replace the implementation developed by the group.

---

## General description

The system simulates a maze composed of rooms connected by one-way corridors. In this maze, "marsamis" move; they may be of the odd or even type.

Each player (software) receives data from sensors for:

- temperature;
- noise;
- marsami movement;
- passage through corridors.

Based on this data, the software:

- updates the maze state;
- identifies balance between odd and even marsamis per room;
- decides when to trigger events;
- controls actuators such as doors and air conditioning;
- records events and stores data in databases.

---

## Maze rules

### Maze structure

- the maze is made up of several rooms;
- rooms are connected by corridors;
- each corridor connects only two rooms;
- multiple corridors may provide access to the same room;
- movement between rooms is one-directional;
- corridors may be opened or closed individually or in bulk.

### Marsamis

- marsamis are released randomly across rooms;
- they move from room to room through available corridors;
- each marsami has a unique identifier;
- there are odd and even marsamis;
- when they become tired, they stop moving and become "immobile";
- the simulation can end when all marsamis stop or when temperature/noise exceeds defined limits.

### Player objective

Each player aims to maximize the score. The score can be obtained in two ways:

1. at the end of the simulation, determine exactly how many marsamis remain in each room;
2. during the simulation, identify in real time when, in a given room, the number of odd and even marsamis is balanced.

If a trigger is activated before the balance is lost, the player earns 1 point. If the balance is lost first, the player loses half a point.

Each room can have a maximum of 3 trigger activations.

---

## Sensors and actuators

### Sensors

Sensors send data to MQTT topics, one per player, using the format below.

#### 1. Noise sensors

Topic:

- `pisid_mazesound_<n>`

Example:

```json
{ "Player": 11, "Hour": "2024-07-04 16:29:21.281898", "Sound": 19.0 }
```

#### 2. Temperature sensors

Topic:

- `pisid_mazetemp_<n>`

Example:

```json
{ "Player": 11, "Hour": "2024-07-04 16:29:21.281898", "Temperature": 19.0 }
```

#### 3. Movement sensors

Topic:

- `pisid_mazemov_<n>`

Example:

```json
{ "Player": 1, "Marsami": 47, "RoomOrigin": 4, "RoomDestiny": 5, "Status": 1 }
```

### Actuators

The software receives actuation orders on the topic:

- `pisid_mazeact`

Examples:

```json
{ "Type": "Score", "Player": 1, "Room": 2 }
{ "Type": "OpenDoor", "Player": 1, "RoomOrigin": 3, "RoomDestiny": 2 }
{ "Type": "CloseDoor", "Player": 1, "RoomOrigin": 3, "RoomDestiny": 2 }
{ "Type": "CloseAllDoor", "Player": 1 }
{ "Type": "OpenAllDoor", "Player": 1 }
{ "Type": "AcOn", "Player": 1 }
{ "Type": "AcOff", "Player": 1 }
```

Actuators allow:

- opening and closing corridors;
- closing or opening all corridors simultaneously;
- turning the air conditioning on or off;
- responding to extreme noise or temperature conditions.

---

## Temperature and noise rules

If the noise and/or temperature reaches a certain threshold:

- all corridors are automatically closed;
- the simulation ends;
- marsamis remain immobile and the player cannot reopen the corridors.

Noise increases proportionally to the number of marsami movements. If some corridors are closed, the noise level decreases.

---

## Simulation start and end

The simulation starts when the group starts the software or simulation.

It ends automatically when:

- the temperature or noise limit is reached;
- a predefined period passes without marsami movement;
- all marsamis are tired or immobile.

---

## System architecture

### 1. PC1 / Player

This is the main computer where the player software runs.

Functions:

- receives sensor data via MQTT;
- processes movement, temperature, and noise events;
- updates the maze state;
- detects odd/even equilibrium events;
- triggers alerts and actions;
- sends data to databases and migration components.

### 2. PC2 / Database and persistence

Responsible for:

- receiving and storing data in MySQL;
- maintaining local simulation data;
- receiving migrated data from MongoDB;
- maintaining system persistence.

### 3. MongoDB

The project uses MongoDB as the ingestion and event storage database, with replicas for fault tolerance.

Main stored data:

- marsami movements;
- temperature;
- noise;
- occupancy per room;
- system events;
- alerts.

### 4. MySQL

The MySQL database is used to:

- store system configuration;
- maintain simulations and application state;
- store historical data for user/web queries;
- provide data for dashboards and monitoring tools.

---

## Databases

### Local MySQL

The project uses a local database called `maze_local`, which may be modified by the group as needed.

Some relevant tables:

- `Simulacao`
- `SetupMaze`
- `ConfiguracaoSistema`
- `Corridor`
- `Utilizador`
- `Temperatura`
- `Som`
- `MedicoesPassagens`
- `Mensagens`
- `OcupacaoLabirinto`

### Cloud MySQL

There is also a cloud database, called `maze`, accessible via:

- host: `194.210.86.10`
- username: `aluno`
- password: `aluno`

The values in this database must not be changed during a simulation.

---

## MongoDB and incremental migration

The system first stores events in MongoDB and then migrates that data to MySQL.

The migrations:

- are performed automatically and in real time;
- may fail under certain circumstances;
- require a reset mechanism when a failure occurs.

The migration logic is implemented in Python modules that read not-yet-migrated records and write them to MySQL.

---

## Android and monitoring

Each team must be able to monitor the system evolution through an Android mobile device.

Expected features:

- chart with the number of marsamis per room;
- temperature chart;
- noise chart;
- danger alerts for excessive temperature or noise;
- real-time visualization of maze state.

---

## Users and administration

There is an application administrator who:

- creates and deletes users and teams;
- manages simulations;
- coordinates system parameters.

Teams have access to HTML/PHP forms to:

- log in;
- create simulations;
- start simulations;
- change relevant parameters;
- visualize data and monitor the system.

Users may only modify data from the simulation they created.

---

## Project execution flow

1. Start the Docker services with MySQL, MongoDB, and phpMyAdmin.
2. Import the `maze_local` database.
3. Start the MQTT broker.
4. Run the main Python pipeline for the system.
5. Receive sensor data and process it in real time.
6. Persist events in MongoDB.
7. Migrate the data to MySQL.
8. Consult the system state via PHP, dashboard, or Android.

---

## Repository structure

```text
Distributed-Maze-System/
├── README.md
├── run_pipeline.py
├── main1_pc1.py
├── main2_pc1.py
├── main_pc2.py
├── core/
│   ├── alert_engine.py
│   ├── config_manager.py
│   ├── decision_engine.py
│   ├── event_processor.py
│   └── state_engine.py
├── mqtt/
│   └── mqtt_listener.py
├── persistance/
│   ├── migration_worker.py
│   ├── mongo_repository.py
│   └── mysql_writer.py
├── docker/
│   ├── README_BD.md
│   └── mysql_files/
├── docker_file/
│   └── docker-compose.yml
├── maze_app_php/
├── site/
└── servers/
```

---

## Main technologies

- Python
- MQTT
- MongoDB
- MySQL
- PHP
- Docker
- Android (graphical monitoring)

---

## Important notes

- The project assumes that the infrastructure services run in Docker.
- It is not recommended to install MySQL or MongoDB locally unless necessary.
- The system was designed with a focus on distribution, redundancy, and fault tolerance.
- The MQTT broker is essential for communication between modules and players.
- The logic for outlier detection and odd/even balance is central to the score system.

---

## Conclusion

This project implements a distributed solution for monitoring and controlling a maze by combining sensors, MQTT, simulation, real-time processing, and persistence across multiple databases. Its architecture aims to reproduce a realistic distributed systems scenario with fault tolerance, incremental data migration, and integration of different technologies.

The main objective is to create a functional, robust, and extensible system capable of responding in real time to maze conditions and to the interaction between players and the environment.
