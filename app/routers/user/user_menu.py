# -*- coding: utf- 8 -*-
import asyncio

from datetime import datetime
from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from data.config import *
from database import *
from utils.functions import *
from keyboards import *
from .. import main_start

router = Router(name=__name__)






################################################################################
################################### MESSAGE ####################################

# Сделать заказ
@router.message(F.text == 'Сделать заказ')
async def create_order(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	await state.set_state('input_create_order')
	
	this_state = 'point_of_work'
	msg = await message.answer('Сделать заказ\nВопрос: <i>Суть работы (Техническое задание)</i>', reply_markup=kb_create_order(this_state))
	await state.update_data(this_state=this_state, msgs=[message, msg])

# Подать заявку на кодера\дизайнера
@router.message(F.text == 'Подать заявку в студию')
async def create_coder(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	msg = await message.answer('Выберите кем хотите быть', reply_markup=kb_choose_profession())



@router.callback_query(F.data.startswith('user'))
async def callback_user(call: CallbackQuery, bot: Bot, state: FSMContext, custom_data: str = None):
	await state.clear()
	cd = custom_data.split(':') if custom_data else call.data.split(':')

	if cd[1] == 'req':
		if cd[2] == 'menu':
			await call.message.edit_text('Выберите кем хотите быть', reply_markup=kb_choose_profession())

		elif cd[2] == 'coder':
			await state.set_state('input_create_coder')
			this_state = 'age'
			msg = await call.message.edit_text('Заявка на кодера\nВопрос: <i>Возраст</i>', reply_markup=kb_create_coder(this_state))
			await state.update_data(this_state=this_state, msgs=[msg])

		elif cd[2] == 'designer':
			await state.set_state('input_create_designer')
			this_state = 'age'
			msg = await call.message.edit_text('Заявка на дизайнера\nВопрос: <i>Возраст</i>', reply_markup=kb_create_designer(this_state))
			await state.update_data(this_state=this_state, msgs=[msg])




# Ответы на вопросы
@router.message(F.text == 'Информация')
async def faq(message: Message, bot: Bot, state: FSMContext):
	await state.clear()

	await message.answer('Информация', disable_web_page_preview=True, reply_markup=kb_info())

################################################################################
################################### CALLBACK ###################################

# Обработка меню пользователя
@router.callback_query(F.data.startswith('user:'))
async def user_callback(call: CallbackQuery, bot: Bot, state: FSMContext):
	cd = call.data.split(':')
	tg_user_id, username, firstname = get_user(call)
	bot_info = await get_bot_info(bot)

	# Профиль пользователя
	if cd[1] == 'menu':
		user = await Userx.get(tg_user_id=tg_user_id)
		user_sub = await UserSubx.get(user_id=user.id)
		
		register_date = datetime.strftime(datetime.fromtimestamp(user.unix), '%d.%m.%Y')
		if user_sub: sub_expiration = f'до окончания {time_to_text(user_sub.unix + user_sub.duration - get_unix(), True)}'
		else: sub_expiration = 'неактивна'
		
		await call.message.edit_text(
			f'\n<b>📱 Ваш профиль:</b>\n<i>Основная информация</i>\n\n🔑 ID:  <code>{tg_user_id}</code>\n🕜 Регистрация:  <code>{register_date}</code>\n\n💵 Подписка:  <code>{sub_expiration}</code>\n💳 Баланс:  <code>{user.balance} ₽</code>\n\n🎖 Ранг:  <code>🌟 Elite</code>\n📞 Слотов занято:  <code>0 из 2</code>\n⚙️ Лимит задач в сутки:  <code>0 из 30</code>\n🤍 Белый список:  <code>0 из 2</code>',
			reply_markup=kb_user_menu(tg_user_id)
		)


	# Пополнение баланса
	elif cd[1] == 'refill':

		# Выдача формы для оплаты
		if len(cd) == 4:
			refill_amount = parse_num(cd[2])
			if not refill_amount:
				return await call.answer('Не удалось получить сумму для пополнения, попробуй чуть позже')
			
			refill_service = cd[3]
			if refill_service not in ['crystalpay', 'aaio', 'payok']:
				return await call.answer('Платежная система временно недоступна, используйте другую')

			status, (refill_id, refill_url) = await refill_create(tg_user_id, refill_amount, refill_service)
			if not status:
				return await call.message.edit_text('❌ <b>Неудалось создать оплату</b> ❌', reply_markup=kb_back(f'user:refill:{refill_amount}'))
			
			await call.message.edit_text(f'<b>💰 Пополнить баланс</b>\nСумма:  <code>{refill_amount} ₽</code>\n\n<i>❔ Нажми на кнопку ниже чтобы открыть форму оплаты.\nПосле оплаты средства будут автоматически начислены на твой баланс.</i>\n\n<b>❗️ ВАЖНО:</b> <i>Переводите только ту сумму, что указана на странице, в противном случае средства могут быть утеряны!</i>\n\n<b>☹️ Платёж не дошёл или другая проблема?</b>\n<i>Напиши нам - {username_support}, приложив к сообщению скриншот чека.</i>', reply_markup=kb_refill(refill_amount, refill_service, refill_url))
		
		# Выбор платежной системы
		elif len(cd) == 3:
			refill_amount = parse_num(cd[2])
			if not refill_amount:
				return await call.answer('Не удалось получить сумму для пополнения, попробуй чуть позже')
			await call.message.edit_text(f'<b>💰 Пополнить баланс</b>\nСумма:  <code>{refill_amount} ₽</code>\n\n<i>❔ Выбери способ оплаты</i>', reply_markup=kb_refill(refill_amount))
		
		# Выбор суммы пополнения
		elif len(cd) == 2:
			await state.set_state('input_refill_amount')
			msg = await call.message.edit_text('<b>💰 Пополнить баланс</b>\n<i>Отправь мне сумму на которую хочешь пополнить баланс или выбери один из предложенных вариантов</i>', reply_markup=kb_refill())
			await state.update_data(msg=msg)

	elif cd[1] == 'sub_menu':
		user_sub = await UserSubx.get(tg_user_id=tg_user_id)
		if user_sub:
			sub_expiration = date_to_text(user_sub.unix + user_sub.duration)
			sub_duration = time_to_text(user_sub.duration)
			await call.message.edit_text(f'<b>💠 Подписка</b>\n\n<i>Название:</i> <b>{user_sub.name}</b>\n\n<i>Длительность:</i>  <code>60 минут</code>\n<i>Стоимость:</i>  <code>{user_sub.price} ₽</code>\n\n<i>Дата окончания подписки:</i>  <code>{sub_expiration}</code>', reply_markup=await kb_sub())
		else:
			await call.message.edit_text('<b>💵 Подписка</b>\n<i>Даёт доступ к «Обычному флуду» и снижает стоимость «Бесконечного флуда»</i>', reply_markup=await kb_sub(user_sub))

	elif cd[1] == 'sub':
		user_sub = await UserSubx.get(tg_user_id=tg_user_id)
		if len(cd) == 4:
			sub_id = parse_num(cd[2])
			user = await Userx.get(tg_user_id=tg_user_id)
			this_sub = await Subx.get(id=sub_id)
			sub_price = this_sub.price

			if sub_price > user.balance:
				balance_to_up = sub_price - user.balance
				return await call.message.edit_text(f'<b>⚠️ Недостаточно средств</b>\n<i>Для пополнения баланса нажми на кнопку ниже</i>\n\nТвой баланс:  <code>{user.balance} ₽</code>', reply_markup=kb_force_refill(balance_to_up, f'user:sub:{sub_id}'))

			sub = await TxnSubx.buy(user_id=user.id, sub_id=this_sub.id)
			if not sub:
				return await call.answer('❌ Во время покупки подписки произошла ошибка, попробуйте позжее', show_alert=True)

			await call.message.edit_text('Подписка успешно куплена', reply_markup=kb_back())
		elif len(cd) == 3:
			sub_id = parse_num(cd[2])
			user = await Userx.get(tg_user_id=tg_user_id)
			this_sub = await Subx.get(id=sub_id)
			sub_price = this_sub.price
			await call.message.edit_text(f'<b>💵 Подтверждение покупки</b>\n<i>Для продолжения тебе необходимо подтвердить списание средств, нажав соответствующую кнопку</i>\n\n🔥 Покупка подписки на  <code>60 минут</code>\n💰 Стоимость:  <code>{sub_price} ₽</code>\n\nДоступный баланс:  <code>{user.balance} ₽</code>', reply_markup=await kb_sub(user_sub, sub_id))
		elif len(cd) == 2:
			await call.message.edit_text('<b>💵 Подписка</b>\n<i>Даёт доступ к «Обычному флуду» и снижает стоимость «Бесконечного флуда»</i>', reply_markup=await kb_sub(user_sub))


	elif cd[1] == 'rank':
		await call.message.edit_text('<b>🎖 Ранги</b>\n<i>Выбери интересующий тебя ранг с помощью кнопок ниже, после чего нажми на кнопку «Хочу этот ранг»</i>\n\n· • ⦁  <code>{rank.name}</code>   ⦁ • ·\n\n📞 Слотов:  <code>2 шт.</code>\n⚙️ Суточный лимит:  <code>30 задач в день</code>\n🤍 Белый список:  <code>2 номера</code>\n💰 Цена:  <code>199 ₽</code>\n\n<i>❗️ У тебя уже есть этот ранг</i>', reply_markup=kb_rank())


	elif cd[1] == 'coupon':
		await call.answer('coupon')


	# Реферальная система
	elif cd[1] == 'referral':
		referral_all = 0 # Количество рефералов
		referral_active = 0 # Количество активных рефералов
		referral_profit = 0 # Профит с рефералов
		await call.message.edit_text(
			f'<b>💙 Реферальная система 💙</b>\n\n<b>🔗 Ссылка:</b>\n<code>t.me/{bot_info.username}?start=ref_{tg_user_id}</code>\n<i>📘 Наша реферальная система позволит вам заработать крупную сумму без вложений. Вам необходимо лишь давать свою ссылку друзьям и вы будете получать пожизненно <code>{int(referral_percent*100)}%</code> с их пополнений в боте</i>\n\n💙 Количество рефералов:  <code>{referral_all}</code>\n💙 Количество активных рефералов:  <code>{referral_active}</code>\n🛍 Заработано с рефералов:  <code>{referral_profit} руб</code>',
			disable_web_page_preview=True,
			reply_markup=kb_back()
		)
	elif cd[1] == 'terms':
		await call.message.edit_text(
			f'<b>⚖️ Условия использования</b>\n<i>Последнее обновление: 22 февраля 2024</i>\n\nСервис является посредником в доставке SMS сообщений и звонков через интернет-ресурсы находящиеся в публичном доступе для физических и юридических лиц, в режиме реального времени.\n\nЗапросы на получение SMS и звонков в отношении физического лица допустимо исполнять только при наличии у Вас письменного согласия на обработку его персональных данных и получения SMS сообщений и звонков. Работа сервиса ведется в рамках Федеральных законов от 27 июля 2006 года, № 152-ФЗ «О персональных данных», ФЗ №126 «О связи» от 07.07.2003 года (поправки от 21.07.2014 года), ФЗ №38 «О рекламе» от 13.03.2006 года, в соответствии с которыми обработка персональных данных и рассылка осуществляются только с согласия субъекта персональных данных.\n\nВыполняя рассылку SMS и звонков, Вы автоматически подтверждаете наличие такого согласия и принимаете <a href="https://telegra.ph/personal-data-02-08">Политику в отношении обработки персональных данных</a> и <a href="https://telegra.ph/terms-of-use-02-08">Пользовательское соглашение</a>.',
			disable_web_page_preview=True,
			reply_markup=kb_terms()
		)


@router.callback_query(F.data.startswith('faq:'))
async def faq_callback(call: CallbackQuery, bot: Bot, state: FSMContext):
	cd = call.data.split(':')
	
	faq_item_key = cd[1]
	faq_item = faq_text.get(faq_item_key)
	if not faq_item:
		await call.answer('♦️ Не удалось найти ответ на вопрос', show_alert=True)
		faq_item = faq_text.items()[0]
		faq_item_key = faq_item[0]
		faq_item = faq_item[1]

	await call.message.edit_text(
		f'<b>❓ {faq_item["title"]}</b>\n\n{faq_item["content"]}',
		disable_web_page_preview=True,
		reply_markup=kb_faq(faq_item_key)
	)














### Создание заказа
@router.message(StateFilter('input_create_order'))
async def state_input_create_order(message: Message, bot: Bot, state: FSMContext, custom_data: str = None):
	mt = custom_data if custom_data else message.text
	state_data = await state.get_data()

	this_state = state_data.get('this_state', 'start')
	answers = state_data.get('answers', {})
	msgs = state_data.get('msgs', [])
	
	if this_state == 'start':
		this_state = 'point_of_work'
		msg = await message.answer('Сделать заказ\nВопрос: <i>Суть работы (Техническое задание)</i>', reply_markup=kb_create_order(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'point_of_work':
		this_state = 'deadline'
		answers['point_of_work'] = mt
		msg = await message.answer('Сделать заказ\nВопрос: <i>Желаемые сроки выполнения работы</i>', reply_markup=kb_create_order(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'deadline':
		this_state = 'budget'
		answers['deadline'] = mt
		msg = await message.answer('Сделать заказ\nВопрос: <i>Бюджет</i>', reply_markup=kb_create_order(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'budget':
		this_state = 'create'
		answers['budget'] = mt
		msg = await message.answer(f'Сделать заказ\nПодтвердите создание заказа:\npoint_of_work: {answers["point_of_work"]}\ndeadline: {answers["deadline"]}\nbudget: {answers["budget"]}', reply_markup=kb_create_order(this_state))
		msgs.append(message)
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

@router.callback_query(StateFilter('input_create_order'))
async def state_input_create_order_(call: CallbackQuery, bot: Bot, state: FSMContext):
	cd = call.data.split(':')[1:]
	state_data = await state.get_data()
	tg_user_id, username, firstname = get_user(call)

	this_state = state_data.get('this_state', None)
	answers = state_data.get('answers', {})
	msgs = state_data.get('msgs', [])

	if cd[0] == 'cst':
		states = {'point_of_work': 'menu', 'deadline': 'start', 'budget': 'point_of_work'}
		this_state = states.get(cd[1], list(states.values())[0])

		await state.update_data(this_state=this_state)

		if this_state == 'menu':
			await state.clear()
			await main_start.utils(call, bot, state, 'utils:menu:main')
			await del_message(*msgs)

		elif this_state in ['start', 'point_of_work', 'deadline']:
			await del_message(call.message)
			await state_input_create_order(call.message, bot, state, answers.get(this_state, ''))

	elif cd[0] == 'cod' and this_state == 'create':
		await state.clear()
		this_state = 'created'

		if cd[1] == 'y':
			user = await Userx.get(tg_user_id=tg_user_id)
			order = await Orderx.add(user_id=user.id, point_of_work=answers.get('point_of_work', 'Не указано'), deadline=answers.get('deadline', 'Не указано'), budget=answers.get('budget', 'Не указано'))
			if order:
				await call.message.edit_text(f'Заказ создан\nID: {order.id}', reply_markup=kb_create_order(this_state))
			else:
				await call.message.edit_text(f'Не удалось создать заказ\nАдминистратор уведомлён', reply_markup=kb_create_order(this_state))
		elif cd[1] == 'n':
			msg = await call.message.edit_text(f'Создание заказа отменено', reply_markup=kb_create_order(this_state))
		
		await del_message(*msgs)
	else:
		await del_message(message)




# Принятие заявки кодера
@router.message(StateFilter('input_create_coder'))
async def state_input_create_coder(message: Message, bot: Bot, state: FSMContext, custom_data: str = None):
	mt = custom_data if custom_data else message.text
	state_data = await state.get_data()

	this_state = state_data.get('this_state', 'start')
	answers = state_data.get('answers', {})
	msgs = state_data.get('msgs', [])
	
	if this_state == 'start':
		this_state = 'age'
		msg = await message.answer('Заявка на кодера\nВопрос: <i>Возраст</i>', reply_markup=kb_create_coder(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'age':
		this_state = 'stack'
		answers['age'] = mt
		msg = await message.answer('Заявка на кодера\nВопрос: <i>Стек навыков</i>', reply_markup=kb_create_coder(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'stack':
		this_state = 'portfolio'
		answers['stack'] = mt
		msg = await message.answer('Заявка на кодера\nВопрос: <i>Портфолио/Примеры работ</i>', reply_markup=kb_create_coder(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'portfolio':
		this_state = 'extra_information'
		answers['portfolio'] = mt
		msg = await message.answer('Заявка на кодера\nВопрос: <i>Дополнительная информация</i>', reply_markup=kb_create_coder(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'extra_information':
		this_state = 'complete_test_task'
		answers['extra_information'] = mt
		await message.answer('Заявка на кодера\nВопрос: <i>Готовы выполнить тестовое задание?</i>', reply_markup=kb_create_coder(this_state))
		msgs.append(message)
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)
	else:
		await del_message(message)
@router.callback_query(StateFilter('input_create_coder'))
async def state_input_create_coder_(call: CallbackQuery, bot: Bot, state: FSMContext):
	cd = call.data.split(':')[1:]
	state_data = await state.get_data()
	tg_user_id, username, firstname = get_user(call)

	this_state = state_data.get('this_state', None)
	answers = state_data.get('answers', {})
	msgs = state_data.get('msgs', [])
	print(cd, this_state)

	if cd[0] == 'cst':
		states = {'age': 'menu', 'stack': 'start', 'portfolio': 'age', 'extra_information': 'stack', 'complete_test_task': 'portfolio'}
		this_state = states.get(cd[1], list(states.values())[0])

		await state.update_data(this_state=this_state)

		if this_state == 'menu':
			await state.clear()
			await callback_user(call, bot, state, 'user:req:menu')
			if len(msgs) > 1:
				await del_message(*msgs)

		elif this_state in ['start', 'age', 'stack', 'portfolio']:
			await del_message(call.message)
			await state_input_create_coder(call.message, bot, state, answers.get(this_state, ''))

	elif cd[0] == 'acd':
		if this_state == 'complete_test_task':
			this_state = 'create'
			answers['complete_test_task'] = (cd[1] == 'y')
			await call.message.edit_text(f'Заявка на кодера\nПодтвердите данные заявки на кодера:\nage: {answers["age"]}\nstack: {answers["stack"]}\nportfolio: {answers["portfolio"]}\nextra_information: {answers["extra_information"]}\ncomplete_test_task: {"Да" if answers["complete_test_task"] else "Нет"}', reply_markup=kb_create_coder(this_state))
			await state.update_data(this_state=this_state, answers=answers)

	elif cd[0] == 'cod' and this_state == 'create':
		await state.clear()
		this_state = 'created'

		if cd[1] == 'y':
			user = await Userx.get(tg_user_id=tg_user_id)
			coder = await Coderx.add(user_id=user.id, age=answers.get('age', 'Не указано'), stack=answers.get('stack', 'Не указано'), portfolio=answers.get('portfolio', 'Не указано'), extra_information=answers.get('extra_information', 'Не указано'), complete_test_task=answers.get('complete_test_task', False))
			if coder:
				await call.message.edit_text(f'Заявка создана\nID: {coder.id}', reply_markup=kb_create_coder(this_state))
			else:
				await call.message.edit_text(f'Не удалось создать заявку\nАдминистратор уведомлён', reply_markup=kb_create_coder(this_state))
		elif cd[1] == 'n':
			msg = await call.message.edit_text(f'Создание заявки отменено', reply_markup=kb_create_coder(this_state))
		
		await del_message(*msgs)




# Принятие заявки дизайнера
@router.message(StateFilter('input_create_designer'))
async def state_input_create_designer(message: Message, bot: Bot, state: FSMContext, custom_data: str = None):
	mt = custom_data if custom_data else message.text
	state_data = await state.get_data()

	this_state = state_data.get('this_state', 'start')
	answers = state_data.get('answers', {})
	msgs = state_data.get('msgs', [])
	
	if this_state == 'start':
		this_state = 'age'
		msg = await message.answer('Заявка на дизайнера\nВопрос: <i>Возраст</i>', reply_markup=kb_create_designer(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'age':
		this_state = 'stack'
		answers['age'] = mt
		msg = await message.answer('Заявка на дизайнера\nВопрос: <i>Используемые программы</i>', reply_markup=kb_create_designer(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'stack':
		this_state = 'services_provided'
		answers['stack'] = mt
		msg = await message.answer('Заявка на дизайнера\nВопрос: <i>Предоставляемые услуги (Например: 2D/3D/Арты/Анимация/Статика и прочее)</i>', reply_markup=kb_create_designer(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'services_provided':
		this_state = 'extra_information'
		answers['services_provided'] = mt
		msg = await message.answer('Заявка на дизайнера\nВопрос: <i>Дополнительная информация</i>', reply_markup=kb_create_designer(this_state))
		msgs.extend([message, msg])
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)

	elif this_state == 'extra_information':
		this_state = 'create'
		answers['extra_information'] = mt
		await message.answer(f'Заявка на дизайнера\nПодтвердите данные заявки на дизайнера:\nage: {answers["age"]}\nstack: {answers["stack"]}\nservices_provided: {answers["services_provided"]}\nextra_information: {answers["extra_information"]}', reply_markup=kb_create_designer(this_state))
		msgs.append(message)
		await state.update_data(this_state=this_state, answers=answers, msgs=msgs)
	else:
		await del_message(message)
@router.callback_query(StateFilter('input_create_designer'))
async def state_input_create_designer_(call: CallbackQuery, bot: Bot, state: FSMContext):
	cd = call.data.split(':')[1:]
	state_data = await state.get_data()
	tg_user_id, username, firstname = get_user(call)

	this_state = state_data.get('this_state', None)
	answers = state_data.get('answers', {})
	msgs = state_data.get('msgs', [])

	if cd[0] == 'cst':
		states = {'age': 'menu', 'stack': 'start', 'services_provided': 'age', 'extra_information': 'stack'}
		this_state = states.get(cd[1], list(states.values())[0])

		await state.update_data(this_state=this_state)

		if this_state == 'menu':
			await state.clear()
			await callback_user(call, bot, state, 'user:req:menu')
			if len(msgs) > 1:
				await del_message(*msgs)

		elif this_state in ['start', 'age', 'stack']:
			await del_message(call.message)
			await state_input_create_designer(call.message, bot, state, answers.get(this_state, ''))

	elif cd[0] == 'cod' and this_state == 'create':
		await state.clear()
		this_state = 'created'

		if cd[1] == 'y':
			user = await Userx.get(tg_user_id=tg_user_id)
			designer = await Designerx.add(user_id=user.id, age=answers.get('age', 'Не указано'), stack=answers.get('stack', 'Не указано'), services_provided=answers.get('services_provided', 'Не указано'), extra_information=answers.get('extra_information', 'Не указано'))
			if designer:
				await call.message.edit_text(f'Заявка создана\nID: {designer.id}', reply_markup=kb_create_designer(this_state))
			else:
				await call.message.edit_text(f'Не удалось создать заявку\nАдминистратор уведомлён', reply_markup=kb_create_designer(this_state))
		elif cd[1] == 'n':
			msg = await call.message.edit_text(f'Создание заявки отменено', reply_markup=kb_create_designer(this_state))
		
		await del_message(*msgs)