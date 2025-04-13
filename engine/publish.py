import os
from db import Session, Scope, Resource, Endpoint
import tldextract
from collections import Counter
STORAGE_ROOT = "storage"

def export():
    session = Session()
    scopes = session.query(Scope).all()

    tag_map = {}
    global_endpoints=[]
    global_resources=[]
    global_subdomains=[]
    for scope in scopes:
        tag = scope.tag or "untagged"
        tag_map.setdefault(tag, []).append(scope)

    for tag, scoped_items in tag_map.items():
        tag_dir = os.path.join(STORAGE_ROOT, tag)
        os.makedirs(tag_dir, exist_ok=True)

        tag_resources = []
        tag_endpoints = []

        for scope in scoped_items:
            scope_dir = os.path.join(tag_dir, scope.name)
            os.makedirs(scope_dir, exist_ok=True)

            res_out = []
            end_out = []

            for resource in session.query(Resource).filter_by(scope_id=scope.id).order_by(Resource.name).all():
                res_out.append(resource.name)
                tag_resources.append(resource.name)
                global_resources.append(resource.name)
                ext = tldextract.extract(resource.name)
                global_subdomains.append(ext.subdomain)


                endpoints = session.query(Endpoint).filter_by(resource_id=resource.id).order_by(Endpoint.name).all()
                for ep in endpoints:
                    end_out.append(ep.name)
                    tag_endpoints.append(ep.name)
                    global_endpoints.append(ep.name)
            res_out = sorted(set(res_out))
            end_out = sorted(set(end_out))
            if len(res_out)>0:
                with open(os.path.join(scope_dir, "subdomains.txt"), "w") as f:
                    f.write("\n".join(res_out))
            if len(end_out)>0:
                with open(os.path.join(scope_dir, "endpoints.txt"), "w") as f:
                    f.write("\n".join(end_out))

        tag_resources = sorted(set(tag_resources))
        tag_endpoints = sorted(set(tag_endpoints))
        if len(tag_resources)>0:
            with open(os.path.join(tag_dir, "subdomains.txt"), "w") as f:
                f.write("\n".join(sorted(set(tag_resources))))
        if len(tag_endpoints)>0:        
            with open(os.path.join(tag_dir, "endpoints.txt"), "w") as f:
                f.write("\n".join(sorted(set(tag_endpoints))))
    global_resources = sorted(set(global_resources))
    global_endpoints = sorted(set(global_endpoints))
    if len(global_endpoints)>0:
        with open(os.path.join(STORAGE_ROOT, "endpoints.txt"), "w") as f:
            f.write("\n".join(sorted(set(global_endpoints))))
    if len(global_resources)>0:
        with open(os.path.join(STORAGE_ROOT, "subdomains.txt"), "w") as f:
            f.write("\n".join(sorted(set(global_resources))))
    if len(global_subdomains)>0:
        global_subdomains = Counter(global_subdomains)
        global_subdomains = [sub for sub, _ in global_subdomains.most_common()]
        with open(os.path.join(STORAGE_ROOT, "wordlist.txt"), "w") as f:
            f.write("\n".join(global_subdomains))





    print("Export completed.")

if __name__ == "__main__":
    export()