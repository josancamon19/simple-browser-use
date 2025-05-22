from typing import Dict, Any, List, Optional
from playwright.sync_api import Page


def get_browser_state(page: Page) -> str:
    # Get page metadata
    url = page.url
    title = page.title()
    
    # Start with page metadata
    yaml_lines = [
        f"url: {url}",
        f"title: {title}",
        f"viewport: {page.viewport_size}",
        "elements:"
    ]
    
    # Get the accessibility tree from Playwright
    accessibility_snapshot = page.accessibility.snapshot()

    # Counter for unique element references
    ref_counter = 1

    def process_node(node: Dict[str, Any], indent: int = 1, path: List[str] = []) -> None:
        nonlocal ref_counter

        # Skip nodes without a role (usually non-interactive elements)
        if "role" not in node:
            return

        # Format the node entry
        node_description = []
        node_attributes = {}

        # Add the role (element type)
        role = node.get("role", "generic")
        node_description.append(role)
        node_attributes["role"] = role

        # Add the name (usually text content) if available
        if node.get("name"):
            node_description.append(f'"{node["name"]}"')
            node_attributes["name"] = node.get("name")

        # Add any states and attributes
        for attr in ["value", "description", "placeholder"]:
            if attr in node and node[attr]:
                node_attributes[attr] = node[attr]
                node_description.append(f"[{attr}=\"{node[attr]}\"]")
                
        # Add boolean states
        for state in ["checked", "selected", "disabled", "required", "readonly", "expanded", "pressed", "busy"]:
            if node.get(state):
                node_description.append(f"[{state}]")
                node_attributes[state] = True
        
        # Add aria attributes if present
        for key in node:
            if key.startswith("aria") and node[key]:
                node_attributes[key] = node[key]
                node_description.append(f"[{key}=\"{node[key]}\"]")
                
        # Add HTML tag if available
        if "tag" in node:
            node_attributes["tag"] = node["tag"]
            node_description.append(f"[tag={node['tag']}]")
            
        # Add CSS classes if available
        if "className" in node:
            node_attributes["className"] = node["className"]
            node_description.append(f"[class=\"{node['className']}\"]")

        # Add a unique reference ID for this element
        ref_id = f"e{ref_counter}"
        ref_counter += 1
        node_description.append(f"[ref={ref_id}]")
        node_attributes["ref"] = ref_id
        
        # Add DOM path if possible
        current_path = path + [role]
        path_str = " > ".join(current_path)
        node_attributes["path"] = path_str
        
        # Determine if element is likely interactive
        is_interactive = role in ["button", "link", "textbox", "checkbox", "radio", "combobox", 
                                 "listbox", "menuitem", "menuitemcheckbox", "menuitemradio", 
                                 "option", "switch", "tab"]
        if is_interactive:
            node_description.append("[interactive]")
            node_attributes["interactive"] = True

        # Create the full node entry with proper indentation
        prefix = "  " * indent
        entry = f"{prefix}- {' '.join(node_description)}"
        yaml_lines.append(entry)
        
        # Add attributes as nested properties with additional indent
        attr_prefix = "  " * (indent + 1)
        for key, value in node_attributes.items():
            # Format value correctly based on type
            if isinstance(value, str):
                formatted_value = f'"{value}"' if " " in value else value
            else:
                formatted_value = str(value).lower()  # Convert True/False to true/false
                
            yaml_lines.append(f"{attr_prefix}{key}: {formatted_value}")

        # Process children if any exist
        children = node.get("children", [])
        if children:
            yaml_lines.append(f"{attr_prefix}children:")
            for child in children:
                process_node(child, indent + 2, current_path)

    # Start with the root node
    if accessibility_snapshot:
        process_node(accessibility_snapshot)
    else:
        yaml_lines.append("  - No accessibility content available")
        
    # Add focused element information
    try:
        focused_element = page.evaluate("() => { const el = document.activeElement; return el ? { tagName: el.tagName, id: el.id, className: el.className } : null; }")
        if focused_element:
            yaml_lines.append("focused_element:")
            for key, value in focused_element.items():
                yaml_lines.append(f"  {key}: {value}")
    except:
        yaml_lines.append("focused_element: Unknown")
    
    # Add visible text count (helpful to determine content richness)
    try:
        text_count = page.evaluate("() => document.body.innerText.split(/\\s+/).filter(Boolean).length")
        yaml_lines.append(f"text_word_count: {text_count}")
    except:
        pass
        
    # Return the YAML-formatted snapshot
    return "\n".join(yaml_lines)
