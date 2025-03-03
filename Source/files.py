import os
from objects import TestStep, TestCase
from pathlib import Path
import sys

# Always try to use the standard path first, but have a fallback
def get_application_path():
    standard_path = '../../../Test/Simulation/Input'
    
    # First try the standard path
    if os.path.exists(standard_path):
        return standard_path
    
    # If running from exe and standard path doesn't exist, try to find it relative to executable
    if getattr(sys, 'frozen', False):
        # We're running from PyInstaller bundle
        app_path = os.path.dirname(sys.executable)
        
        # Try some common relative positions (assuming standard project structure)
        possible_paths = [
            standard_path,  # Try original relative path first
            os.path.join(app_path, '../../../Test/Simulation/Input'),  # Same relative path from exe
            os.path.join(app_path, 'Test/Simulation/Input')  # Directly in exe folder
        ]
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found test directory at: {path}")
                return path
                
        # If nothing worked, default to standard path (which might not exist yet)
        print(f"Warning: Could not find Test directory. Using standard path: {standard_path}")
        print(f"Make sure to place the executable in the correct location.")
        return standard_path
    else:
        # Running in normal Python environment
        return standard_path

# Get the appropriate path based on context
PATH = get_application_path()
print(f"Using test case path: {PATH}")

def create_test_case(file):
    file_path = os.path.join(PATH, f"{file}.in")
    Path(file_path).touch()
    print(f"Created file: {file_path}")
    
def delete_test_case(file):
    file_path = os.path.join(PATH, f"{file}.in")
    os.remove(file_path)

def get_test_cases():
    test_cases = []
    try:
        files = os.listdir(PATH)
        for file_name in files:
            if file_name.endswith('.in'):
                file_path = os.path.join(PATH, file_name)
                with open(file_path, 'r') as file:
                    test_cases.append(get_test_case(file, file_name))
    except FileNotFoundError:
        print(f"Warning: Test directory not found at {PATH}")
        # Don't auto-create directory - this should follow standard structure
        print(f"Please ensure the directory exists at: {PATH}")
    return test_cases

def get_test_case(file, name):
    check = 0
    test_case = TestCase(name.split('.')[0], file.name.split('_')[0], [])
    current_step = TestStep(index=0, title="", requirements="", description=[], expected=[], inputs=[]) 
    file_content = file.read()
    lines = file_content.split('\n')
    
    for line in lines:
        if line.strip() == "=================================================================================":
            check += 1
            if check == 6:
                test_case.test_steps.append(current_step)
                current_step = TestStep(index=0, title="", requirements="", description=[], expected=[], inputs=[])
                check = 1
        elif line.strip() == "-------------------------------------------------------------------------------":
            check += 1
        elif line.strip() != "":
            if check == 1:
                if "Test step" in line:
                    current_step.index = int(line.split(":", 1)[0].split(" ")[2]) - 1
                    current_step.title = line.split(":", 1)[1].strip()
                else:
                    current_step.title += f"\n{line.strip()}"
            elif check == 2 and "Requirements" in line:
                current_step.requirements = line.split(":", 1)[1].strip()
            elif check == 3:
                if "Description" in line:
                    current_step.description.append(line.split(":", 1)[1].strip())
                else:
                    current_step.description.append(line.strip())
            elif check == 4:
                if "Expected" in line:
                    current_step.expected.append(line.split(":", 1)[1].strip())
                else:
                    current_step.expected.append(line.strip())
            elif check == 5:
                # Parse inputs into dictionaries with name and default
                parts = line.strip().split(" ", 1)
                command_name = parts[0]
                command_default = parts[1] if len(parts) > 1 else ""
                current_step.inputs.append({"name": command_name, "default": command_default})
    
    if check != 0:
        test_case.test_steps.append(current_step)
    return test_case

