from fastmcp import FastMCP
from typing import Dict

# Create an MCP Server
mcp = FastMCP("Creating Technical Specification Service for Single Measure")

# Global store for session configurations
session_configs: Dict[str, Dict[str, str]] = {}

# Reusable self-verification prompt block
MANDATORY_SELF_VERIFICATION = """

MANDATORY SELF-VERIFICATION:
After creating the specification, you MUST:
1. Compare the created structure with SAMPLE_TECHNICAL_SPECIFICATION template provided above, section by section
2. Fix ALL differences in formatting, headers, section order
3. Verify that "Data Flow" section exactly matches the template format (numbered items with arrow notation, ##### headers for stored procedures)
4. Only after complete structural compliance, save the file to '{store_doc_dir}' directory
5. FILE NAMING REQUIREMENT: The file name MUST follow this format: "BlockName_MeasureName.md"
   - BlockName: The name from the first H1 header (# Header) of the specification (e.g., "Продажи")
   - MeasureName: The name of the measure being documented
   - Example: "Продажи_% выполнения плана по выручке от реализации.md"
   - Replace any characters that are invalid for file names with underscores"""

SAMPLE_TECHNICAL_SPECIFICATION = """

# Продажи

## Мера "% выполнения плана по выручке от реализации"

### 1. Общая информация

**Название меры:** % выполнения плана по выручке от реализации  
**Тип:** Мера (Measure)  
**Источник:** OLAP.bim  
**Папка отображения:** План-Факт  
**Формат отображения:** Процент (0.0%;-0.0%;0.0%)  

### 2. Назначение (Цель/задача)

Мера "% выполнения плана по выручке от реализации" предназначена для расчета процента выполнения плана по выручке от реализации. Данная мера показывает, насколько фактическая выручка соответствует запланированной, позволяя оценить эффективность выполнения планов продаж.

### 3. Исходные данные

**Основные меры:**
- [Сумма (со скидкой) реальная нараст. итогом] - фактическая выручка нарастающим итогом
- [План нараст. итогом] - плановая выручка нарастающим итогом

**Основные таблицы:**
- М001 Заказы Клиентов - для фактических данных
- М002 Планы Продаж - для плановых данных

**Связанные таблицы:**
- 000 Календарь - для временных расчетов
- 007 Сезон - для сезонных расчетов
- С002 Расчеты - для выбора периода расчета

### 4. Логика обработки

#### 4.1. Выражение DAX

```dax
VAR Result =
    DIVIDE ( [Сумма (со скидкой) реальная нараст. итогом], [План нараст. итогом] )
RETURN
    Result
```

#### 4.2. Описание логики

1. **Расчет фактической выручки:** Используется мера "Сумма (со скидкой) реальная нараст. итогом" для получения фактической выручки нарастающим итогом
2. **Расчет плановой выручки:** Используется мера "План нараст. итогом" для получения плановой выручки нарастающим итогом
3. **Расчет процента выполнения:** Выполняется деление фактической выручки на плановую с помощью функции DIVIDE
4. **Обработка деления на ноль:** Функция DIVIDE автоматически обрабатывает случаи деления на ноль, возвращая BLANK

### 5. Условия фильтрации

- **Статус заказов:** Учитываются только заказы со статусом "Реальный"
- **Исключение ВГО:** Исключаются заказы с флагом "ВГО булево"
- **Активные планы:** Учитываются только активные планы продаж
- **Временные фильтры:** Применяются фильтры по календарю и сезону в зависимости от выбранного периода

### 6. Зависимости

#### 6.1. Базовые меры
- [Сумма (со скидкой) реальная нараст. итогом] - фактическая выручка нарастающим итогом
- [План нараст. итогом] - плановая выручка нарастающим итогом

#### 6.2. Таблицы OLAP
- **М001 Заказы Клиентов** - основная таблица заказов
- **М002 Планы Продаж** - таблица планов продаж
- **000 Календарь** - календарная таблица
- **007 Сезон** - справочник сезонов
- **С002 Расчеты** - справочник типов расчетов

#### 6.3. Представления DWH
- **uni.vt_order** - представление заказов
- **uni.vt_sales_plan** - представление планов продаж

#### 6.4. Поток данных
1. **OLAP мера** → **DWH представления** → **Фактические таблицы** → **Хранимые процедуры**
2. **uni.vt_order** ← **fact_order** ← **sp_load_fact_order**
3. **uni.vt_sales_plan** ← **fact_sales_plan** ← **sp_load_fact_sales_plan**
4. **Данные заказов и планов** ← **1С система** ← **sp_load_all_data**

##### sp_load_fact_order
Загружает данные о заказах клиентов из 1С, включая информацию о суммах, скидках, статусах заказов, датах и связанных справочниках. Обрабатывает как реальные, так и плановые заказы.

##### sp_load_fact_sales_plan
Загружает данные о планах продаж из 1С, включая информацию о суммах контрактов, плановых наценках, прибыли и связанных справочниках. Обрабатывает как основные, так и корректировочные планы.

##### sp_load_all_data
Координирует загрузку всех данных в DWH, включая справочники, фактические таблицы и обновление связанных процедур.
"""


