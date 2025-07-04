import json

### TELEGRAM ###
telegram_token = '7306244866:AAHy6rQwm5LJiex5P4_gfuWvWbX6otI2Oc0' # Токен телеграм бота
admin_ids = [6315225351, 6554101798] # ID админов
moderator_ids = [5749609907, 7321334922] # ID модераторов
filestorage_id = -1002177894042 # ID чата для хранения файлов
## URL ##
url_administrator = 'https://t.me/KillaCoder'
url_portfolio = 'https://t.me/KillaPortfolio'
url_rules = 'https://telegra.ph/User-agreement-08-31-36'
url_tz = 'https://telegra.ph/technical-specification-08-31'

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
				'user_q': '<b>Что необходимо разработать?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Телеграм-бот': 'Телеграм-бот', 'Веб-сайт': 'Веб-сайт'},
					{'Чекер': 'Чекер','Софт': 'Софт'}
				]
			},
			'programming_language': {
				'q': 'Язык программирования:',
				'user_q': '<b>Какой язык программирования необходимо использовать?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': True,
				'is_file': False,
				'inline_kb': [
					{'Python': 'Python', 'JavaScript': 'JavaScript', 'C++': 'C++'},
					{'Golang': 'Golang', 'BAS': 'BAS', 'ZennoPoster': 'ZennoPoster'},
					{'React': 'React', 'Vue': 'Vue', 'PHP': 'PHP'}
				]
			},
			'deadline': {
				'q': 'Желаемые сроки выполнения:',
				'user_q': '<b>Сроки выполнения заказа?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': True,
				'is_file': False,
				'inline_kb': [
					{'От 1 До 7 дней': 'От 1 До 7 дней', 'От 7 До 14 дней': 'От 7 До 14 дней'},
					{'От 14 До 30 дней': 'От 14 До 30 дней', 'Больше 30 дней': 'Больше 30 дней'}
				]
			},
			'examples': {
				'q': 'Примеры:',
				'user_q': '<b>Примеры работ, которые Вам нужны</b>\n\n<i>♦️ Напишите свой вариант. Доступна отправка файлов.</i>',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			},
			'budget': {
				'q': 'Бюджет:',
				'user_q': '<b>Бюджет на разработку проекта</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных вариантов.</i>',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Меньше 50 $': 'Меньше 50 $', 'От 50 До 100 $': 'От 50 До 100 $'},
					{'От 100 До 500 $': 'От 100 До 500$', 'Больше 500 $': 'Больше 500 $'}
				]
			},
			'technical_specification': {
				'q': 'Техническое задание:',
				'user_q': '<b>Техническое задание</b>\n\n<i>♦️ Пришлите нам техническое задание для вашего проекта. Доступна отправка файлов.</i>',
				'skipable': False,
				'is_file': True,
				'reply_kb': []
			}
		},

		'design': {
			'design_reason': {
				'q': 'Оформление:',
				'user_q': '<b>Что необходимо оформить?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Аватар': 'Аватар', 'Баннер': 'Баннер'},
					{'Сайт': 'Сайт', 'Стикеры': 'Стикеры'}
				]
			},
			'style': {
				'q': 'Стиль:',
				'user_q': '<b>Какой нужен стиль оформления?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'2D - Статика': '2D - Статика', '2D - Анимация': '2D - Анимация'},
					{'3D - Статика': '3D - Статика', '3D - Анимация': '3D - Анимация'}
				]
			},
			'deadline': {
				'q': 'Желаемые сроки выполнения:',
				'user_q': '<b>Сроки выполнения заказа?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': True,
				'is_file': False,
				'inline_kb': [
					{'Меньше 24 часов': 'Меньше 24 часов', 'От 1 До 7 дней': 'От 1 До 7 дней'},
					{'От 7 До 14 дней': 'От 7 До 14 дней', 'Больше 14 дней': 'Больше 14 дней'}
				]
			},
			'examples': {
				'q': 'Примеры:',
				'user_q': '<b>Примеры работ, которые Вам нужны</b>\n\n<i>♦️ Напишите свой вариант. Доступна отправка файлов.</i>',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			},
			'budget': {
				'q': 'Бюджет:',
				'user_q': '<b>Бюджет на выполнение заказа</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Меньше 50 $': 'Меньше 50 $', 'От 50 До 100 $': 'От 50 До 100 $'},
					{'От 100 До 500 $': 'От 100 До 500$', 'Больше 500 $': 'Больше 500 $'}
				]
			},
			'colors': {
				'q': 'Цвета:',
				'user_q': '<b>Цвета, которые необходимо использовать</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': True,
				'is_file': True,
				'inline_kb': [
					{'Синий': 'Синий', 'Зеленый': 'Зеленый', 'Красный': 'Красный'},
					{'Желтый': 'Желтый', 'Оранжевый': 'Оранжевый', 'Фиолетовый': 'Фиолетовый'}
				]
			},
			'additional_info': {
				'q': 'Дополнительная информация:',
				'user_q': '<b>Дополнительная информация</b>\n\n<i>♦️ Пришлите нам техническое задание для вашего проекта. Доступна отправка файлов.</i>',
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
				'user_q': '<b>Ваш возраст?</b>\n\n<i>♦️ Напишите свой вариант.</i>',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'stack': {
				'q': 'Стек навыков:',
				'user_q': '<b>Укажите свой стек навыков</b>\n\n<i>♦️ Напишите свой вариант.</i>',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'portfolio': {
				'q': 'Портфолио/Примеры работ:',
				'user_q': '<b>Предоставьте портфолио или примеры работ</b>\n\n<i>♦️ Напишите свой вариант. Доступна отправка файлов.</i>',
				'skipable': False,
				'is_file': True,
				'reply_kb': []
			},
			'additional_info': {
				'q': 'Дополнительная информация:',
				'user_q': '<b>Укажите дополнительную информацию</b>\n\n<i>♦️ Напишите свой вариант. Доступна отправка файлов.</i>',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			},
			'complete_test_task': {
				'q': 'Готовы выполнить тестовое задание?',
				'user_q': '<b>Готовы выполнить тестовое задание?</b>\n\n<i>♦️ Выберите один из предложенных вариантов.</i>',
				'bool': True,
				'inline_kb': [
					{'Да': 'True', 'Нет': 'False'}
				]
			}
		},

		'designer': {
			'age': {
				'q': 'Возраст:',
				'user_q': '<b>Возраст</b>\n\n<i>♦️ Напишите свой вариант.</i>',
				'skipable': False,
				'is_file': False,
				'reply_kb': []
			},
			'using_programms': {
				'q': 'Используемые программы:',
				'user_q': '<b>Какие программы вы используете?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': False,
				'is_file': False,
				'inline_kb': [
					{'Photoshop': 'Photoshop', 'Figma': 'Figma'},
					{'Premiere': 'Premiere', 'After Effects': 'After Effects'},
				]
			},
			'services_provided': {
				'q': 'Предоставляемые услуги:',
				'user_q': '<b>Какие услуги вы предоставляете?</b>\n\n<i>♦️ Напишите свой вариант или выберите один из предложенных.</i>',
				'skipable': False,
				'is_file': True,
				'inline_kb': [
					{'2D - Статика': '2D - Статика', '2D - Анимация': '2D - Анимация'},
					{'3D - Статика': '3D - Статика', '3D - Анимация': '3D - Анимация'}
				]
			},
			'additional_info': {
				'q': 'Дополнительная информация:',
				'user_q': '<b>Укажите дополнительную информацию</b>\n\n<i>♦️ Напишите свой вариант. Доступна отправка файлов.</i>',
				'skipable': True,
				'is_file': True,
				'reply_kb': []
			}
		}
	}
}

