Легенда проекта: Аналитика мобильного EdTech-приложения "LingvoApp"
Я - единственный продуктовый аналитик в стартапе по изучению языков. Приложение монетизируется через Freemium-модель, где бесплатные базовые функции и уроки + платная Premium-подписка с доп. функционалом.
Моя задача - построить с нуля систему сбора метрик, чтобы понять, где пользователи отваливаются при онбординге, как учатся, и что заставляет их покупать подписку.

Приложение у нас мобильное - под IOS и Android

Первый шаг - Определиться с тем, что за функционал есть в нашем приложении, чтобы можно было его проанализировать и выделить основные события действий пользователей и уже к ним метрики придумывать

Общий функционал:
скачать приложение -> зарегистрироваться/войти -> выбрать общие практические занятия -> проходить эти занятия -> получить результат и фидбэк
Платный функционал:
добавляются еще несколько типов возможных занятий, больше занятий в целом, потенциальные семинары\лекции с преподавателями онлайн 

Путь пользователя начинается с первого запуска, где мы сразу ведем его через интерактивный пробный урок с подсказками, чтобы он быстро понял механику и ценность продукта. Сразу после этого короткого обучения мы показываем первый экран с предложением платных фич, а затем отправляем юзера на регистрацию, где через квиз собираем информацию про его текущий уровень языка, цели обучения и желаемую частоту занятий. В основном цикле приложения пользователь выбирает уроки, проходит их и получает фидбэк, при этом у него перед глазами всегда есть точка входа в покупку в виде отдельной кнопки рядом с иконкой профиля и заблокированные «замочками» премиальные лекции.

Далее я определяю метрики, какие нужно со всего этого собрать:
1. Технические данные - ОС, модель устройства, версия приложения
2. Онбординг - прохождение каждого шага туториала, время до завершения первого урока, конверсия из установки в регистрацию
3. Цель обучения, стартовый уровень языка, сколько будет заниматься пользователь, имя пользователя, страна, возраст
4. Количество и типы пройденных уроков, время внутри каждого занятия, процент правильных ответов, DAU, MAU, WAU, ретеншн
5. Количество переходов на экран оплаты, конверсия из просмотра в покупку, средний доход с пользователя.

Далее нужно спроектировать сущности БД, которые будут генерироваться скриптом

## 1. Пользователи 

| Поле | Описание |
|------|----------|
| user_id | Уникальный идентификатор пользователя |
| install_time | Дата и время установки приложения |
| name | Имя пользователя |
| age | Возраст пользователя |
| country | Страна пользователя |
| goal | Цель обучения |
| onboarding_level | Стартовый уровень языка  |
| plan_on_study_time | Планируемая частота занятий минут в день |
| is_premium | Флаг премиум-статуса |

## 2. Каталог уроков 

| Поле | Описание |
|------|----------|
| lesson_id | Уникальный идентификатор урока |
| lesson_name | Название урока |
| lesson_type | Тип урока  |
| difficulty_level | Уровень сложности  |
| is_premium | Доступен ли урок только по подписке  |

## 3. Сырой лог событий

| Поле | Описание |
|------|----------|
| event_id | Уникальный идентификатор события |
| event_time | Время наступления события  |
| user_id | Идентификатор пользователя |
| platform | Платформа (iOS / Android) |
| device_model | Модель устройства |
| app_version | Версия приложения |
| event_name | Название события |
| event_properties | Дополнительные свойства события в формате JSON |

## 4. Факт успеваемости 

| Поле | Описание |
|------|----------|
| user_id | Идентификатор пользователя |
| lesson_id | Идентификатор урока |
| started_at | Время начала урока |
| completed_at | Время завершения урока |
| status | Статус прохождения |
| score_percentage | Процент правильных ответов  |
| time_spent_sec | Время, затраченное на урок (секунды) |
| mistakes_count | Количество ошибок |

## 5. Факт оплат

| Поле | Описание |
|------|----------|
| transaction_id | Уникальный идентификатор транзакции |
| user_id | Идентификатор пользователя |
| event_time | Время совершения платежа |
| plan_type | Тип плана  |
| revenue_rub | Сумма платежа в рублях |


