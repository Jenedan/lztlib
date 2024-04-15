from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils import message_utils
from keyboards import inline
from database import db as db

router = Router()

class States(StatesGroup):
    book_info = State()
    keyword = State()
    title = State()
    author = State()
    desc = State()
    genre = State()
    preview = State()

async def correct_msg(msg):
    if len(msg.text) < 5:
        text = await message_utils.add("error")
        return msg.answer(text)

'''Хандлер на команду /start'''
async def start(msg: Message, state: FSMContext):
    await state.clear()

    keyboard = await inline.start()
    text = await message_utils.start(msg.from_user.full_name)
    await msg.answer(text, reply_markup=keyboard)

'''Коллбек от кнопки назад'''
async def call_start(call: CallbackQuery, state: FSMContext):
    await state.clear()

    keyboard = await inline.start()
    text = await message_utils.start(call.from_user.full_name)
    await call.message.edit_text(text, reply_markup=keyboard)

'''Вывод списка всех книг'''
async def books_all(call: CallbackQuery):
    keyboard = await inline.books()
    text = await message_utils.books()
    await call.message.edit_text(text, reply_markup=keyboard)

'''Вывод подробностей о книге'''
async def book_info(call: CallbackQuery):
    book_id = call.data.split("_")[1]
    keyboard = await inline.delete(book_id)
    text = await message_utils.info(book_id)
    await call.message.edit_text(text, reply_markup=keyboard)

'''Удаление книги'''
async def book_delete(call: CallbackQuery):
    book_id = call.data.split("_")[1]
    keyboard = await inline.back()
    await db.remove_book(book_id)
    await call.message.edit_text("Книга успешно удалена!", reply_markup=keyboard)

'''Меню выбора метода поиска'''
async def books_find(call: CallbackQuery):
    keyboard = await inline.find()
    text = await message_utils.find("select")
    await call.message.edit_text(text, reply_markup=keyboard)

'''Поиск по жанру'''
async def find_genre(call: CallbackQuery):
    keyboard = await inline.genres()
    text = await message_utils.find("genre")
    await call.message.edit_text(text, reply_markup=keyboard)

'''Результаты поиска по жанру'''
async def genre_results(call: CallbackQuery):
    print(call.data)
    id = call.data.split("_")[1]
    keyboard = await inline.books("genre", id)
    text = await message_utils.books("genre", id)
    await call.message.edit_text(text, reply_markup=keyboard)

'''Поиск по ключевому слову'''
async def find_keyword(call: CallbackQuery, state: FSMContext):
    await state.set_state(States.keyword)

    keyboard = await inline.back()
    text = await message_utils.find("keyword")
    await call.message.edit_text(text, reply_markup=keyboard)

'''Результаты поиска по ключевому слову'''
async def keyword_results(msg: Message, state: FSMContext):
    await state.clear()

    keyboard = await inline.books("keyword", msg.text)
    text = await message_utils.books("keyword", msg.text)
    await msg.answer(text, reply_markup=keyboard)

'''Добавление книги, название книги'''
async def add_title(call: CallbackQuery, state: FSMContext):
    await state.set_state(States.title)
    keyboard = await inline.back()
    text = await message_utils.add("title")
    await call.message.edit_text(text, reply_markup=keyboard)

'''Добавление книги, автор'''
async def add_author(msg: Message, state: FSMContext):
    await correct_msg(msg)
    await state.update_data(title=msg.text)
    await state.set_state(States.author)
    text = await message_utils.add("author")
    keyboard = await inline.back()
    await msg.answer(text, reply_markup=keyboard)

'''Добавление книги, описание'''
async def add_desc(msg: Message, state: FSMContext):
    await correct_msg(msg)
    await state.update_data(author=msg.text)
    await state.set_state(States.desc)
    text = await message_utils.add("desc")
    keyboard = await inline.back()
    await msg.answer(text, reply_markup=keyboard)

'''Добавление книги, жанр'''
async def add_genre(msg: Message, state: FSMContext):
    await correct_msg(msg)
    await state.update_data(desc=msg.text)
    await state.set_state(States.genre)
    text = await message_utils.add("genre")
    keyboard = await inline.genres("add")
    await msg.answer(text, reply_markup=keyboard)

'''Выводим превью книги если кинули жанр сообщением'''
async def add_preview_text(msg: Message, state: FSMContext):
    await correct_msg(msg)
    await state.update_data(genre=msg.text)
    await state.set_state(States.preview)

    data = await state.get_data()
    book_info = [data["title"], data["author"], data["desc"], data["genre"]]
    text = await message_utils.add("preview", value=book_info)
    keyboard = await inline.confirm()
    await msg.answer(text, reply_markup=keyboard)

'''Выводим превью книги если кинули жанр кнопкой'''
async def add_preview(call: CallbackQuery, state: FSMContext):
    genre = call.data.split("_")[2]
    await state.update_data(genre=genre)
    await state.set_state(States.preview)
    data = await state.get_data()
    book_info = [data["title"], data["author"], data["desc"], data["genre"]]
    text = await message_utils.add("preview", value=book_info)
    keyboard = await inline.confirm()
    await call.message.edit_text(text, reply_markup=keyboard)

'''Отправляем в бд'''
async def add_run(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await db.add_book(data["title"], data["author"], data["desc"], data["genre"])
    await state.clear()
    keyboard = await inline.back()
    await call.message.edit_text("Книга успешно добавлена!", reply_markup=keyboard)



handlers_message = {
    router.message.register: [
        (start, Command("start")),
        (keyword_results, States.keyword, F.text),
        (add_author, States.title, F.text),
        (add_desc, States.author, F.text),
        (add_genre, States.desc, F.text),
        (add_preview_text, States.genre, F.text)
    ]
}

handlers_callbacks = {
    router.callback_query.register: [
        (call_start, F.data == "start"),
        (books_all, F.data == "all"),
        (books_find, F.data == "find"),
        (book_info, F.data.startswith("book_")),
        (book_delete, F.data.startswith("delete_")),
        (find_genre, F.data == "find_genre"),
        (genre_results, F.data.startswith("genre_")),
        (find_keyword, F.data == "find_keyword"),
        (add_title, F.data == "add"),
        (add_preview, States.genre, F.data.startswith("add_genre_")),
        (add_run, States.preview, F.data == "confirm")
    ]
}

for register_method, handler in handlers_message.items():
    for args in handler:
        register_method(*args)
    
for register_method, handler in handlers_callbacks.items():
    for args in handler:
        register_method(*args)