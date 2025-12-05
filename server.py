from fastmcp import FastMCP
from typing import Optional, Dict
import os

# Create an MCP Server
mcp = FastMCP("Creating Technical Specification Service")

# Global store for session configurations
session_configs: Dict[str, Dict[str, str]] = {}

# Reusable self-verification prompt block
MANDATORY_SELF_VERIFICATION = """

MANDATORY SELF-VERIFICATION:
After creating the specification, you MUST:
1. Open file '{existing_doc_dir}' and find any existing measure
2. Compare the created structure with the found measure section by section
3. Fix ALL differences in formatting, headers, section order
4. Verify that "Data Flow" section exactly matches the example from the document
5. Only after complete structural compliance, save the file"""

# Self-verification block for multiple measures
MANDATORY_SELF_VERIFICATION_MULTIPLE = """

MANDATORY SELF-VERIFICATION:
After creating all measure specifications, you MUST:
1. Open file '{existing_doc_dir}' and find any existing measure
2. Compare each created structure with the found measure section by section
3. Fix ALL differences in formatting, headers, section order for each measure
4. Verify that "Data Flow" sections exactly match the example from the document
5. Only after complete structural compliance for all measures, save the file"""

@mcp.prompt()
def lets_configure_session() -> str:
    res = "Let's configure the MCP Server tech-spec calling a special tool configure_session"
    return res

@mcp.tool()
def configure_session(session_id: str, procedures_dir: str, views_dir: str) -> str:
    """
    Configures the session by storing paths to directories for stored procedures and views.
    This tool must be called once before using other tools in the session.
    Args:
        session_id (str): A unique identifier for the user session.
        procedures_dir (str): The absolute path to the directory containing SQL stored procedures.
        views_dir (str): The absolute path to the directory containing SQL views.
    Returns:
        str: A confirmation message indicating that the session has been configured.
    """
    session_configs[session_id] = {
        "stored_procedures_dir": procedures_dir,
        "views_dir": views_dir
    }
    return f"Session {session_id} configured successfully."

def _generate_single_measure_prompt(measure: str, existing_doc_dir: str, olap_dir: str, stored_procedures_dir: str, views_dir: str) -> str:
    """Helper function to generate a prompt for a single measure."""
    return f"""
Instructions for measure '{measure}':
1. Locate and analyze the specified measure "{measure}" in the .bim file located in the directory '{olap_dir}'.
2. Extract measure properties (name, expression, format, displayFolder, etc.).
3. Analyze the data lineage:
   a. Trace data from the OLAP tables used by the measure back to the source DWH views in the directory '{views_dir}'.
   b. Then, trace the data from those views back to the stored procedures in '{stored_procedures_dir}' that populate the underlying tables.
   c. Analyze the logic of the identified stored procedure(s) to understand the business logic and data transformations.
4. Generate a comprehensive technical specification definition. CRITICALLY IMPORTANT: the output must be IDENTICAL in structure to existing measures in '{existing_doc_dir}'. Any deviation from the structure is UNACCEPTABLE.
5. Include the data lineage findings (from step 3) within the generated specification, placing it in an appropriate section (like "Dependencies" or "Data Flow") that aligns with the style of '{existing_doc_dir}'.
    5.1. Note: It is crucial to provide a common definition for all listed stored procedures associated with the dataflow for the '{measure}' measure.
6. Add the new definition to the existing markdown file, maintaining consistency with the document's format.
    6.1. After adding the new measure definition, MANDATORY execute the following structure validation:
        a) Ensure sections follow STRICTLY this order: 1. General Information, 2. Purpose, 3. Source Data, 4. Processing Logic, 5. Filter Conditions, 6. Dependencies (with subsections 6.1-6.4)
        b) Verify that section "6.4. Data Flow" contains ALL elements: OLAP measure → DWH Views → Fact Tables → Stored Procedures → Description of each procedure
        c) Check formatting compliance: heading levels (###, ####), DAX code formatting in ```dax blocks, numbered lists in data flow
        d) Compare final structure with any existing measure in the document and eliminate ALL differences in formatting and section order
7. Important: Ignore any commented-out code within the measure's expression; it should not be included in the technical specification.
8. CRITICALLY IMPORTANT - FINAL VALIDATION:
   After creating the technical specification, perform step-by-step verification:
   - Read the created measure description and compare its structure with any other measure in the document
   - Check EVERY header, EVERY subsection, EVERY formatting element
   - If structural differences are found, fix them IMMEDIATELY
   - Ensure stored procedure descriptions follow exactly the same format as in other measures
9. MANDATORY CHECKLIST before completion:
   ✓ Headers match the format (### for main sections, #### for subsections)
   ✓ "Data Flow" section has numbered list with 4 items
   ✓ Stored procedure descriptions are formatted as ##### headers
   ✓ DAX code is enclosed in ```dax blocks
   ✓ Structure is completely identical to existing measures in the document
"""

