# MCP Tech Spec Server (Ru)

MCP (Model Context Protocol) сервер для генерации технических спецификаций для OLAP мер. Этот сервер предназначен для вызова из внешних агентов (например, LangGraph агентов) для создания комплексной документации по мерам бизнес-аналитики.

## Обзор

MCP Tech Spec сервер анализирует OLAP меры из проектов Power BI Desktop (.bim файлы) и генерирует подробные документы технических спецификаций. Он отслеживает поток данных от мер через представления DWH к хранимым процедурам, создавая человекочитаемую документацию, следующую стандартизированному шаблону.

## Конфигурация сервера

Сервер работает на HTTP транспорте и по умолчанию прослушивает порт 8000.

```python
mcp.run(transport="http", port=8000)
```

## Инструменты

### 1. `configure_session`

Настраивает сессию с необходимыми путями к директориям. **Должен быть вызван один раз перед использованием других инструментов.**

**Параметры:**
- `session_id` (str): Уникальный идентификатор пользовательской сессии
- `procedures_dir` (str): Абсолютный путь к директории, содержащей SQL хранимые процедуры
- `views_dir` (str): Абсолютный путь к директории, содержащей SQL представления
- `olap_dir` (str): Абсолютный путь к директории, содержащей .bim файл
- `store_doc_dir` (str): Абсолютный путь к директории, где будут сохранены сгенерированные документы

**Возвращает:**
- Сообщение подтверждения об успешной настройке сессии

### 2. `ts_measure_new_doc`

Генерирует подробный документ технической спецификации для одной меры, включая её поток данных.

**Параметры:**
- `measure` (str): Точное название меры для анализа из OLAP проекта (.bim файл)
- `session_id` (str): Уникальный идентификатор сессии (должен быть настроен через `configure_session` заранее)

**Возвращает:**
- Подробную строку промпта, которая инструктирует LLM выполнить анализ и создать документ

**Функциональность:**
1. Извлекает свойства меры из .bim файла (название, выражение, формат, displayFolder, описание)
2. Отслеживает поток данных: OLAP таблицы → представления DWH → хранимые процедуры
3. Генерирует промпт, следующий стандартизированному шаблону технической спецификации
4. Включает обязательные шаги самопроверки для обеспечения соответствия структуры документа

## Шаблон технической спецификации

Сервер генерирует спецификации, следующие стандартизированной структуре:

1. **Общая информация** - Общая информация (название меры, тип, источник, формат отображения)
2. **Назначение** - Назначение и цели
3. **Исходные данные** - Исходные данные (меры, таблицы, связанные таблицы)
4. **Логика обработки** - Логика обработки (DAX выражение и описание)
5. **Условия фильтрации** - Условия фильтрации
6. **Зависимости** - Зависимости (базовые меры, OLAP таблицы, представления DWH, поток данных)

Раздел потока данных включает пронумерованные элементы с нотацией стрелок и подробными описаниями хранимых процедур.

## Соглашение об именовании файлов

Сгенерированные документы следуют формату: `BlockName_MeasureName.md`
- `BlockName`: Название из первого H1 заголовка (например, "Продажи")
- `MeasureName`: Название документируемой меры
- Пример: `Продажи_% выполнения плана по выручке от реализации.md`

## Порядок использования

1. **Настроить сессию**: Вызвать `configure_session` со всеми необходимыми путями к директориям
2. **Сгенерировать спецификацию**: Вызвать `ts_measure_new_doc` для каждой меры, которую нужно задокументировать
3. **Обработать промпт**: Возвращённый промпт должен быть обработан LLM для создания фактического markdown документа
4. **Сохранить документ**: LLM должен сохранить документ в настроенную директорию `store_doc_dir`, следуя соглашению об именовании

## Интеграция

Этот MCP сервер предназначен для вызова из внешних агентов (таких как LangGraph агенты), которые оркестрируют процесс генерации документации. Агент обрабатывает:
- Управление сессиями
- Итерацию по нескольким мерам
- Обработку возвращённых промптов
- Создание и управление файлами

MCP сервер фокусируется исключительно на генерации промптов для анализа и поддержании конфигураций сессий.

## Лицензия

Этот проект распространяется под лицензией Apache License 2.0. См. файл LICENSE для подробностей.

---

# MCP Tech Spec Server (Eng)

MCP (Model Context Protocol) server for generating technical specifications for OLAP measures. This server is designed to be called from external agents (e.g., LangGraph agents) to create comprehensive documentation for business intelligence measures.

## Overview

The MCP Tech Spec server analyzes OLAP measures from Power BI Desktop projects (.bim files) and generates detailed technical specification documents. It traces data flow from measures through DWH views to stored procedures, creating human-readable documentation that follows a standardized template.

## Server Configuration

The server runs on HTTP transport and listens on port 8000 by default.

```python
mcp.run(transport="http", port=8000)
```

## Tools

### 1. `configure_session`

Configures a session with required directory paths. **Must be called once before using other tools.**

**Parameters:**
- `session_id` (str): Unique identifier for the user session
- `procedures_dir` (str): Absolute path to directory containing SQL stored procedures
- `views_dir` (str): Absolute path to directory containing SQL views
- `olap_dir` (str): Absolute path to directory containing .bim file
- `store_doc_dir` (str): Absolute path to directory where generated documentation will be saved

**Returns:**
- Confirmation message indicating successful session configuration

### 2. `ts_measure_new_doc`

Generates a detailed technical specification document for a single measure, including its data flow.

**Parameters:**
- `measure` (str): The exact name of the measure to analyze from the OLAP project (.bim file)
- `session_id` (str): The unique identifier for the session (must be configured via `configure_session` first)

**Returns:**
- A detailed prompt string that instructs an LLM to perform the analysis and create the document

**Functionality:**
1. Extracts measure properties from the .bim file (name, expression, format, displayFolder, description)
2. Traces data flow: OLAP tables → DWH views → stored procedures
3. Generates a prompt that follows a standardized technical specification template
4. Includes mandatory self-verification steps to ensure document structure compliance

## Technical Specification Template

The server generates specifications following a standardized structure:

1. **Общая информация** - General information (measure name, type, source, display format)
2. **Назначение** - Purpose and goals
3. **Исходные данные** - Source data (measures, tables, related tables)
4. **Логика обработки** - Processing logic (DAX expression and description)
5. **Условия фильтрации** - Filtering conditions
6. **Зависимости** - Dependencies (base measures, OLAP tables, DWH views, data flow)

The data flow section includes numbered items with arrow notation and detailed descriptions of stored procedures.

## File Naming Convention

Generated documents follow the format: `BlockName_MeasureName.md`
- `BlockName`: The name from the first H1 header (e.g., "Продажи")
- `MeasureName`: The name of the measure being documented
- Example: `Продажи_% выполнения плана по выручке от реализации.md`

## Usage Flow

1. **Configure session**: Call `configure_session` with all required directory paths
2. **Generate specification**: Call `ts_measure_new_doc` for each measure to document
3. **Process prompt**: The returned prompt should be processed by an LLM to create the actual markdown document
4. **Save document**: The LLM should save the document to the configured `store_doc_dir` following the naming convention

## Integration

This MCP server is designed to be called from external agents (such as LangGraph agents) that orchestrate the documentation generation process. The agent handles:
- Session management
- Iterating through multiple measures
- Processing the returned prompts
- File creation and management

The MCP server focuses solely on generating the analysis prompts and maintaining session configurations.

## License

This project is distributed under the Apache License 2.0. See the LICENSE file for details.
