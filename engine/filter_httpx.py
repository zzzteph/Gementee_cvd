import sys
import json
from db import Session, Scope, Resource, Endpoint
from datetime import datetime, timezone

import tldextract
def utc_now():
    return datetime.now(timezone.utc)

def get_top_level_domain(domain):
    """Extracts the top-level domain (TLD) from a given domain."""
    extracted = tldextract.extract(domain)
    return f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else extracted.domain

def import_endpoints(scope_id: int, file_path: str):
    session = Session()

    scope = session.query(Scope).filter_by(id=scope_id).first()
    if not scope:
        return

    with open(file_path, "r") as f:
        for line in f:
            data = json.loads(line.strip())
            domain = data.get("input")
            if not domain or data.get("failed", False):
                continue 
       
            endpoint_tld=get_top_level_domain(data.get("url"))
            if endpoint_tld == scope.name:
                print(f"{data.get("url")}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python httpx_parser.py <scope_id> <file_path>")
        sys.exit(1)

    import_endpoints(int(sys.argv[1]), sys.argv[2])