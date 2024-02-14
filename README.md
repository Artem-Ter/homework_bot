# Telegram bot to check homework status on Yandex.Practicum platform using API.


## Project description:

The Telegram bot to check homework status at Yandex.Practicum. The status is checked every 10 minutes.

Access to API by token using JSON. API adress:
```
https://practicum.yandex.ru/api/user_api/homework_statuses/. 
```

## How to launch a project:

Clone the repository and switch to it on the command line:

```
https://github.com/Artem-Ter/homework_bot.git
```

```
cd homework_bot
```

Create and activate virtual environment:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Install dependencies from a file:

```
pip install -r requirements.txt
```


Start project:

```
python3 homework.py
```

## Technologies used:

- Python,
- Python Telegram Bot.
- logging,
- requests.

## Project author:
[Artem Tereschenko](https://github.com/Artem-Ter)

