# MVC Refactoring Guide

Этот документ помогает понять, **что можно улучшить в текущем проекте**, если цель - сделать архитектуру ближе к понятной MVC/слоистой схеме.

Важно: в FastAPI чаще используют не чистый MVC из учебника, а более практичную схему:

- `router` - принимает HTTP-запросы;
- `service` - содержит бизнес-логику;
- `repository` - общается с базой данных;
- `mappers` - переводят ORM-модели в схемы ответа;
- `schemas` - описывают вход и выход API;
- `exceptions` - описывают ошибки приложения.

Для новичка это можно запомнить так:

- `router` = "что пришло по HTTP";
- `service` = "что с этим делать";
- `repository` = "как достать/сохранить в БД";
- `mapper` = "как превратить ORM в красивый ответ";
- `schema` = "какой JSON мы принимаем и отдаём".

---

## 1. Что уже хорошо

В проекте уже есть правильные идеи:

- роуты не ходят в базу напрямую;
- есть отдельные сервисы;
- есть отдельные репозитории;
- есть отдельные мапперы;
- есть единый обработчик ошибок в `src/application.py`;
- есть схемы для request/response;
- есть soft delete через `is_deleted`.

Это уже неплохая база. То есть проект не "сломанный", а просто местами слои смешаны.

---

## 2. Главная проблема сейчас

Самая большая проблема в том, что **репозиторий делает слишком много**.

Репозиторий в идеале должен:

- выполнять SQL-запросы;
- возвращать данные;
- не решать, что делать с бизнес-правилами.

А сейчас в некоторых местах он:

- сам решает, какие связи удалить;
- сам восстанавливает удалённые записи;
- сам группирует данные;
- сам собирает итоговый ответ;
- иногда сам понимает "что считать удалённым" и "что считать лишним".

Это уже похоже не на repository, а на маленький service.

---

## 3. Как правильно делить ответственность

### Router

Роутер должен:

- принять параметры запроса;
- вызвать сервис;
- вернуть результат;
- не знать SQL;
- не знать, как устроена таблица `students_courses`.

### Service

Сервис должен:

- решать, какие действия выполнить;
- вызывать репозиторий в нужном порядке;
- проверять бизнес-условия;
- выбрасывать доменные ошибки;
- собирать use-case целиком.

### Repository

Репозиторий должен:

- выполнять чтение и запись в БД;
- не решать, как строится use-case;
- не заниматься HTTP;
- не возвращать "красивый JSON";
- не знать про роуты.

### Mapper

Маппер должен:

- превращать ORM в `Pydantic`-схемы;
- не лезть в БД;
- не решать бизнес-логику.

---

## 4. Что можно улучшить в проекте

### 4.1 Перенести бизнес-логику из repository в service

Это самое важное улучшение.

#### Сейчас

В `src/repositories/students_courses.py` метод `update_student_with_courses()` делает сразу всё:

- ищет студента;
- читает текущие связи;
- восстанавливает курсы;
- создаёт связи;
- удаляет лишние связи;
- удаляет "осиротевшие" курсы.

То есть там смешаны:

- SQL;
- правила;
- принятие решений.

#### Как лучше

Репозиторий можно разбить на маленькие операции:

- `get_student()`
- `get_student_links()`
- `get_course_by_reestr_number()`
- `insert_course()`
- `restore_course()`
- `attach_course_to_student()`
- `detach_course_from_student()`
- `soft_delete_course_if_orphan()`

А сервис уже будет решать, в каком порядке это вызывать.

#### Пример "до"

```python
async def update_student_with_courses(self, student_id: int, data: StudentPatch):
    # репозиторий сам делает почти всё
    ...
```

#### Пример "после"

```python
async def update_student_with_courses(self, student_id: int, data: StudentPatch):
    student = await self.repo.get_student(student_id)
    if student is None:
        raise ObjectNotFoundException("Student not found")

    current_links = await self.repo.get_student_links(student_id)

    requested_courses = []
    for course_data in data.courses or []:
        course = await self.repo.get_or_restore_course(
            course_data.reestr_number,
            course_data.title,
        )
        requested_courses.append(course)

    await self.repo.sync_student_courses(
        student_id=student_id,
        requested_course_ids={course.id for course in requested_courses},
        current_links=current_links,
    )
```

#### Почему так лучше

- легче читать;
- легче тестировать;
- меньше магии в репозитории;
- проще искать баги.

---

### 4.2 Не возвращать из repository готовые response-схемы

#### Сейчас

В репозиториях методы вроде:

- `get_author_with_books()`
- `get_person_with_passport()`
- `get_all_students_with_courses()`

часто возвращают уже почти готовые `Pydantic`-схемы или используют `build_*_response()`.

#### Проблема

Repository начинает знать слишком много о внешнем API.

Например, он уже не просто "достал данные из БД", а ещё и "собрал ответ для клиента".

