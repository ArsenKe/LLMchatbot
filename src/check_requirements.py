import pkg_resources
import re
from packaging import version
import sys

def parse_requirement(req_string):
    """Parse requirement string to name and version"""
    # Remove URL and other options
    req_string = re.split(r'\s+(?:--|@|http)', req_string)[0]
    parts = req_string.split('==')
    name = parts[0].lower().strip()
    ver = parts[1] if len(parts) > 1 else None
    return name, ver

def check_requirements():
    print("\n=== Checking Requirements ===\n")
    
    # Read requirements.txt
    with open('requirements.txt', 'r') as f:
        requirements = [line.strip() for line in f if line.strip() 
                       and not line.startswith('#')]

    installed = {pkg.key: pkg.version for pkg 
                in pkg_resources.working_set}
    
    print(f"{'Package':<25} {'Required':<15} {'Installed':<15} {'Status'}")
    print("-" * 65)

    for req in requirements:
        name, required_version = parse_requirement(req)
        
        if name in installed:
            installed_version = installed[name]
            
            if required_version:
                if version.parse(installed_version) == version.parse(required_version):
                    status = "✅ Match"
                else:
                    status = "⚠️ Version Mismatch"
            else:
                status = "✅ Installed"
                
            print(f"{name:<25} {required_version or 'Any':<15} {installed_version:<15} {status}")
        else:
            print(f"{name:<25} {required_version or 'Any':<15} {'Not found':<15} ❌ Missing")

if __name__ == "__main__":
    check_requirements()