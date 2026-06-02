import re
from typing import Dict, List, Any, Optional, Tuple
from taxonomy.categories import find_category_path, get_leaf_categories
from taxonomy.spec_registry import get_spec_schema, SPEC_REGISTRY
from taxonomy.unit_normalizer import UnitNormalizer

# Simple Levenshtein distance implementation to avoid external dependencies
def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

# Known brands index for fuzzy lookup
KNOWN_BRANDS = [
    "Samsung", "Apple", "Xiaomi", "Oppo", "Vivo", "Asus", "Lenovo", "HP", "Dell", "Intel", "AMD",
    "Toyota", "Honda", "NPR", "Mahle", "Bosch", "Denso", "Koyo", "Mitsubishi", "Caterpillar",
    "Rinso", "Dulux", "Nippon Paint", "P&G", "Unilever", "Clorox", "Cargill", "Wilmar", "Musim Mas",
    "Asahi", "Corning", "Saint-Gobain", "Holcim", "Lafarge", "Dulux Weathershield"
]

class InputCorrector:
    @classmethod
    def fuzzy_match_brand(cls, brand: str) -> Tuple[str, float, Optional[str]]:
        """
        Fuzzy matches a brand name against KNOWN_BRANDS.
        Returns (best_match, confidence, message)
        """
        if not brand:
            return brand, 1.0, None
            
        brand_clean = brand.strip()
        brand_lower = brand_clean.lower()
        
        # Exact match check
        for kb in KNOWN_BRANDS:
            if kb.lower() == brand_lower:
                return kb, 1.0, None
                
        # Levenshtein search
        best_match = brand_clean
        best_dist = 999
        
        for kb in KNOWN_BRANDS:
            dist = levenshtein_distance(brand_lower, kb.lower())
            if dist < best_dist:
                best_dist = dist
                best_match = kb
                
        # Confidence formula: 1.0 - (dist / max_len)
        max_len = max(len(brand_clean), len(best_match))
        confidence = 1.0 - (best_dist / max_len) if max_len > 0 else 0.0
        
        if confidence >= 0.95:
            return best_match, confidence, f"Auto-corrected brand: '{brand_clean}' -> '{best_match}' (Confidence: {confidence:.2f})"
        elif confidence >= 0.75:
            return best_match, confidence, f"Suggested brand: '{best_match}' (Confidence: {confidence:.2f})"
        else:
            # Unrecognized brand
            return brand_clean, 0.0, None

    @classmethod
    def fuzzy_match_category(cls, category_input: Any) -> Tuple[List[str], float, Optional[str]]:
        """
        Fuzzy matches a category name or path segment to our hierarchical categories.
        """
        if not category_input:
            return [], 0.0, "Empty category path"

        # If it's a string, we treat it as the leaf category and try to find path
        leaf_name = ""
        if isinstance(category_input, str):
            leaf_name = category_input.strip()
        elif isinstance(category_input, list) and len(category_input) > 0:
            leaf_name = category_input[-1].strip()
            
        if not leaf_name:
            return [], 0.0, "Invalid category format"

        # Exact match
        path = find_category_path(leaf_name)
        if path:
            return path, 1.0, None

        # Fuzzy match leaf category
        all_leaves = get_leaf_categories()
        best_leaf = None
        best_dist = 999
        for leaf in all_leaves:
            dist = levenshtein_distance(leaf_name.lower(), leaf.lower())
            if dist < best_dist:
                best_dist = dist
                best_leaf = leaf

        max_len = max(len(leaf_name), len(best_leaf)) if best_leaf else 1
        confidence = 1.0 - (best_dist / max_len)
        
        if confidence >= 0.70 and best_leaf:
            path = find_category_path(best_leaf)
            if path:
                msg = f"Auto-corrected category path: '{category_input}' -> {path} (Confidence: {confidence:.2f})"
                return path, confidence, msg
                
        return [category_input] if isinstance(category_input, str) else category_input, 0.0, "Category not found in taxonomy"

    @classmethod
    def correct_specifications(cls, specs: Dict[str, Any], leaf_category: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Validates and corrects specifications based on the category's spec registry.
        """
        schema = get_spec_schema(leaf_category)
        if not schema:
            return specs, []

        corrected_specs = {}
        corrections = []

        # Iterate over all specifications provided
        for key, val in specs.items():
            found_def = None
            found_key = key
            is_required = False

            # Check if key matches required specs or their aliases
            for req_key, req_def in schema["required"].items():
                aliases = [req_key] + req_def.get("aliases", [])
                if key.lower() in [a.lower() for a in aliases]:
                    found_def = req_def
                    found_key = req_key
                    is_required = True
                    break

            # Check optional specs if not found in required
            if not found_def:
                for opt_key, opt_def in schema.get("optional", {}).items():
                    aliases = [opt_key] + opt_def.get("aliases", [])
                    if key.lower() in [a.lower() for a in aliases]:
                        found_def = opt_def
                        found_key = opt_key
                        break

            if found_def:
                # Key correction notification
                if key != found_key:
                    corrections.append({
                        "field": f"specifications.{key}",
                        "type": "spec_key_correction",
                        "severity": "auto_corrected",
                        "original": key,
                        "corrected": found_key,
                        "confidence": 0.95,
                        "message": f"Spec key corrected: '{key}' -> '{found_key}'"
                    })

                # Validate and normalize value
                val_type = found_def.get("type")
                val_unit = found_def.get("unit")
                
                # Perform unit normalization
                normalized_val, val_parsed_unit = UnitNormalizer.normalize_value(val, val_type, val_unit)
                
                if val_type == "enum":
                    enum_vals = found_def.get("values", [])
                    if normalized_val not in enum_vals:
                        # Fuzzy match enum values
                        best_enum = None
                        best_dist = 999
                        for ev in enum_vals:
                            dist = levenshtein_distance(normalized_val, ev)
                            if dist < best_dist:
                                best_dist = dist
                                best_enum = ev
                        
                        max_len = max(len(normalized_val), len(best_enum)) if best_enum else 1
                        enum_conf = 1.0 - (best_dist / max_len)
                        
                        if enum_conf >= 0.80 and best_enum:
                            corrections.append({
                                "field": f"specifications.{found_key}",
                                "type": "enum_correction",
                                "severity": "auto_corrected",
                                "original": val,
                                "corrected": best_enum,
                                "confidence": enum_conf,
                                "message": f"Corrected value for '{found_key}': '{val}' -> '{best_enum}'"
                            })
                            normalized_val = best_enum
                        else:
                            corrections.append({
                                "field": f"specifications.{found_key}",
                                "type": "invalid_enum",
                                "severity": "warning",
                                "original": val,
                                "corrected": None,
                                "confidence": 0.0,
                                "message": f"Value '{val}' for '{found_key}' is not in allowed values: {enum_vals}"
                            })

                elif val_type in ("float", "int") and isinstance(normalized_val, (int, float)):
                    typical_range = found_def.get("typical_range")
                    if typical_range:
                        r_min, r_max = typical_range
                        # Outlier threshold is 10x
                        if normalized_val > r_max * 10 or normalized_val < r_min / 10:
                            # Typo check: maybe they added extra zeros or missing decimal?
                            suggested_val = None
                            if normalized_val > r_max * 10:
                                # Try dividing by 10 or 100
                                if r_min <= normalized_val / 10 <= r_max:
                                    suggested_val = normalized_val / 10
                                elif r_min <= normalized_val / 100 <= r_max:
                                    suggested_val = normalized_val / 100
                            elif normalized_val < r_min / 10:
                                # Try multiplying by 10 or 100
                                if r_min <= normalized_val * 10 <= r_max:
                                    suggested_val = normalized_val * 10
                                elif r_min <= normalized_val * 100 <= r_max:
                                    suggested_val = normalized_val * 100

                            if suggested_val:
                                corrections.append({
                                    "field": f"specifications.{found_key}",
                                    "type": "outlier_correction",
                                    "severity": "suggestion",
                                    "original": val,
                                    "corrected": f"{suggested_val}{val_unit or ''}",
                                    "confidence": 0.85,
                                    "message": f"Outlier detected for '{found_key}': '{val}'. Did you mean '{suggested_val}{val_unit or ''}'?"
                                })
                            else:
                                corrections.append({
                                    "field": f"specifications.{found_key}",
                                    "type": "outlier_warning",
                                    "severity": "warning",
                                    "original": val,
                                    "corrected": None,
                                    "confidence": 0.0,
                                    "message": f"Value '{val}' for '{found_key}' is outside typical range [{r_min}, {r_max}]"
                                })

                corrected_specs[found_key] = normalized_val
            else:
                # Keep unrecognized spec as-is
                corrected_specs[key] = val

        # Cross-spec consistency checks
        # Tempered Glass thickness check
        if leaf_category == "Tempered Glass":
            thickness = corrected_specs.get("thickness")
            if thickness and isinstance(thickness, (int, float)) and thickness < 4.0:
                corrections.append({
                    "field": "specifications.thickness",
                    "type": "contradiction_warning",
                    "severity": "warning",
                    "original": f"{thickness}mm",
                    "corrected": None,
                    "confidence": 0.90,
                    "message": "Tempered glass is typically >= 4mm thick. Thinner flat glass is usually regular or float glass."
                })

        return corrected_specs, corrections

    @classmethod
    def correct_input(cls, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans and corrects a user prediction request.
        Returns a dictionary with 'corrected_request', 'corrections', and 'original_request'.
        """
        original_req = request_data.copy()
        
        brand = request_data.get("brand", "")
        category_path = request_data.get("category_path", [])
        specs = request_data.get("specifications", {})
        
        corrections = []
        
        # 1. Fuzzy match category
        norm_cat_path, cat_conf, cat_msg = cls.fuzzy_match_category(category_path)
        leaf_cat = norm_cat_path[-1] if norm_cat_path else ""
        if cat_msg and cat_conf >= 0.70:
            corrections.append({
                "field": "category_path",
                "type": "category_correction",
                "severity": "auto_corrected",
                "original": category_path,
                "corrected": norm_cat_path,
                "confidence": cat_conf,
                "message": cat_msg
            })
            
        # 2. Fuzzy match brand
        norm_brand, brand_conf, brand_msg = cls.fuzzy_match_brand(brand)
        if brand_msg and brand_conf >= 0.95:
            corrections.append({
                "field": "brand",
                "type": "brand_correction",
                "severity": "auto_corrected",
                "original": brand,
                "corrected": norm_brand,
                "confidence": brand_conf,
                "message": brand_msg
            })
        elif brand_msg and brand_conf >= 0.75:
            corrections.append({
                "field": "brand",
                "type": "brand_suggestion",
                "severity": "suggestion",
                "original": brand,
                "corrected": norm_brand,
                "confidence": brand_conf,
                "message": brand_msg
            })

        # 3. Correct specifications
        norm_specs, spec_corrections = cls.correct_specifications(specs, leaf_cat)
        corrections.extend(spec_corrections)
        
        corrected_req = {
            "title": request_data.get("title", ""),
            "title_en": request_data.get("title_en"),
            "category_path": norm_cat_path,
            "brand": norm_brand if brand_conf >= 0.95 else brand, # auto-correct only if high confidence
            "specifications": norm_specs,
            "oem_part_number": request_data.get("oem_part_number"),
            "description": request_data.get("description", "")
        }
        
        result = {
            "corrected_request": corrected_req,
            "original_request": original_req
        }
        
        # Only add corrections field if there were any issues found
        if corrections:
            result["corrections"] = corrections
            
        return result
