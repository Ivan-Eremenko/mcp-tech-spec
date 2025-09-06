from fastmcp import FastMCP
from typing import Optional
import os
import json

# Create an MCP Server
mcp = FastMCP("Creating Technical Specification Service")

@mcp.tool()
def tech_spec_by_measure(
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

The .bim file is a Power BI Desktop project file that contains the data model, measures, and relationships. Parse this file and create human-readable documentation following the technical specification format from the example."""
    
    return prompt


# Run the mcp
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
