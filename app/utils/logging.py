# -*- coding: utf- 8 -*-
import logging, os

logs_path = 'logs'
os.makedirs(logs_path, exist_ok=True)
# Формат логгирования
log_formatter_file = logging.Formatter(u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s')
log_formatter_console = logging.Formatter(u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s')

# Логгирование в файл tgbot/data/logs.log
file_handler = logging.FileHandler(f'{logs_path}/latest.log', 'w', 'utf-8')
file_handler.setFormatter(log_formatter_file)
file_handler.setLevel(logging.INFO)

# Логгирование в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter_console)
console_handler.setLevel(logging.INFO)
logging.getLogger('aiogram').setLevel(logging.WARNING)

# Подключение настроек логгирования
logging.basicConfig(
	format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
	handlers=[
		file_handler,
		console_handler
	],
	level=logging.INFO
)