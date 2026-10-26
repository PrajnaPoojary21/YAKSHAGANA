import ast
import os

def get_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports

print(f"{'FILE':<25} {'LIBRARIES USED'}")
print("-" * 70)
for filename in sorted(os.listdir(".")):
    if filename.endswith(".py"):
        try:
            imports = get_imports(filename)
            print(f"{filename:<25} {', '.join(sorted(imports))}")
        except Exception as e:
            print(f"{filename:<25} (error reading: {e})")