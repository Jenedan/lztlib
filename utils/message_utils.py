from database import db as db

async def start(fullname):
    return(
        f"Привет, *{fullname}*\n\n"
        f"Чего хочешь?"
    )

async def info(book_id):
    book = await db.get_book_info(book_id)
    return(
        f"Информация о книге\n\n"
        f"Название: *{book[1]}*\n"
        f"Автор: *{book[2]}*\n"
        f"Жанр: *{book[3]}*\n"
        f"Описание: *{book[4]}*"
    )

async def find(key):
    match key:
        case "select":
            return(
                f"Каким методом будем искать?"
            )
        case "genre":
            return(
                f"Выберите жанр книги"
            )
        case "keyword":
            return(
                f"Введите слово для поиска по автору или названию книги"
            )
    
async def add(key, value=None):
    match key:
        case "preview":
            return(
                f"Название: *{value[0]}*\n"
                f"Автор: *{value[1]}*\n"
                f"Описание: *{value[2]}*\n"
                f"Жанр: *{value[3]}*"
            )
        case "title":
            return(
                f"Укажите название книги"
            )
        case "author":
            return(
                f"Укажите автора книги"
            )
        case "desc":
            return(
                f"Укажите описание книги"
            )
        case "genre":
            return(
                f"Выберите жанр из уже предложенных, или напишите свой"
            )
        case "error":
            return(
                "Длина текста должна быть не менее 5-и символов"
            )

async def books(filter=None, key=None):
    if not filter:
        books = await db.get_books()
    if filter == "keyword":
        books = await db.find_books_keyword(key)
    if filter == "genre":
        books = await db.find_books_genre(key)

    if not books:
        return(
            f"В данный момент книг нет"
        )
    
    count = len(books)
    return(
            f"Найдено книг: {count}"
        )