@mcp.tool()
def ts_measure_new_doc(
    measure: str,  # The exact name of the measure to analyze from the OLAP project (.bim file)
    session_id: str,  # A unique identifier for the user session, used to retrieve configuration
    olap_dir: Optional[str] = None,  # Path to the directory containing the .bim file
    example_tech_spec_dir: Optional[str] = None  # Path to markdown file with example template
) -> str:
    """
    Generate a detailed technical specification document for a measure, including its data lineage.
    
    This tool analyzes a measure from a .bim file and its underlying data sources (views, stored procedures)
    to create a comprehensive technical specification in a new markdown document. The specification includes 
    measure definition, calculation logic, OLAP dependencies, and a high-level description of the data flow.
    
    Args:
        measure (str): The exact name of the measure to analyze from the OLAP project (.bim file).
        session_id (str): The unique identifier for the session, provided after calling 'configure_session'.
        olap_dir (str, optional): Path to the directory containing the .bim file. 
                                 If not provided, the tool will search in common locations.
        example_tech_spec_dir (str, optional): Path to a markdown file containing an example 
                                              technical specification template to follow for formatting.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to perform the analysis and create the document.
    """
    if session_id not in session_configs:
        return "Error: Session not configured. Please call 'configure_session' first."
    config = session_configs[session_id]
    stored_procedures_dir = config["stored_procedures_dir"]
    views_dir = config["views_dir"]

    if not olap_dir:
        olap_dir = "/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP"
    
    if not example_tech_spec_dir:
        example_tech_spec_dir = "/Users/eremenkoivan/Projects/PythonProjects/MCPTechSpec/ТЗ DWH ETL.md"
    
    base_prompt = _generate_single_measure_prompt(measure, example_tech_spec_dir, olap_dir, stored_procedures_dir, views_dir)
    
    prompt = f"""Create a technical specification markdown file for measure: "{measure}".
{base_prompt}
The .bim file is a Power BI Desktop project file that contains the data model, measures, and relationships. Use it, along with the provided SQL directories, as the source for the analysis to create human-readable documentation following the technical specification format from the example.
Save the new markdown file in the same directory where the {example_tech_spec_dir} file is located."""

    prompt += MANDATORY_SELF_VERIFICATION.format(existing_doc_dir=example_tech_spec_dir)
    
    return prompt

@mcp.tool()
def ts_measure_existing_doc(
    measure: str,  # The exact name of the measure to analyze from the OLAP project (.bim file)
    existing_doc_dir: str,  # Path to the existing document which contains technical specifications
    session_id: str,  # A unique identifier for the user session, used to retrieve configuration
    olap_dir: Optional[str] = None,  # Path to the directory containing the .bim file   
    replace_existing_measure: bool = True,  # Indicates whether a measure should be rewritten if it already exists in the existing_doc_dir
) -> str:
    """
    Generate a detailed technical specification for a measure, including data lineage, and add it to an existing document.
    
    This tool analyzes a measure from a .bim file and its underlying data sources (views, stored procedures)
    to create a comprehensive technical specification. The specification includes measure definition,
    calculation logic, OLAP dependencies, and a high-level description of the data flow from DWH to the cube.
    The output is added to an existing markdown document.
    
    Args:
        measure (str): The exact name of the measure to analyze from the OLAP project (.bim file).
        existing_doc_dir (str): Path to the existing document which contains technical specifications.
        session_id (str): The unique identifier for the session, provided after calling 'configure_session'.
        olap_dir (str, optional): Path to the directory containing the .bim file. 
                                 If not provided, the tool will search in common locations.
        replace_existing_measure (bool, optional): If True and a definition for the measure already exists, it will be replaced. Defaults to True.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to perform the analysis and update the document.
    """
    if session_id not in session_configs:
        return "Error: Session not configured. Please call 'configure_session' first."
    config = session_configs[session_id]
    stored_procedures_dir = config["stored_procedures_dir"]
    views_dir = config["views_dir"]

    if not olap_dir:
        olap_dir = "/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP"
    
    base_prompt = _generate_single_measure_prompt(measure, existing_doc_dir, olap_dir, stored_procedures_dir, views_dir)
    
    prompt = f"""Create a technical specification definition in markdown format for measure: "{measure}".
{base_prompt}
The .bim file is a Power BI Desktop project file. Parse this file and create human-readable documentation following the technical specification format from the existing document."""

    if replace_existing_measure:
        prompt += f"\nIf a definition for measure '{measure}' already exists in '{existing_doc_dir}', replace it with the new one. Otherwise, add the new definition."
    else:
        prompt += f"\nIf a definition for measure '{measure}' already exists in '{existing_doc_dir}', do not change it. Add the new definition only if it does not exist."

    prompt += MANDATORY_SELF_VERIFICATION.format(existing_doc_dir=existing_doc_dir)

    return prompt

