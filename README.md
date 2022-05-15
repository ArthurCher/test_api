# REST API

Структура
* server_queue.py - асинхронный сервер для создания очередей, клиенту создается свой поток с очередью запросов
* server.py - базовый класс для обработки запросов, все создаваемые приложения будут его наследовать
* api.py - основное приложение, для запуска сервера нужно запустить именно его

Сервер работает в двух режимах:
* Совершить транзакцию
* Получить историю транзакций клиента

В обоих случаях в запросе отправляется json:
* Для совершения транзакции:
`{
    "task":"make_transaction", # указывает тип задачи, который нужно выполнить - совершить транзакцию
    "user_id": 3, # id юзера, который совершает транзакцию
    "transaction": 212 # размер транзакции
  }`

* Для получения истории транзакции клиента:
`{
    "task":"get_history", # указывает тип задачи, который нужно выполнить - получить историю
    "user_id": 3, # id юзера, по которому нужно получить историю
  }`

Ответ получаем в формате json:
* При совершения транзакции:
`{
	"user_id": 3, # id юзера, совершившего транзакци/
	"transaction_status": true, # статус транзакции, False если недостаточно средств с выводом ошибки "error": "insufficient funds"
	"bakance": 32788.0 # оставшийся баланс после транзакции (если транзакция прошла)
}`

* При получении истории транзакции клиента
`
{
	"1652643804": {                       # id транзакции
		"user_id": 2,                     # id пользователя
		"transaction": 1250.0,            # Размер транзакции
		"status": "finish"                # Статус транзакции (blocked при недостатке средств)
	},
	"1652643832": {
		"user_id": 2,
		"transaction": 20000.0,
		"status": "blocked"
	},
	"1652643871": {
		"user_id": 2,
		"transaction": 2000.0,
		"status": "finish"
	}
}
`