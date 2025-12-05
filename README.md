# MCP Tech Spec Server (Cursor UI) (Ru)

Стандартный MCP сервер для генерации и обновления технических спецификаций мер OLAP, вызываемый напрямую из интерфейса Cursor. Текущая реализация не синхронизирована с графом LangGraph.

## Назначение
- Анализ мер в Power BI (.bim) и связанных SQL артефактов (views, stored procedures)
- Формирование промптов для LLM: создание/добавление/обновление спецификаций
- Работа через Cursor UI как обычный MCP сервер (HTTP, порт 8000)

## Запуск сервера
```python
mcp.run(transport="http", port=8000)
```

## Инструменты
### 1) configure_session
Инициализация сессии: сохраняет пути к директориям с SQL процедурами и представлениями. Обязателен единоразовый вызов перед остальными инструментами.
- Параметры: `session_id`, `procedures_dir`, `views_dir`
- Возвращает: подтверждение настройки сессии

### 2) ts_measure_new_doc
Генерация промпта для создания новой спецификации одной меры.
- Параметры: `measure`, `session_id`, `olap_dir?`, `example_tech_spec_dir?`
- Логика: анализирует меру в .bim, трассирует поток данных (OLAP таблицы → DWH views → хранимые процедуры), опирается на пример спецификации; указывает сохранить файл рядом с шаблоном

### 3) ts_measure_existing_doc
Генерация промпта для добавления/замены спецификации меры в существующем документе.
- Параметры: `measure`, `existing_doc_dir`, `session_id`, `olap_dir?`, `replace_existing_measure?`
- Логика: анализирует меру и обновляет указанный markdown, при `replace_existing_measure=True` перезаписывает найденное описание

### 4) ts_list_measures_existing_doc
Генерация промпта для пакетного обновления мер по списку.
- Параметры: `list_measures_dir`, `existing_doc_dir`, `session_id`, `olap_dir?`, `replace_existing_measure?`
- Требование к списку мер: markdown с `#` — категория, `##` — мера
- Логика: для каждой категории создаёт/обновляет раздел, добавляет спецификации мер с описанием потока данных

## Структура генерируемых спецификаций
- Общая информация (название, тип, источник, формат)
- Назначение
- Исходные данные
- Логика обработки (DAX + описание)
- Условия фильтрации
- Зависимости (базовые меры, OLAP таблицы, DWH views, поток данных)

## Значения по умолчанию
Если не переданы параметры:
- `olap_dir`: `/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP`
- `example_tech_spec_dir`: `/Users/eremenkoivan/Projects/PythonProjects/MCPTechSpec/ТЗ DWH ETL.md` (для `ts_measure_new_doc`)

## Как использовать в Cursor
1. Вызвать `configure_session` с путями к процедурам и представлениям.
2. Выбрать инструмент: одиночная мера (`ts_measure_new_doc`/`ts_measure_existing_doc`) или пакет (`ts_list_measures_existing_doc`).
3. Скопировать сгенерированный промпт в Cursor и выполнить, позволяя LLM создать/обновить markdown.
4. Проверить сохранённые файлы (имя и расположение указываются в промпте).

Сервер предназначен только для генерации промптов и управления конфигурацией сессий; оркестрация выполняется пользователем через Cursor UI.

## Лицензия

Этот проект распространяется под лицензией Apache License 2.0. См. файл LICENSE для подробностей.

---

# MCP Tech Spec Server (Cursor UI) (Eng)

Standard MCP server for generating and updating technical specifications for OLAP measures, called directly from the Cursor interface. The current implementation is not synchronized with the LangGraph graph.

## Purpose
- Analysis of measures in Power BI (.bim) and related SQL artifacts (views, stored procedures)
- Generation of prompts for LLM: create/add/update specifications
- Operation through Cursor UI as a standard MCP server (HTTP, port 8000)

## Server Startup
```python
mcp.run(transport="http", port=8000)
```

## Tools
### 1) configure_session
Session initialization: saves paths to directories with SQL procedures and views. Must be called once before other tools.
- Parameters: `session_id`, `procedures_dir`, `views_dir`
- Returns: session configuration confirmation

### 2) ts_measure_new_doc
Generates a prompt for creating a new specification for a single measure.
- Parameters: `measure`, `session_id`, `olap_dir?`, `example_tech_spec_dir?`
- Logic: analyzes the measure in .bim, traces data flow (OLAP tables → DWH views → stored procedures), uses example specification as reference; instructs to save the file next to the template

### 3) ts_measure_existing_doc
Generates a prompt for adding/replacing a measure specification in an existing document.
- Parameters: `measure`, `existing_doc_dir`, `session_id`, `olap_dir?`, `replace_existing_measure?`
- Logic: analyzes the measure and updates the specified markdown, with `replace_existing_measure=True` overwrites found description

### 4) ts_list_measures_existing_doc
Generates a prompt for batch updating measures from a list.
- Parameters: `list_measures_dir`, `existing_doc_dir`, `session_id`, `olap_dir?`, `replace_existing_measure?`
- Requirement for measure list: markdown with `#` — category, `##` — measure
- Logic: for each category creates/updates a section, adds measure specifications with data flow description

## Structure of Generated Specifications
- General information (name, type, source, format)
- Purpose
- Source data
- Processing logic (DAX + description)
- Filtering conditions
- Dependencies (base measures, OLAP tables, DWH views, data flow)

## Default Values
If parameters are not provided:
- `olap_dir`: `/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP`
- `example_tech_spec_dir`: `/Users/eremenkoivan/Projects/PythonProjects/MCPTechSpec/ТЗ DWH ETL.md` (for `ts_measure_new_doc`)

## How to Use in Cursor
1. Call `configure_session` with paths to procedures and views.
2. Choose a tool: single measure (`ts_measure_new_doc`/`ts_measure_existing_doc`) or batch (`ts_list_measures_existing_doc`).
3. Copy the generated prompt into Cursor and execute it, allowing the LLM to create/update the markdown.
4. Check saved files (name and location are specified in the prompt).

The server is intended only for generating prompts and managing session configurations; orchestration is performed by the user through the Cursor UI.

## License

This project is distributed under the Apache License 2.0. See the LICENSE file for details.