import json

### TELEGRAM ###
telegram_token = '7306244866:AAG8kB3Uwhx71sxJ-FrhgLBDTBNQd2eeYWI' # Токен телеграм бота
admin_ids = [6315225351, 6554101798] # ID админов
moderator_ids = [5749609907, 7321334922] # ID модераторов
filestorage_id = -1002177894042 # ID чата для хранения файлов
## URL ##
url_administrator = 'https://t.me/plowside'
url_portfolio = 'https://t.me/plowside'

### GENERAL ###
database_config = {
	'user': 'postgres',
	'password': 'plowside',
	'database_name': 'dev_team',
	'host': 'localhost',
	'port': 5432
}

req_questions = {
	'order': {
		'programming': {
			'development_reason': {
				'q': 'Разработка:',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Телеграм-бот': 'Телеграм-бот', 'Веб-сайт': 'Веб-сайт'}
				]
			},
			'programming_language': {
				'q': 'Язык программирования:',
				'skipable': True,
				'is_file': False,
				'inline_kb': [
					{'Python': 'Python', 'C#': 'C#'},
					{'GO': 'GO', 'JavaScript': 'JavaScript'}
				]
			},
			'deadline': {
				'q': 'Желаемые сроки выполнения:',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'examples': {
				'q': 'Примеры:',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			},
			'budget': {
				'q': 'Бюджет:',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Договорной': 'Договорной'}
				]
			},
			'technical_specification': {
				'q': 'Техническое задание:',
				'skipable': False,
				'is_file': True,
				'reply_kb': []
			}
		},

		'design': {
			'design_reason': {
				'q': 'Оформление:',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Аватар': 'Аватар', 'Баннер': 'Баннер'},
					{'Сайт': 'Сайт'}
				]
			},
			'style': {
				'q': 'Стиль:',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'2D': '2D', '3D': '3D'},
					{'Статика': 'Статика', 'Анимация': 'Анимация'}
				]
			},
			'deadline': {
				'q': 'Желаемые сроки выполнения:',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'examples': {
				'q': 'Примеры:',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			},
			'budget': {
				'q': 'Бюджет:',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Договорной': 'Договорной'}
				]
			},
			'colors': {
				'q': 'Цвета:',
				'skipable': False,
				'is_file': True,
				'reply_kb': []
			},
			'additional_info': {
				'q': 'Дополнительная информация:',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			}
		}
	},

	'application': {
		'coder': {
			'age': {
				'q': 'Возраст:',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'stack': {
				'q': 'Стек навыков:',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'portfolio': {
				'q': 'Портфолио/Примеры работ:',
				'skipable': False,
				'is_file': True,
				'reply_kb': []
			},
			'additional_info': {
				'q': 'Дополнительная информация:',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			},
			'complete_test_task': {
				'q': 'Готовы выполнить тестовое задание?',
				'bool': True,
				'inline_kb': [
					{'Да': 'True', 'Нет': 'False'}
				]
			}
		},

		'designer': {
			'age': {
				'q': 'Возраст:',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'using_programms': {
				'q': 'Используемые программы:',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'services_provided': {
				'q': 'Предоставляемые услуги:',
				'skipable': False,
				'is_file': True,
				'inline_kb': [
					{'2D': '2D', '3D': '3D'},
					{'Арты': 'Арты', 'Анимация': 'Анимация', 'Статика': 'Статика'},
				]
			},
			'additional_info': {
				'q': 'Дополнительная информация:',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			}
		}
	}
}

trns_all = {
	'kb_admin_requests': {'q': {'order': {'programming': 'Программирование', 'design': 'Дизайн'}, 'application': {'coder': 'Кодер', 'designer': 'Дизайнер'}}, 'type': {0: '⚪️ Все', 1: 'Заказы', 2: 'Заявки'}, 'status': {0: '⚪️ Все', 1: '🟢 Активные', 2: '🔴 Завершенные'}},
	'morph': {'order': {'l': {"i": "заказ", "r": "заказа", "d": "заказу", "v": "заказ", "t": "заказом", "p": "заказе"}, 'u': {"i": "Заказ", "r": "Заказа", "d": "Заказу", "v": "Заказ", "t": "Заказом", "p": "Заказе"}, 'end': {'n': 'ый', 'm': 'ые', 'zh': ''}}, 'application': {'l': {"i": "заявка", "r": "заявки", "d": "заявке", "v": "заявку", "t": "заявкой", "p": "заявке"}, 'u': {"i": "Заявка", "r": "Заявки", "d": "Заявке", "v": "Заявку", "t": "Заявкой", "p": "Заявке"}, 'end': {'n': 'ая', 'm': 'ые', 'zh': 'a'}}},
	'h1': {'order': 'Создание заказа\n', 'application': 'Создание заявки\n'},
	'indicators': {'emoji': {True: '🟢', False: '🔴'}, 'emoji2': {True: '🟡', False: '🔴'}}
}



##### ОБРАБОТКА #####