import os
import ipaddress
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from db import Scope, Base
import shutil
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///storage/database.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

SCOPE_FOLDER = "scope"
PROJECTS_FOLDER="storage/projects"


def utc_now():
    return datetime.now(timezone.utc)

def determine_type(entry):
    """Determines if an entry is an IP range or a domain."""
    try:
        ipaddress.ip_network(entry, strict=False)
        return "ip_range"
    except ValueError:
        return "domains"

def remove_scope_data():
    scopes = session.query(Scope).order_by(Scope.updated_at.asc()).all()
    
    for scope in scopes:
        found=False
        for file_name in os.listdir(SCOPE_FOLDER):
            if file_name.endswith(".txt"):
                tag = os.path.splitext(file_name)[0]
                file_path = os.path.join(SCOPE_FOLDER, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        entry = line.strip()
                        print(entry)
                        if scope.tag==tag and scope.name==entry:
                            found=True
                            print(f"Found {scope.name}")
        print(f"{found} - {scope.name}")                    
        if not found:
            print(f"Removing {scope.name}")
            path = os.path.join(PROJECTS_FOLDER, scope.tag,scope.name)
            print(f"Removing {path}")
            if os.path.isdir(path):
                shutil.rmtree(path)
            session.delete(scope)
            session.commit()

    for tag_entry in os.listdir(PROJECTS_FOLDER):
        tag_path=os.path.join(PROJECTS_FOLDER,tag_entry)
        if os.path.isdir(tag_path) and not tag_path.startswith("."):
            for scope_entry in os.listdir(tag_path):
                scope_entry_path=os.path.join(tag_path,scope_entry)
                if os.path.isdir(scope_entry_path) and not scope_entry_path.startswith("."):
                    exists = session.query(Scope).filter_by(name=scope_entry,tag=tag_entry).first()
                    if not exists:
                        print(f"Removing folder {scope_entry_path}")
                        shutil.rmtree(scope_entry_path)

                        


def process_scope_files():
    """Scans the scope folder, parses .txt files, and adds new scope entries."""
    if not os.path.exists(SCOPE_FOLDER):
        print(f"Folder '{SCOPE_FOLDER}' not found.")
        return

    for file_name in os.listdir(SCOPE_FOLDER):
        if file_name.endswith(".txt"):
            tag = os.path.splitext(file_name)[0]
            file_path = os.path.join(SCOPE_FOLDER, file_name)
            
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    entry = line.strip()
                    if entry and not entry.startswith(".") and len(entry)>=3:
                        add_scope_entry(entry, tag)

def add_scope_entry(name, tag):
    """Adds a new scope entry if it does not exist."""
    entry_type = determine_type(name)
    exists = session.query(Scope).filter_by(name=name).first()
    
    if not exists:
        new_scope = Scope(
            name=name,
            type=entry_type,
            tag=tag,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        session.add(new_scope)
        os.makedirs(PROJECTS_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(PROJECTS_FOLDER, new_scope.tag), exist_ok=True)
        os.makedirs(os.path.join(PROJECTS_FOLDER, new_scope.tag,new_scope.name), exist_ok=True)
        gitkeep_path = os.path.join(os.path.join(PROJECTS_FOLDER, new_scope.tag,new_scope.name), ".gitkeep")
        open(gitkeep_path, "w").close()
        print(f"Added: {name} ({entry_type}) with tag '{tag}'")


def remove_unwanted_tags():
    for path in os.listdir(PROJECTS_FOLDER):
        if os.path.isdir(path) and not path.startswith("."):
            exists = session.query(Scope).filter_by(tag=path).first()
            if not exists:
                print(f"Remove tag folder {path}")
                shutil.rmtree(path)

def main():
    remove_scope_data()
    process_scope_files()
    remove_unwanted_tags()
    session.commit()
    session.close()
    print("Scope update complete.")

if __name__ == "__main__":
    main()
