import json
import time
from typing import Any, Dict, List
from deepdiff import DeepDiff
import jsonschema
from jsonschema import validate

def validate_json_schema(instance: Dict, schema: Dict) -> bool:
    """
    Валидация JSON по схеме.
    """
    try:
        validate(instance=instance, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        raise AssertionError(f"JSON schema validation failed: {e.message}")

def compare_json_objects(
    expected: Dict,
    actual: Dict,
    exclude_paths: List[str] = None
) -> Dict:
    """
    Сравнение двух JSON объектов с игнорированием определенных путей.
    """
    diff = DeepDiff(
        expected,
        actual,
        exclude_paths=exclude_paths,
        ignore_order=True,
        report_repetition=True
    )
    return diff

def wait_for_condition(
    condition_func,
    timeout: int = 30,
    interval: float = 1.0,
    *args,
    **kwargs
) -> bool:
    """
    Ожидание выполнения условия.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func(*args, **kwargs):
            return True
        time.sleep(interval)
    return False

def extract_value_from_json(json_obj: Dict, path: str) -> Any:
    """
    Извлечение значения из JSON по пути (например, 'items[0].name').
    """
    parts = path.split('.')
    current = json_obj
    
    for part in parts:
        if '[' in part and ']' in part:
            # Обработка массивов (например, items[0])
            name, index = part.replace(']', '').split('[')
            current = current[name][int(index)]
        else:
            current = current[part]
    
    return current