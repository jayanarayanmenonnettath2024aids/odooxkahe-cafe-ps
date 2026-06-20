import json
import os

def generate_markdown(openapi_path, output_path):
    with open(openapi_path, 'r') as f:
        spec = json.load(f)

    md = "# Complete OpenAPI Contract\n\n"
    md += "This document provides the exhaustive API contract for the Odoo Cafe POS Backend.\n\n"
    
    # Components and schemas
    schemas = spec.get("components", {}).get("schemas", {})

    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            md += f"## {method.upper()} `{path}`\n\n"
            md += f"**Summary:** {details.get('summary', 'No summary')}\n\n"
            
            # Auth
            security = details.get("security", [])
            if security:
                auth_reqs = ", ".join([list(s.keys())[0] for s in security])
                md += f"**Authentication:** Required ({auth_reqs})\n\n"
            else:
                md += "**Authentication:** None\n\n"
                
            # Parameters (Validation Rules)
            params = details.get("parameters", [])
            if params:
                md += "**Parameters:**\n"
                for p in params:
                    req = "Required" if p.get("required") else "Optional"
                    schema = p.get("schema", {})
                    ptype = schema.get("type", "string")
                    md += f"- `{p['name']}` ({ptype}) [{req}]: {p.get('description', '')}\n"
                md += "\n"
                
            # Request Body
            req_body = details.get("requestBody", {})
            if req_body:
                content = req_body.get("content", {}).get("application/json", {})
                schema_ref = content.get("schema", {}).get("$ref", "")
                if schema_ref:
                    schema_name = schema_ref.split("/")[-1]
                    md += f"**Request Body Schema:** `{schema_name}`\n\n"
                    # Try to dump schema props
                    schema_def = schemas.get(schema_name, {})
                    props = schema_def.get("properties", {})
                    if props:
                        md += "| Field | Type | Description/Validation |\n"
                        md += "|---|---|---|\n"
                        for fname, fprop in props.items():
                            ftype = fprop.get("type", "any")
                            if "anyOf" in fprop:
                                ftype = "Union"
                            val_rules = []
                            if "maxLength" in fprop: val_rules.append(f"maxLen: {fprop['maxLength']}")
                            if "minLength" in fprop: val_rules.append(f"minLen: {fprop['minLength']}")
                            if "pattern" in fprop: val_rules.append(f"pattern: {fprop['pattern']}")
                            val_str = ", ".join(val_rules) if val_rules else "-"
                            md += f"| `{fname}` | `{ftype}` | {val_str} |\n"
                        md += "\n"

            # Responses
            responses = details.get("responses", {})
            if responses:
                md += "**Responses:**\n"
                for rcode, rdetails in responses.items():
                    md += f"- **{rcode}**: {rdetails.get('description', '')}\n"
                md += "\n"
                
            md += "---\n\n"

    with open(output_path, 'w', encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    generate_markdown("openapi.json", r"C:\Users\JAYAN\.gemini\antigravity-ide\brain\d041c51e-0973-4526-94ce-b88d3dd54224\openapi_contract.md")