Далее создаем скрипт, который накидает автоматически фейковые данные для дальнейшей работы с ними
скрипт этот представлен в main.py 
Он генерирует события с помощью библиотеки faker, а затем с помощью pandas создает два .csv файла, в одном информация про пользователей, в другом про события

После этого нужно развернуть clickhouse и power bi

1. скачаем power bi с microsoft store и установим драйвер ODBC

2. Создаем и запускаем контейнер с ClickHouse со следующими параметрами:
docker run -d --name clickhouse-server \
  -e CLICKHOUSE_USER="myusername" \
  -e CLICKHOUSE_PASSWORD="mypassword" \
  -e CLICKHOUSE_DB=lingvodb \
  -p 8123:8123 -p 9000:9000 \
  clickhouse/clickhouse-server

3. Копируем сгенерированные цсв файлы в контейнер с помощью команд:
"docker cp dim_users.csv clickhouse-server:/var/lib/clickhouse/user_files/"

"docker cp dim_lessons_catalog.csv clickhouse-server:/var/lib/clickhouse/user_files/"

"docker cp raw_events.csv clickhouse-server:/var/lib/clickhouse/user_files/"

"docker cp fact_learning.csv clickhouse-server:/var/lib/clickhouse/user_files/"

"docker cp fact_payments.csv clickhouse-server:/var/lib/clickhouse/user_files/"

4. Подключаемся к кликхаусу с консоли с помощью команды: docker exec -it clickhouse-server clickhouse-client -u "myusername" --password "mypassword" -d lingvodb


5. Создадим таблицы в ClickHouse 
-- 1. пользователи
CREATE TABLE dim_users (
    user_id String,
    install_time DateTime,
    name String,
    age UInt8,
    country String,
    goal String,
    onboarding_level String,
    plan_on_study_time UInt16,
    is_premium UInt8
) ENGINE = MergeTree()
ORDER BY user_id;

-- 2. каталог уроков
CREATE TABLE dim_lessons_catalog (
    lesson_id String,
    lesson_name String,
    lesson_type String,
    difficulty_level UInt8,
    is_premium UInt8
) ENGINE = MergeTree()
ORDER BY lesson_id;

-- 3. Сырой лог событий
CREATE TABLE raw_events (
    event_id String,
    event_time DateTime,
    user_id String,
    platform String,
    device_model String,
    app_version String,
    event_name String,
    event_properties String
) ENGINE = MergeTree()
ORDER BY (event_time, event_name, user_id);

-- 4. Таблица успеваемости
CREATE TABLE fact_learning (
    user_id String,
    lesson_id String,
    started_at DateTime,
    completed_at DateTime,
    status String,
    score_percentage Float32,
    time_spent_sec UInt32,
    mistakes_count UInt16
) ENGINE = MergeTree()
ORDER BY (started_at, user_id);

-- 5. Таблица оплаты
CREATE TABLE fact_payments (
    transaction_id String,
    user_id String,
    event_time DateTime,
    plan_type String,
    revenue_rub Float32
) ENGINE = MergeTree()
ORDER BY (event_time, user_id);

6. Занесем данные в созданные таблицы:

Переключаемся на созданную БД: "USE lingvodb;"
Загружаем все файлы :
"INSERT INTO dim_users FROM INFILE '/var/lib/clickhouse/user_files/dim_users.csv' FORMAT CSVWithNames;"

"INSERT INTO dim_lessons_catalog FROM INFILE '/var/lib/clickhouse/user_files/dim_lessons_catalog.csv' FORMAT CSVWithNames;"

"INSERT INTO raw_events FROM INFILE '/var/lib/clickhouse/user_files/raw_events.csv' FORMAT CSVWithNames;"

"INSERT INTO fact_learning FROM INFILE '/var/lib/clickhouse/user_files/fact_learning.csv' FORMAT CSVWithNames;"

"INSERT INTO fact_payments FROM INFILE '/var/lib/clickhouse/user_files/fact_payments.csv' FORMAT CSVWithNames;"


