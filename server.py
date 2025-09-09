from fastmcp import FastMCP
from typing import Optional, List
import os
import json

# Create an MCP Server
mcp = FastMCP("Creating Technical Specification Service")

def _generate_single_measure_prompt(measure: str, existing_doc_dir: str, olap_dir: str) -> str:
    """Helper function to generate a prompt for a single measure."""
    return f"""
Instructions for measure '{measure}':
1. Locate and analyze the specified measure "{measure}" in the .bim file located in the directory '{olap_dir}'.
2. Extract measure properties (name, expression, format, displayFolder, etc.).
3. Identify dependencies and related objects.
4. Generate a comprehensive technical specification definition following the format from the existing document at '{existing_doc_dir}'.
5. Add the new definition to the existing markdown file, maintaining consistency with the existing format.
6. Important: Ignore any commented-out code within the measure's expression; it should not be included in the technical specification.
"""

@mcp.tool()
def ts_measure_new_doc(
    measure: str,  # The exact name of the measure to analyze from the OLAP project (.bim file)
    olap_dir: Optional[str] = None,  # Path to the directory containing the .bim file
    example_tech_spec_dir: Optional[str] = None  # Path to markdown file with example template
) -> str:
    """
    Generate a detailed technical specification document for a specific measure from an OLAP project.
    
    This tool analyzes a measure from a .bim (Business Intelligence Model) file and creates a comprehensive
    technical specification document in markdown format. The specification includes measure definition,
    calculation logic, dependencies, and usage guidelines based on the provided example template.
    
    Args:
        measure (str): The exact name of the measure to analyze from the OLAP project (.bim file).
                      This should match the measure name as it appears in the model.
        olap_dir (str, optional): Path to the directory containing the .bim file. 
                                 If not provided, the tool will search in common locations.
        example_tech_spec_dir (str, optional): Path to a markdown file containing an example 
                                              technical specification template to follow for formatting.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to:
             - Locate and analyze the specified measure in the .bim file
             - Extract measure properties (name, expression, format, etc.)
             - Identify dependencies and related objects
             - Generate a comprehensive technical specification document
             - Format the output according to the provided example template
    
    Example:
        tech_spec_by_measure("Total Sales", "/path/to/olap", "/path/to/template.md")
        # Returns a prompt for analyzing "Total Sales" measure and creating its specification
    
    Note:
        The .bim file is a Power BI Desktop project file that contains the data model,
        measures, and relationships. The tool generates instructions for an LLM to parse
        this file and create human-readable documentation.
    """
    
    # Set default paths if not provided
    if not olap_dir:
        olap_dir = "/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP"
    
    if not example_tech_spec_dir:
        example_tech_spec_dir = "/Users/eremenkoivan/Projects/PythonProjects/MCPTechSpec/ТЗ DWH ETL.md"
    
    # Create detailed prompt for LLM
    prompt = f"""Create a technical specification markdown file for measure: "{measure}" which is from a .bim file located in directory {olap_dir} and format it like the example in the file {example_tech_spec_dir}. 

Instructions:
1. Locate and analyze the specified measure "{measure}" in the .bim file
2. Extract measure properties (name, expression, format, displayFolder, etc.)
3. Identify dependencies and related objects
4. Generate a comprehensive technical specification document following the format from the example template
5. Save the new markdown file in the same directory where the {example_tech_spec_dir} file is located
6. Important: Ignore any commented-out code within the measure's expression; it should not be included in the technical specification.

The .bim file is a Power BI Desktop project file that contains the data model, measures, and relationships. Parse this file and create human-readable documentation following the technical specification format from the example."""
    
    return prompt