#### Лучше

Репозиторий возвращает ORM или сырые данные.
Сервис или mapper превращает это в `Student`, `Author`, `Person`.

#### Пример

**Плохо:**

```python
books = await self.fetch_active_all(BooksOrm, author_id=author.id)
return build_author_response(author, books)
```

**Лучше:**

```python
books = await self.fetch_active_all(BooksOrm, author_id=author.id)
return author, books
```

А уже потом:

```python
return build_author_response(author, books)
```

в сервисе или mapper-слое.

#### Почему это важно

Так легче:

- менять формат ответа;
- переиспользовать репозиторий;
- писать тесты;
- не ломать бизнес-логику при изменении API.

---

### 4.3 Сделать service настоящим слоем бизнес-логики

#### Сейчас

Во многих сервисах логика почти такая:

- вызвать репозиторий;
- поймать `IntegrityError`;
- вернуть page-model;
- если `None`, кинуть ошибку.

Это полезно, но это пока не полноценный service layer.

#### Что можно улучшить

Сервис должен принимать решения.

Например:

- какой объект искать;
- когда выбрасывать `ObjectNotFoundException`;
- когда писать `AlreadyExistsException`;
- какие записи считать удалёнными;
- какие записи восстанавливать;
- что делать, если в запросе пришли дубли.

#### Пример

В `students_courses` сервис может делать такое:

```python
async def update_student_with_courses(self, student_id: int, data: StudentPatch) -> None:
    student = await self.repo.get_student(student_id)
    if student is None:
        raise ObjectNotFoundException("Student not found")

    # здесь сервис решает, как именно синхронизировать список курсов
    ...
```

А репозиторий только даёт инструменты:

```python
await self.repo.get_student(student_id)
await self.repo.get_student_links(student_id)
await self.repo.attach_course_to_student(...)
await self.repo.detach_course_from_student(...)
```

---

### 4.4 Упростить исключения

#### Сейчас идея хорошая, но можно ещё чище

Вместо большого числа узких классов:

- `StudentNotFoundError`
- `AuthorNotFoundError`
- `PassportNotFoundError`

можно использовать более общие типы:

- `ObjectNotFoundException`
- `AlreadyExistsException`

А конкретику передавать через `message` и `details`.

#### Пример

```python
raise ObjectNotFoundException(
    "Book not found",
    details={"book_id": 123}
)
```

#### Что это даёт

- меньше классов;
- меньше файлов;
- проще читать;
- легче поддерживать.

#### Когда узкие исключения всё-таки нужны

Если ошибка имеет особое поведение:

- нужно разный HTTP status;
- нужно разный формат ответа;
- нужно особое логирование.

Если ничего особенного нет, общий класс лучше.

---

### 4.5 `details` лучше использовать для технического контекста

#### Для чего это нужно

`message` отвечает на вопрос:

- "Что случилось?"

`details` отвечает на вопрос:

- "С чем именно это случилось?"

#### Пример

```python
raise ObjectNotFoundException(
    "Book not found",
    details={"book_id": 10}
)
```

#### В ответе API это будет выглядеть так

```json
{
  "error": {
    "code": "object_not_found_exception",
    "message": "Book not found",
    "details": {
      "book_id": 10
    }
  }
}
```

#### Когда это полезно

- для логов;
- для фронтенда;
- для отладки;
- для интеграций.

---

### 4.6 Убрать лишние модели из `src/schemas/errors.py`

#### Сейчас

В `src/schemas/errors.py` у тебя есть:

- `ErrorPayload`
- `ErrorResponse`
- `NotFoundError`
- `ConflictError`
- `AuthorNotFoundError`
- `AuthorConflictError`

#### Что реально нужно

Для текущего приложения достаточно:

- `ErrorPayload`
- `ErrorResponse`

#### Почему

Потому что эти модели используются в `application.py` для единого JSON-ответа.

Остальные модели сейчас:

- либо не используются;
- либо дублируют смысл exception-классов;
- либо добавляют шум.

#### Простой совет

Если модель не участвует в ответах API и не нужна для документации, её лучше убрать.

---

### 4.7 Исправить обработчики исключений в `application.py`

#### Сейчас проблема

У тебя есть два handler-а на один и тот же класс `AlreadyExistsException`.

Это путаница.

#### Почему это плохо

- непонятно, какой обработчик реально сработает;
- тяжело поддерживать;
- легко забыть, зачем второй вообще нужен.

#### Что лучше

Сделать:

- один handler для `ObjectNotFoundException`;
- один handler для `AlreadyExistsException`;
- один общий handler для `AppException`.

#### Идея

Если нужен разный текст для книги/студента/автора, лучше передавать его в сам exception:

```python
raise AlreadyExistsException("A student with this record book number already exists")
```

а не плодить одинаковые handlers.

---

### 4.8 Улучшить слой `mapper`

