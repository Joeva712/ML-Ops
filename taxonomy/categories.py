from typing import Dict, List, Optional

# Hierarchical category structure: Top-level -> Subcategory -> Leaf
CATEGORY_TREE: Dict[str, Dict[str, List[str]]] = {
    "Electronics": {
        "Smartphones & Tablets": ["Smartphones", "Tablets"],
        "Laptops & Computers": ["Laptops", "Desktops", "Monitors"],
        "Components": ["Resistors", "Capacitors", "ICs", "PCBs"]
    },
    "Automotive": {
        "Engine Components": ["Pistons", "Crankshafts", "Camshafts", "Gaskets & Seals", "Turbochargers"],
        "Brake Systems": ["Brake Pads", "Brake Rotors", "Calipers"],
        "Suspension": ["Shock Absorbers", "Coil Springs", "Control Arms"]
    },
    "Chemicals & Cleaning": {
        "Detergent & Cleaning": ["Laundry Detergent", "Dish Soap", "Floor Cleaner", "Industrial Degreaser"],
        "Adhesives & Sealants": ["Epoxy Adhesive", "Silicone Sealant", "Super Glue"]
    },
    "Paints & Coatings": {
        "Architectural Paint": ["Interior Paint", "Exterior Paint", "Primer"],
        "Industrial Coatings": ["Epoxy Coating", "Polyurethane Coating", "Powder Coat"]
    },
    "Glass & Ceramics": {
        "Flat Glass": ["Tempered Glass", "Laminated Glass", "Float Glass"],
        "Ceramics": ["Ceramic Tiles", "Sanitary Ware"]
    },
    "Raw Materials": {
        "Metals": ["Steel Sheet", "Steel Rebar", "Aluminum Extrusion", "Copper Wire"],
        "Plastics & Polymers": ["Polyethylene (PE)", "Polypropylene (PP)", "PVC Granules", "ABS Resin"]
    },
    "Food & Agriculture": {
        "Cooking Oil": ["Palm Oil", "Soybean Oil", "Sunflower Oil"],
        "Agriculture Supplies": ["Urea Fertilizer", "NPK Fertilizer", "Pesticides"]
    },
    "Construction": {
        "Cement & Concrete": ["OPC Cement", "PPC Cement", "Ready-Mix Concrete"],
        "Structural Materials": ["Beams & Columns", "Plywood Panels"]
    }
}

def get_flat_categories() -> List[List[str]]:
    """Returns all paths as lists: [Top, Sub, Leaf]"""
    paths = []
    for top, subs in CATEGORY_TREE.items():
        for sub, leaves in subs.items():
            for leaf in leaves:
                paths.append([top, sub, leaf])
    return paths

def get_leaf_categories() -> List[str]:
    """Returns a flat list of all leaf category names."""
    leaves = []
    for top, subs in CATEGORY_TREE.items():
        for sub, leaf_list in subs.items():
            leaves.extend(leaf_list)
    return leaves

def find_category_path(leaf_name: str) -> Optional[List[str]]:
    """Finds the full path for a given leaf name (case-insensitive fuzzy match)."""
    leaf_lower = leaf_name.lower()
    for top, subs in CATEGORY_TREE.items():
        for sub, leaves in subs.items():
            for leaf in leaves:
                if leaf.lower() == leaf_lower:
                    return [top, sub, leaf]
    return None