@mcp.tool()
def ts_measure_existing_doc(
    measure: str,  # The exact name of the measure to analyze from the OLAP project (.bim file)
    existing_doc_dir: str,  # Path to the existing document which contains technical specification
    olap_dir: Optional[str] = None,  # Path to the directory containing the .bim file   
    replace_existing_measure: bool = True, # Indicate does a measure should be rewrite if already exists in the existing_doc_dir
) -> str:
    """
    Generate a detailed technical specification definition for a specific measure from an OLAP project and add it to an existing document.
    
    This tool analyzes a measure from a .bim (Business Intelligence Model) file and creates a comprehensive
    technical specification definition in markdown format, adding it to an existing document which already contains similar technical specifications
    for other measures. The specification includes measure definition, calculation logic, dependencies, and usage guidelines 
    based on the format of the existing document.
    
    Args:
        measure (str): The exact name of the measure to analyze from the OLAP project (.bim file).
                      This should match the measure name as it appears in the model.
        existing_doc_dir (str): Path to the existing document which contains technical specifications.
        olap_dir (str, optional): Path to the directory containing the .bim file. 
                                 If not provided, the tool will search in common locations.
        replace_existing_measure (bool, optional): If True and a definition for the measure already exists, it will be replaced. Defaults to True.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to:
             - Locate and analyze the specified measure in the .bim file
             - Extract measure properties (name, expression, format, etc.)
             - Identify dependencies and related objects
             - Generate a comprehensive technical specification definition
             - Format the output according to the provided existing document
             - Add the new specification to the existing document
    
    Example:
        tech_spec_by_measure_existing_doc("Total Sales", "/path/to/existing_doc.md", "/path/to/olap")
        # Returns a prompt for analyzing "Total Sales" measure and adding its specification to existing document
    
    Note:
        The .bim file is a Power BI Desktop project file that contains the data model,
        measures, and relationships. The tool generates instructions for an LLM to parse
        this file and create human-readable documentation.
    """

    # Set default paths if not provided
    if not olap_dir:
        olap_dir = "/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP"
    
    # Create detailed prompt for LLM
    base_prompt = _generate_single_measure_prompt(measure, existing_doc_dir, olap_dir)
    
    prompt = f"""Create a technical specification definition in markdown format for measure: "{measure}".
{base_prompt}
The .bim file is a Power BI Desktop project file that contains the data model, measures, and relationships. Parse this file and create human-readable documentation following the technical specification format from the existing document."""

    if replace_existing_measure:
        prompt += f"\nIf a definition for measure '{measure}' already exists in '{existing_doc_dir}', replace it with the new one. Otherwise, add the new definition."
    else:
        prompt += f"\nIf a definition for measure '{measure}' already exists in '{existing_doc_dir}', do not change it. Add the new definition only if it does not exist."

    return prompt


@mcp.tool()
def ts_list_measures_existing_doc(
    list_measures_dir: str,  # Path to the existing document which contains list of measure names
    existing_doc_dir: str,  # Path to the existing document which contains technical specifications
    olap_dir: Optional[str] = None,  # Path to the directory containing the .bim file  
    replace_existing_measure: bool = True,
) -> str:
    """
    Generate detailed technical specification definitions for each specific measure listed in a certain file, where measure names correspond to
    measures from an OLAP project and add them to an existing document.
    
    This tool analyzes measures from a .bim (Business Intelligence Model) file and creates comprehensive
    technical specification definitions in markdown format for each measure listed in a certain file, adding them to an existing document which already contains similar technical specifications
    for other measures. The specification includes measure definition, calculation logic, dependencies, and usage guidelines 
    based on the format of the existing document.
    
    Args:
        list_measures_dir (str): Path to the existing document which contains list of measure names
        existing_doc_dir (str): Path to the existing document which contains technical specifications.
        olap_dir (str, optional): Path to the directory containing the .bim file. 
                                 If not provided, the tool will search in common locations.
        replace_existing_measure (bool, optional): If True and a definition for a measure already exists, it will be replaced. Defaults to True.
    
    Returns:
        str: A detailed prompt string that instructs an LLM to:
             - Iteratively take each separate measure from the specified file
             - Locate and analyze the specified measure in the .bim file
             - Extract measure properties (name, expression, format, etc.)
             - Identify dependencies and related objects
             - Generate a comprehensive technical specification definition
             - Format the output according to the provided existing document
             - Add the new specification to the existing document
    
    Example:
        tech_spec_list_measures_existing_doc("/path/to/measure_list.md", "/path/to/existing_doc.md", "/path/to/olap")
        # Returns a prompt for analyzing each separate measure listed in the specified file and adding its specification to existing document
    
    Note:
        The .bim file is a Power BI Desktop project file that contains the data model,
        measures, and relationships. The tool generates instructions for an LLM to parse
        this file and create human-readable documentation.
    """

    # Set default paths if not provided
    if not olap_dir:
        olap_dir = "/Users/eremenkoivan/Library/CloudStorage/OneDrive-TWIGACG/agrotek/OLAP"
    
    try:
        with open(list_measures_dir, 'r', encoding='utf-8') as f:
            # Clean measure names by removing brackets and stripping whitespace
            measures = [line.strip().replace('[', '').replace(']', '') for line in f if line.strip()]
    except FileNotFoundError:
        return f"Error: The file '{list_measures_dir}' was not found."
    except Exception as e:
        return f"An error occurred while reading '{list_measures_dir}': {e}"

    if not measures:
        return f"No measures found in '{list_measures_dir}'."

    # Create a combined prompt for all measures
    prompts = [f"Please perform the following tasks to update the technical specification document at '{existing_doc_dir}':"]
    for measure in measures:
        prompts.append(_generate_single_measure_prompt(measure, existing_doc_dir, olap_dir))

    final_prompt = "\n".join(prompts)
    final_prompt += "\nThe .bim file is a Power BI Desktop project file that contains the data model, measures, and relationships. Parse this file and create human-readable documentation for each measure, appending it to the specified document."

    if replace_existing_measure:
        final_prompt += f"\nFor each measure, if a definition already exists in '{existing_doc_dir}', replace it with the new one. Otherwise, add the new definition."
    else:
        final_prompt += f"\nFor each measure, if a definition already exists in '{existing_doc_dir}', do not change it. Add the new definition only if it does not exist."

    return final_prompt


# Run the mcp
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)

