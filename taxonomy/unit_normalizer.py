import re
from typing import Tuple, Optional, Dict, Any

class UnitNormalizer:
    # Target standard base units for each category
    # Length -> mm
    # Weight -> kg (or g for pistons)
    # Volume -> L
    # Storage -> GB

    LENGTH_CONVERSIONS = {
        "mm": 1.0,
        "millimeter": 1.0,
        "millimeters": 1.0,
        "cm": 10.0,
        "centimeter": 10.0,
        "centimeters": 10.0,
        "m": 1000.0,
        "meter": 1000.0,
        "meters": 1000.0,
        "inch": 25.4,
        "inches": 25.4,
        "\"": 25.4,
        "in": 25.4,
        "ft": 304.8,
        "foot": 304.8,
        "feet": 304.8,
        "yd": 914.4,
        "yard": 914.4,
        "yards": 914.4,
    }

    WEIGHT_CONVERSIONS = {
        "kg": 1.0,
        "kilogram": 1.0,
        "kilograms": 1.0,
        "g": 0.001,
        "gram": 0.001,
        "grams": 0.001,
        "lb": 0.45359237,
        "lbs": 0.45359237,
        "pound": 0.45359237,
        "pounds": 0.45359237,
        "oz": 0.028349523,
        "ounce": 0.028349523,
        "ounces": 0.028349523,
        "ton": 1000.0,
        "tons": 1000.0,
        "tonne": 1000.0,
        "tonnes": 1000.0,
    }

    VOLUME_CONVERSIONS = {
        "l": 1.0,
        "liter": 1.0,
        "liters": 1.0,
        "litre": 1.0,
        "litres": 1.0,
        "ml": 0.001,
        "milliliter": 0.001,
        "milliliters": 0.001,
        "gal": 3.78541,
        "gallon": 3.78541,
        "gallons": 3.78541,
        "fl oz": 0.0295735,
        "m3": 1000.0,
        "m³": 1000.0,
    }

    STORAGE_CONVERSIONS = {
        "gb": 1.0,
        "gigabyte": 1.0,
        "gigabytes": 1.0,
        "mb": 0.001,
        "megabyte": 0.001,
        "tb": 1000.0,
        "terabyte": 1000.0,
    }

    @classmethod
    def parse_numeric_and_unit(cls, val_str: str) -> Tuple[Optional[float], Optional[str]]:
        """Parses a string like '96mm' or '256 GB' or '6.7\"' into (value, unit_string)."""
        if not isinstance(val_str, str):
            if isinstance(val_str, (int, float)):
                return float(val_str), None
            return None, None

        # Clean string
        val_str = val_str.strip().lower()
        
        # Match pattern: number (with decimals) followed by optional spaces and unit
        match = re.match(r"^([\d\.]+)\s*([a-zA-Z°³\"\s]+)?$", val_str)
        if not match:
            return None, None

        num_val = float(match.group(1))
        unit_str = match.group(2).strip() if match.group(2) else None
        return num_val, unit_str

    @classmethod
    def normalize_value(cls, val_any: Any, target_type: str, target_unit: Optional[str] = None) -> Tuple[Any, Optional[str]]:
        """Normalizes a single value to the target type and base unit."""
        if val_any is None:
            return None, None

        if target_type == "float" or target_type == "int":
            num_val, unit = cls.parse_numeric_and_unit(str(val_any))
            if num_val is None:
                return val_any, None

            # Perform unit conversion if target unit is specified
            if target_unit and unit:
                unit = unit.strip().lower()
                converted_val = None
                
                # Check conversion tables
                if target_unit == "mm" and unit in cls.LENGTH_CONVERSIONS:
                    converted_val = num_val * cls.LENGTH_CONVERSIONS[unit]
                elif target_unit == "kg" and unit in cls.WEIGHT_CONVERSIONS:
                    converted_val = num_val * cls.WEIGHT_CONVERSIONS[unit]
                elif target_unit == "L" and unit in cls.VOLUME_CONVERSIONS:
                    converted_val = num_val * cls.VOLUME_CONVERSIONS[unit]
                elif target_unit == "GB" and unit in cls.STORAGE_CONVERSIONS:
                    converted_val = num_val * cls.STORAGE_CONVERSIONS[unit]
                
                if converted_val is not None:
                    return int(converted_val) if target_type == "int" else converted_val, target_unit

            return int(num_val) if target_type == "int" else num_val, unit or target_unit

        elif target_type == "enum":
            return str(val_any).strip().lower(), None
        elif target_type == "bool":
            if isinstance(val_any, bool):
                return val_any, None
            s = str(val_any).strip().lower()
            return s in ("true", "1", "yes", "y", "refined"), None
        else:
            return str(val_any).strip(), None

    @classmethod
    def normalize_specifications(cls, specs: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a spec dict based on a spec schema registry."""
        normalized = {}
        for key, val in specs.items():
            # Find the spec in the schema (required or optional)
            spec_def = None
            found_key = key
            
            # Check required specs
            for s_key, s_def in schema.get("required", {}).items():
                aliases = [s_key] + s_def.get("aliases", [])
                if key.lower() in [a.lower() for a in aliases]:
                    spec_def = s_def
                    found_key = s_key
                    break
            
            # Check optional specs
            if not spec_def:
                for s_key, s_def in schema.get("optional", {}).items():
                    aliases = [s_key] + s_def.get("aliases", [])
                    if key.lower() in [a.lower() for a in aliases]:
                        spec_def = s_def
                        found_key = s_key
                        break
            
            if spec_def:
                target_type = spec_def.get("type", "string")
                target_unit = spec_def.get("unit")
                norm_val, _ = cls.normalize_value(val, target_type, target_unit)
                normalized[found_key] = norm_val
            else:
                # Keep unrecognized specs as-is
                normalized[key] = val
                
        return normalized
