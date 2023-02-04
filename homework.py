import logging
import os
import time

import requests
import telegram

from dotenv import load_dotenv

from exceptions import (TokenMissingException,
                        ResponseKeysMissingException,
                        InvalidHomeworkStatusException,
                        UnavailableEndpointException)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s'
)


def check_tokens():
    """Check if all tokens and chat_id exist.
    Return: True if all tokens exist and Fa if not.
    """
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for key, value in tokens.items():
        if value is None:
            message = (
                f'Отсутствует обязательная переменная окружения: {key} \n'
                'Программа принудительно остановлена.'
            )
            logging.critical(message)
            raise TokenMissingException(message)


def send_message(bot, message):
    """Send given message to TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Бот отправил сообщение {message}')
    except Exception as error:
        logging.error(
            f'Произошел сбой при отправке сообщения в Telegram: {error}'
        )


def get_api_answer(timestamp):
    """Get response from ENDPOINT API from last update=timestamp until now."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        response_status = response.status_code
        if response_status != 200:
            message = (
                f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен. '
                f'Код ответа API: {response.status_code}'
            )
            raise UnavailableEndpointException(message)
        return response.json()
    except UnavailableEndpointException:
        logging.error(message)
    except Exception:
        logging.error(message)


def check_response(response):
    """Check if response is dict and at least one of its values is list."""
    try:
        if not all(
            (isinstance(response, dict),
             isinstance(response['homeworks'], list))
        ):
            raise TypeError(
                'Структура данных не соответствует ожиданиям'
            )
        response_keys = ('current_date', 'homeworks')
        keys = response.keys()
        for key in response_keys:
            if key not in keys:
                message = f'Ключ {key} отсутсвует в ответе API'
                raise ResponseKeysMissingException(message)
        return True
    except TypeError:
        logging.error('Структура данных не соответствует ожиданиям')
        return False
    except ResponseKeysMissingException:
        logging.error(message)
        return False


def parse_status(homework):
    """Check status of given homework.
    Return verdict according to HOMEWORK_VERDICTS.
    """
    try:
        homework_keys = ('homework_name', 'status')
        for key in homework_keys:
            if key not in homework.keys():
                raise ResponseKeysMissingException(
                    f'В ответе API домашки нет ключа {key}'
                )
        homework_name = homework.get('homework_name')
        status = homework.get('status')
        if status not in HOMEWORK_VERDICTS.keys():
            message = (
                f'Неожиданный статус {status} домашней работы {homework_name}'
            )
            raise InvalidHomeworkStatusException(message)
        verdict = HOMEWORK_VERDICTS.get(status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except ResponseKeysMissingException:
        logging.error(
            'В ответе API домашки нет ключа "homework_name"'
        )
    except InvalidHomeworkStatusException:
        logging.error(message)


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            if check_response(response):
                homeworks = response.get('homeworks')
                timestamp = response.get('current_date')
                if not homeworks:
                    logging.debug('Изменения в статусах отсутствуют')
                else:
                    for homework in homeworks:
                        message = parse_status(homework)
                        send_message(bot, message)
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)


if __name__ == '__main__':
    main()