@mcp.tool()
def ts_list_measures_existing_doc(
    list_measures_dir: str,  # Path to the existing document which contains list of measure names
    existing_doc_dir: str,  # Path to the existing document which contains technical specifications
    session_id: str,  # A unique identifier for the user session, used to retrieve configuration
    olap_dir: Optional[str] = None,  # Path to the directory containing the .bim file  
    replace_existing_measure: bool = True,  # Indicate if measures should be rewritten if they already exist
) -> str:
    """
    Generate technical specifications for a list of measures, including data lineage, and add them to an existing document.
    
    The list of measures file should be structured with level 1 headings (#) for categories and level 2 headings (##) for measures.
    The tool will find or create the category in the existing document and add/update the measure specifications under it,
    including a new "Data Flow" section detailing the data lineage from DWH stored procedures and views.
    
    Args:
        list_measures_dir (str): Path to the existing document which contains list of measure names with categories.
        existing_doc_dir (str): Path to the existing document which contains technical specifications.
        session_id (str): The unique identifier for the session, provided after calling 'configure_session'.
        olap_dir (str, optional): Path to the directory containing the .bim file. 
                                 If not provided, the tool will search in common locations.
        replace_existing_measure (bool, optional): If True and a definition for a measure already exists, it will be replaced. Defaults to True.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to perform the update.
    """
    if session_id not in session_configs:
        return "Error: Session not configured. Please call 'configure_session' first."
    config = session_configs[session_id]
    stored_procedures_dir = config["stored_procedures_dir"]
    views_dir = config["views_dir"]

    if not olap_dir:
        olap_dir = "/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP"
    
    measures_by_category = {}
    current_category = None
    try:
        with open(list_measures_dir, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    current_category = line.lstrip('# ').strip()
                    if current_category not in measures_by_category:
                        measures_by_category[current_category] = []
                elif line.startswith('## '):
                    if current_category:
                        measure_name = line.lstrip('## ').strip().replace('[', '').replace(']', '')
                        measures_by_category[current_category].append(measure_name)
    except FileNotFoundError:
        return f"Error: The file '{list_measures_dir}' was not found."
    except Exception as e:
        return f"An error occurred while reading '{list_measures_dir}': {e}"

    if not measures_by_category:
        return f"No measures or categories found in '{list_measures_dir}'."

    instruction_lines = [
        f"You are tasked with updating the technical specification document located at '{existing_doc_dir}'.",
        "Follow these instructions carefully:",
    ]

    for category, measures in measures_by_category.items():
        instruction_lines.append(f"\n# Processing Category: '{category}'")
        instruction_lines.append(f"1. In the document '{existing_doc_dir}', locate the section starting with the heading '# {category}'.")
        instruction_lines.append(f"2. If this section does not exist, create it by adding the heading '# {category}' at the end of the document.")
        instruction_lines.append(f"3. Within this '{category}' section, generate and add/update the technical specifications for the following measures:")

        for measure in measures:
            base_prompt = _generate_single_measure_prompt(measure, existing_doc_dir, olap_dir, stored_procedures_dir, views_dir)
            instruction_lines.append(f"\n## For measure '{measure}':\n{base_prompt}")

    final_prompt = "\n".join(instruction_lines)
    
    final_prompt += f"\n\n## General Information"
    final_prompt += f"\nThe .bim file is a Power BI Desktop project file. Use it, along with the SQL directories, as the source for measure analysis."

    if replace_existing_measure:
        final_prompt += f"\nFor each measure, if a definition already exists under the correct category, replace it. Otherwise, add the new definition."
    else:
        final_prompt += f"\nFor each measure, add the new definition only if it does not already exist under the correct category."

    final_prompt += MANDATORY_SELF_VERIFICATION_MULTIPLE.format(existing_doc_dir=existing_doc_dir)

    return final_prompt

# Run the mcp
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)

