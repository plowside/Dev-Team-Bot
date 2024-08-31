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

# Меню админа
@router.message(F.text == '🧑🏻‍💻 Админ меню')
async def create_order(message: Message, bot: Bot, state: FSMContext):
	tg_user_id, username, firstname = get_user(message)
	await state.clear()

	await message.answer('🧑🏻‍💻 Админ меню', reply_markup=kb_admin_menu(tg_user_id))