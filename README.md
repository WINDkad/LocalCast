# LocalCast

LocalCast - локальный web-сервис на Python для управления и трансляции мультимедийного контента на Smart TV и другие устройства внутри сети.

Система позволяет загружать видео и изображения через web-панель и автоматически воспроизводить их в browser player.

---

# Основные возможности

- авторизация администратора;
- смена логина и пароля через web-интерфейс;
- создание отдельных папок трансляций;
- загрузка видео и изображений;
- удаление контента;
- browser-based player;
- autoplay;
- repeat playlist;
- repeat one;
- shuffle режим;
- fullscreen режим;
- auto-refresh контента без перезагрузки страницы;
- работа на Smart TV, ПК, планшетах и телефонах;
- Docker deployment.

---

# Поддерживаемые форматы

## Видео

- `.mp4`
- `.mkv`
- `.avi`
- `.mov`
- `.webm`
- `.m4v`

## Изображения

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

---

# Структура проекта

```text
LocalCast/
│
├── templates/
│   ├── admin.html
│   ├── folder.html
│   ├── player.html
│   └── login.html
│
├── tv_content/
│   ├── common/
│   ├── 1/
│   └── 2/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── server.py
├── media_lib.py
├── config.py
└── README.md
```

---

# Запуск через Docker

## 1. Клонировать проект

```bash
git clone https://github.com/WINDkad/LocalCast.git
```

## 2. Перейти в папку проекта

```bash
cd LocalCast
```

## 3. Запустить контейнер

```bash
docker compose up -d --build
```

---

# Остановка проекта

```bash
docker compose down
```

---

# Проверка контейнера

```bash
docker ps
```

---

# Просмотр логов

```bash
docker logs -f localcast
```

---

# Административная панель

После запуска проект будет доступен по адресу:

```text
http://127.0.0.1:8000/admin
```

Для подключения с другого устройства внутри сети:

```text
http://IP_КОМПЬЮТЕРА:8000/admin
```

---

# Авторизация

При первом запуске автоматически создаются стандартные учётные данные:

```text
login: admin
password: admin
```

После входа логин и пароль можно изменить через web-интерфейс.

---

# Browser Player

Каждая папка трансляции имеет собственный player.

Примеры:

```text
/player/common
/player/1
/player/2
```

Player поддерживает:

- autoplay;
- repeat playlist;
- repeat one;
- shuffle;
- fullscreen;
- скрытие UI;
- автоматическое обновление контента.

---

# Использование на Smart TV

1. Подключить телевизор к той же сети;
2. Открыть встроенный браузер;
3. Перейти по адресу:

```text
http://IP_КОМПЬЮТЕРА:8000/player/1
```

После этого контент начнёт воспроизводиться автоматически.

---

# Хранение данных

## Контент

Все медиафайлы сохраняются в:

```text
tv_content/
```

## Настройки

Runtime-данные сохраняются в:

```text
data/
```

---

# Безопасность

В проекте реализованы:

- session-based авторизация;
- защита административной панели;
- защита загрузки и удаления файлов;
- безопасная работа с путями файлов;
- хранение учётных данных вне GitHub.

---

# Назначение проекта

LocalCast может использоваться для:

- Smart TV;
- digital signage;
- рекламных экранов;
- учебных аудиторий;
- офисов;
- локальных презентационных систем.

---

# Технологии

- Python
- FastAPI
- Uvicorn
- HTML / CSS / JavaScript
- Docker
- Docker Compose