trns_all = {
	'kb_admin_requests': {'q': {'order': {'programming': '⚙️ Программирование', 'design': '🖌 Дизайн'}, 'application': {'coder': '⚙️ Кодер', 'designer': '🖌 Дизайнер'}}, 'type': {0: '⚪️ Все', 1: 'Заказы', 2: 'Заявки'}, 'status': {0: '⚪️ Все', 1: '🟢 Активные', 2: '🔴 Завершенные'}},
	'morph': {'order': {'l': {"i": "заказ", "r": "заказа", "d": "заказу", "v": "заказ", "t": "заказом", "p": "заказе"}, 'u': {"i": "Заказ", "r": "Заказа", "d": "Заказу", "v": "Заказ", "t": "Заказом", "p": "Заказе"}, 'end': {'n': 'ый', 'm': 'ые', 'zh': ''}}, 'application': {'l': {"i": "заявка", "r": "заявки", "d": "заявке", "v": "заявку", "t": "заявкой", "p": "заявке"}, 'u': {"i": "Заявка", "r": "Заявки", "d": "Заявке", "v": "Заявку", "t": "Заявкой", "p": "Заявке"}, 'end': {'n': 'ая', 'm': 'ые', 'zh': 'a'}}},
	'h1': {'order': {'header': '<b>🔥 Сделать заказ</b>', 'req_name' :'Услуга: <code>{req_type_trns}</code>'}, 'application': {'header': '<b>💼 Вступить в студию</b>', 'req_name': 'Должность: <code>{req_type_trns}</code>'}},
	'indicators': {'emoji': {True: '🟢', False: '🔴'}, 'emoji2': {True: '🟡', False: '🔴'}}
}



##### ОБРАБОТКА #####