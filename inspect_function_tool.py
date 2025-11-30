import sys
sys.path.insert(0, 'd:/vscode/projects/coe_intern/drug_repurposing_agents')

from agents import function_tool

@function_tool
def my_test_tool(x: int):
    return x * 2

print(f"Type: {type(my_test_tool)}")
print(f"Dir: {dir(my_test_tool)}")

# Try to find the function
if hasattr(my_test_tool, 'func'):
    print(f"Has .func: {my_test_tool.func}")
elif hasattr(my_test_tool, 'fn'):
    print(f"Has .fn: {my_test_tool.fn}")
elif hasattr(my_test_tool, 'run'):
    print(f"Has .run: {my_test_tool.run}")
elif hasattr(my_test_tool, '__call__'):
    print("Has __call__")
    try:
        print(f"Call result: {my_test_tool(5)}")
    except Exception as e:
        print(f"Call failed: {e}")
