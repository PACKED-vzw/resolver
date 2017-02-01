##
# JSONSchema schema's
from resolver.model.data import data_formats


entity_schema = {
    "properties": {
        "domain": {"type": "string"},
        "type": {"type": "string",
                 "enum": ["work", "concept", "event", "agent"]},
        "id": {"type": "string"},
        "prim_key": {"type": "integer"},
        "title": {"type": "string"},
        "documents": {"type": "array",
                      "items": {"type": "integer"}},
        "persistentURIs": {"type": "array",
                           "items": {"type": "string"}}
    },
    "required": ["type", "id"]
}


document_schema = {
    "oneOf": [
        {"$ref": "#/definitions/data"},
        {"$ref": "#/definitions/representation"}
    ],
    "definitions": {
        "document": {
            "properties": {
                "id": {"type": "integer"},
                "entity": {"type": "integer"},
                "enabled": {"type": "boolean"},
                "notes": {"type": "string"},
                "url": {"type": "string"},
                "type": {"type": "string",
                         "enum": ["data", "representation"]},
                "resolves": {"type": "boolean"}
            },
            "required": ["entity", "enabled", "type"]
        },
        "data": {
            "allOf": [
                {"$ref": "#/definitions/document"},
                {"properties":
                    {"format": {"type": "string", "enum": data_formats},
                     "type": {"type": "string", "enum": ["data"]}},
                 "required": ["format"]}]
        },
        "representation": {
            "allOf": [
                {"$ref": "#/definitions/document"},
                {"properties":
                     {"order": {"type": "integer"},
                      "reference": {"type": "boolean"},
                      "label": {"type": "string"},
                      "type": {"type": "string", "enum": ["representation"]}},
                 "required": ["reference"]}]
        }
    }
}
