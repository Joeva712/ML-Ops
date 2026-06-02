from typing import Dict, List, Any, Optional

# Specification registries for major leaf categories.
# Defines required and optional fields, their types, units, and aliases.
SPEC_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Pistons": {
        "required": {
            "bore_diameter": {"type": "float", "unit": "mm", "aliases": ["bore", "diameter", "bore_size"], "typical_range": [50.0, 150.0]},
            "stroke": {"type": "float", "unit": "mm", "aliases": ["stroke_length"], "typical_range": [40.0, 120.0]},
            "material": {"type": "enum", "values": ["aluminum", "cast_iron", "forged_steel"], "aliases": ["piston_material"]},
            "compression_ratio": {"type": "float", "aliases": ["cr", "compression"], "typical_range": [8.0, 15.0]},
        },
        "optional": {
            "oem_part_number": {"type": "string", "aliases": ["oem", "part_no", "part_number"]},
            "weight": {"type": "float", "unit": "g", "typical_range": [150.0, 800.0]},
            "coating": {"type": "enum", "values": ["chrome", "moly", "dlc", "none"]},
        }
    },
    "Smartphones": {
        "required": {
            "ram": {"type": "float", "unit": "GB", "aliases": ["memory", "ram_size"], "typical_range": [2.0, 24.0]},
            "storage": {"type": "float", "unit": "GB", "aliases": ["capacity", "internal_storage", "rom"], "typical_range": [16.0, 1024.0]},
            "screen_size": {"type": "float", "unit": "inch", "aliases": ["display_size", "screen"], "typical_range": [4.0, 7.5]},
            "battery": {"type": "float", "unit": "mAh", "aliases": ["battery_capacity"], "typical_range": [2000.0, 7000.0]},
        },
        "optional": {
            "processor": {"type": "string", "aliases": ["cpu", "chipset"]},
            "camera_mp": {"type": "float", "unit": "MP", "aliases": ["camera", "megapixels"], "typical_range": [8.0, 200.0]},
        }
    },
    "Laundry Detergent": {
        "required": {
            "form": {"type": "enum", "values": ["powder", "liquid", "pods", "gel"], "aliases": ["detergent_form"]},
            "weight_volume": {"type": "float", "unit": "kg", "aliases": ["net_weight", "net_volume", "size", "volume"], "typical_range": [0.2, 20.0]},
        },
        "optional": {
            "scent": {"type": "string", "aliases": ["fragrance"]},
            "concentration": {"type": "float", "unit": "%", "typical_range": [1.0, 100.0]},
            "loads_per_pack": {"type": "int", "aliases": ["loads", "washes"], "typical_range": [5, 200]},
        }
    },
    "Interior Paint": {
        "required": {
            "finish": {"type": "enum", "values": ["matte", "eggshell", "satin", "semi-gloss", "gloss"], "aliases": ["sheen"]},
            "base": {"type": "enum", "values": ["water", "oil", "latex", "acrylic"], "aliases": ["paint_base"]},
            "volume": {"type": "float", "unit": "L", "aliases": ["size", "can_size"], "typical_range": [0.5, 25.0]},
        },
        "optional": {
            "coverage": {"type": "float", "unit": "m²/L", "aliases": ["coverage_rate", "spread_rate"], "typical_range": [5.0, 20.0]},
            "color": {"type": "string", "aliases": ["shade", "color_code"]},
            "voc": {"type": "float", "unit": "g/L", "typical_range": [0.0, 150.0]},
        }
    },
    "Exterior Paint": {
        "required": {
            "finish": {"type": "enum", "values": ["matte", "eggshell", "satin", "semi-gloss", "gloss"], "aliases": ["sheen"]},
            "base": {"type": "enum", "values": ["water", "oil", "latex", "acrylic"], "aliases": ["paint_base"]},
            "volume": {"type": "float", "unit": "L", "aliases": ["size", "can_size"], "typical_range": [0.5, 25.0]},
        },
        "optional": {
            "coverage": {"type": "float", "unit": "m²/L", "aliases": ["coverage_rate", "spread_rate"], "typical_range": [5.0, 20.0]},
            "color": {"type": "string", "aliases": ["shade", "color_code"]},
            "voc": {"type": "float", "unit": "g/L", "typical_range": [0.0, 150.0]},
        }
    },
    "Tempered Glass": {
        "required": {
            "thickness": {"type": "float", "unit": "mm", "typical_range": [2.0, 25.0]},
            "width": {"type": "float", "unit": "mm", "typical_range": [100.0, 6000.0]},
            "height": {"type": "float", "unit": "mm", "typical_range": [100.0, 6000.0]},
        },
        "optional": {
            "tint": {"type": "enum", "values": ["clear", "bronze", "gray", "green", "blue"]},
            "u_value": {"type": "float", "unit": "W/m²K", "typical_range": [0.5, 6.0]},
        }
    },
    "Steel Sheet": {
        "required": {
            "grade": {"type": "string", "aliases": ["steel_grade", "material_grade"]},
            "thickness": {"type": "float", "unit": "mm", "typical_range": [0.1, 50.0]},
        },
        "optional": {
            "width": {"type": "float", "unit": "mm", "typical_range": [50.0, 3000.0]},
            "length": {"type": "float", "unit": "mm", "typical_range": [100.0, 12000.0]},
            "surface_finish": {"type": "enum", "values": ["mill", "polished", "brushed", "anodized", "2b"]},
        }
    },
    "Palm Oil": {
        "required": {
            "volume": {"type": "float", "unit": "L", "typical_range": [0.5, 20000.0]},
            "packaging": {"type": "enum", "values": ["bottle", "jerry_can", "drum", "flexitank", "bulk"]},
        },
        "optional": {
            "refined": {"type": "bool", "aliases": ["is_refined", "refined_oil"]},
            "ffa": {"type": "float", "unit": "%", "typical_range": [0.01, 5.0]},
        }
    },
    "OPC Cement": {
        "required": {
            "grade": {"type": "enum", "values": ["33", "43", "53"], "aliases": ["cement_grade"]},
            "weight": {"type": "float", "unit": "kg", "typical_range": [1.0, 100.0]},
        },
        "optional": {
            "compressive_strength": {"type": "float", "unit": "MPa", "typical_range": [30.0, 80.0]},
            "setting_time": {"type": "float", "unit": "min", "typical_range": [30.0, 600.0]},
        }
    }
}

def get_spec_schema(leaf_category: str) -> Optional[Dict[str, Any]]:
    """Get the specification schema for a leaf category."""
    # Find matching key (case-insensitive)
    for cat_name, schema in SPEC_REGISTRY.items():
        if cat_name.lower() == leaf_category.lower():
            return schema
    # Fallback to general base structure
    return None
