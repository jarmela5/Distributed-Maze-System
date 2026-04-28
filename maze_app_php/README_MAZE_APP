# Configuração do Backend Android

## 1. Copiar os ficheiros do backend (Pasta `src`)
O Docker mapeia a pasta local `src/` do seu PC para `/var/www/html/` dentro do container. 

**Ação:** Coloque a pasta `maze_app_php/` dentro da diretoria `src/` do seu projeto.

A estrutura final deverá ficar:
`[Pasta-do-Projeto]/src/maze_app_php/`

**Conteúdo obrigatório:** Esta pasta deve conter os ficheiros `login.php`, `get_temperature_data.php`, `get_min_max_temp_values.php`, entre outros.

## 2. Testar a ligação no Navegador
Antes de usar a aplicação, confirme que o servidor está a responder corretamente abrindo o navegador no seguinte endereço:

[http://localhost:9000/maze_app_php/get_temperature_data.php?username=admin&password=admin&database=maze_local](http://localhost:9000/maze_app_php/get_temperature_data.php?username=admin&password=admin&database=maze_local)

## 3. Configuração na Aplicação Android
Ao abrir a aplicação no emulador, preencha os campos de ligação da seguinte forma:

* **Host:** `10.0.2.2:9000` (Endereço padrão para o emulador aceder ao localhost do PC).
* **Username:** O seu utilizador da base de dados (ex: `admin`).
* **Password:** A sua password da base de dados.
* **Database:** `maze_local` (O nome da base de dados configurada no MySQL).

## Notas Importantes
* **Docker:** Certifique-se de que os containers Docker estão em execução.
* **Base de Dados:** Confirme que a base de dados se chama exatamente `maze_local` e que a tabela `utilizadores` contém as credenciais que está a usar.
* **Erros de Formato:** Se a aplicação apresentar "Erro no formato da resposta", verifique se o PHP está a devolver um JSON válido e se não existem erros de ligação ao MySQL impressos no ecrã.