#### Что уже хорошо

У тебя уже есть папка `src/mappers`.

Это правильно.

#### Что можно улучшить

Сделать правило:

- repository не собирает response-схемы;
- service не занимается SQL;
- mapper только преобразует данные.

#### Пример

```python
def build_student_response(student: StudentsOrm, courses: list[CoursesOrm]) -> Student:
    ...
```

Это хороший стиль.

#### Что важно

Mapper не должен сам ходить в базу.
Он должен только:

- взять ORM;
- превратить в schema;
- вернуть результат.

---

### 4.9 Не делать слишком сложные repository-методы

#### Сейчас

В `StudentsCoursesRepository` есть методы, которые делают слишком много:

- `_get_or_restore_course()`
- `_attach_course_to_student()`
- `_soft_delete_orphan_courses()`
- `update_student_with_courses()`

#### Почему это проблема

Когда метод делает сразу всё, потом трудно:

- понять его логику;
- протестировать его;
- переиспользовать куски;
- менять часть поведения без риска сломать всё остальное.

#### Лучше

Разбить на простые методы.

Например:

```python
await repo.get_course_by_reestr_number(...)
await repo.restore_course(course_id)
await repo.link_student_course(student_id, course_id)
await repo.unlink_student_course(student_id, course_id)
```

А всю последовательность держать в service.

---

### 4.10 Ограничить размер страниц в API

#### Сейчас

В роутерах:

```python
limit: int = Query(10, ge=1)
offset: int = Query(0, ge=0)
```

#### Что можно улучшить

Добавить верхнюю границу:

```python
limit: int = Query(10, ge=1, le=100)
```

#### Зачем

Если клиент случайно или специально запросит `limit=100000`, база и приложение получат лишнюю нагрузку.

#### Простая аналогия

Это как разрешить человеку заказать "сколько угодно" книг сразу. Лучше сказать: "не больше 100 за раз".

---

### 4.11 Привести транзакции к понятной границе

#### Сейчас

Коммит делается в `src/db.py` внутри dependency `get_session()`.

Это рабочая схема.

#### Что важно не делать

- не делать `commit()` внутри repository;
- не смешивать commit/rollback в каждом методе;
- не растаскивать транзакцию по разным слоям без нужды.

#### Нормальная идея

Один запрос = одна сессия = один транзакционный сценарий.

Это проще понимать новичку и проще отлаживать.

---

### 4.12 Добавить тесты на уровни

Это очень полезно для такого проекта.

#### Какие тесты нужны

1. **Service tests**
   - проверяют бизнес-логику;
   - например, что при отсутствии студента выбрасывается `ObjectNotFoundException`.

2. **Repository tests**
   - проверяют SQL и работу с БД;
   - например, что `fetch_active_page()` реально возвращает только активные записи.

3. **API tests**
   - проверяют роуты;
   - например, что `GET /students` возвращает `StudentsPage`.

#### Пример идеи теста

```python
async def test_get_student_not_found():
    ...
    with pytest.raises(ObjectNotFoundException):
        await service.get_student_with_courses(999)
```

#### Почему это важно

Когда архитектура начинает делиться на слои, тесты помогают не сломать поведение при рефакторинге.

---

## 5. Что бы я делал в первую очередь

Если идти по приоритету, я бы делал так:

### Шаг 1

Упростить исключения:

- оставить общие классы;
- передавать `message` и `details`;
- убрать лишние дубли.

### Шаг 2

Почистить `src/application.py`:

- один handler на один тип ошибки;
- убрать дублирующийся `AlreadyExistsException`.

### Шаг 3

Разделить `service` и `repository` в `students_courses`:

- репозиторий = SQL-операции;
- сервис = сценарий работы.

### Шаг 4

Перестать возвращать готовые response-схемы из репозитория:

- mapper должен жить отдельно;
- repository должен быть проще.

### Шаг 5

Добавить тесты.

---

## 6. Как выглядит "хороший" итоговый вариант

Если упростить до одной фразы, то хороший проект будет устроен так:

- `router` принимает HTTP;
- `service` решает бизнес-задачу;
- `repository` говорит с БД;
- `mapper` собирает ответ;
- `exceptions` описывают ошибки;
- `schemas` описывают JSON;
- `application.py` переводит ошибки в HTTP-ответы.

Если этот принцип соблюдён, проект легче поддерживать и легче объяснять другим.

---

## 7. Короткий вывод

Сейчас проект уже рабочий, но до чистого слоя MVC/architecture его можно улучшить в нескольких местах:

- убрать бизнес-логику из repository;
- сделать service более умным;
- упростить exceptions;
- оставить repository только для БД;
- привести обработку ошибок к единому виду;
- добавить тесты;
- ограничить нагрузку через pagination limits.

Если делать рефакторинг постепенно, проект станет понятнее и для тебя, и для ментора.