@mcp.prompt()
def lets_configure_session() -> str:
    res = "Let's configure the MCP Server tech-spec calling a special tool configure_session"
    return res

@mcp.tool()
def configure_session(session_id: str, procedures_dir: str, views_dir: str, olap_dir: str, store_doc_dir: str) -> str:
    """
    Configures the session by storing paths to directories for stored procedures and views.
    This tool must be called once before using other tools in the session.
    Args:
        session_id (str): A unique identifier for the user session.
        procedures_dir (str): The absolute path to the directory containing SQL stored procedures.
        views_dir (str): The absolute path to the directory containing SQL views.
        olap_dir (str): The absolute path to the directory containing .bim file.
        store_doc_dir (str): The absolute path to the directory where generated documentation will be saved.
    Returns:
        str: A confirmation message indicating that the session has been configured.
    """
    session_configs[session_id] = {
        "stored_procedures_dir": procedures_dir,
        "views_dir": views_dir,
        "olap_dir": olap_dir,
        "store_doc_dir": store_doc_dir
    }
    return f"Session {session_id} configured successfully."

def _generate_single_measure_prompt(measure: str, olap_dir: str, stored_procedures_dir: str, views_dir: str) -> str:
    """Helper function to generate a prompt for a single measure."""
    return f"""
=== TARGET STRUCTURE TEMPLATE ===
The following is the EXACT structure you MUST follow when creating the technical specification:
{SAMPLE_TECHNICAL_SPECIFICATION}
=== END OF TEMPLATE ===

Instructions for measure '{measure}':

STEP 1: DATA EXTRACTION
- Locate the measure "{measure}" in the .bim file at '{olap_dir}'
- Extract all measure properties: name, expression, format, displayFolder, description

STEP 2: DATA LINEAGE ANALYSIS
- Trace OLAP tables used by the measure → DWH views in '{views_dir}'
- Trace views → stored procedures in '{stored_procedures_dir}' that populate underlying tables
- Analyze stored procedure logic to understand business transformations

STEP 3: GENERATE SPECIFICATION
Create a markdown document with the EXACT structure shown in the TARGET STRUCTURE TEMPLATE above.

CRITICAL REQUIREMENTS:
- Ignore any commented-out code in measure expressions
- Use EXACT heading levels: ## for measure title, ### for main sections, #### for subsections, ##### for stored procedures
- DAX code MUST be in ```dax blocks
- Data flow section MUST have numbered items with arrow notation
- Structure MUST be IDENTICAL to the template - NO deviations allowed
"""

@mcp.tool()
def ts_measure_new_doc(
    measure: str,  # The exact name of the measure to analyze from the OLAP project (.bim file)
    session_id: str,  # A unique identifier for the user session, used to retrieve configuration
) -> str:
    """
    Generate a detailed technical specification document for a measure, including its data lineage.
    
    This tool analyzes a measure from a .bim file and its underlying data sources (views, stored procedures)
    to create a comprehensive technical specification in a new markdown document. The specification includes 
    measure definition, calculation logic, OLAP dependencies, and a high-level description of the data flow.
    
    Args:
        measure (str): The exact name of the measure to analyze from the OLAP project (.bim file).
        session_id (str): The unique identifier for the session, provided after calling 'configure_session'.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to perform the analysis and create the document.
    """
    if session_id not in session_configs:
        return "Error: Session not configured. Please call 'configure_session' first."
    config = session_configs[session_id]
    stored_procedures_dir = config["stored_procedures_dir"]
    views_dir = config["views_dir"]
    olap_dir = config["olap_dir"]
    store_doc_dir = config["store_doc_dir"]
    
    base_prompt = _generate_single_measure_prompt(measure, olap_dir, stored_procedures_dir, views_dir)
    
    prompt = f"""Create a technical specification markdown file for measure: "{measure}".
{base_prompt}
The .bim file is a Power BI Desktop project file that contains the data model, measures, and relationships. Use it, along with the provided SQL directories, as the source for the analysis to create human-readable documentation following the technical specification format from the template."""

    prompt += MANDATORY_SELF_VERIFICATION.format(store_doc_dir=store_doc_dir)
    
    return prompt


# Run the mcp
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)

