from pydantic import BaseModel
import re

class MainCriteria(BaseModel):
    word_count: int
    presence_of_keys: int
    absence_of_PII: int

def deserialize_model(model_string: str, model_class):
    # Extract the content inside parentheses
    match = re.search(r"\((.*)\)", model_string)
    if not match:
        raise ValueError(f"Invalid model string: {model_string}")
    
    # Convert the key-value pairs into a dictionary-like format
    content = match.group(1)
    content_dict = {}
    for pair in content.split(","):
        key, value = pair.split("=")
        content_dict[key.strip()] = eval(value.strip())  # Convert value to correct type
    
    # Use the model class to create an instance
    return model_class(**content_dict)