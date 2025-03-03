class Argument:
    def __init__(self, name, description, arg_type, default):
        self.name = name
        self.description = description
        self.type = arg_type
        self.default = default

class Command:
    def __init__(self, input, description, arguments):
        self.input = input
        self.description = description
        self.arguments = arguments

class TestStep:
    def __init__(self, index, title, requirements, description, expected, inputs):
        self.index = index
        self.title = title
        self.requirements = requirements
        self.description = description
        self.expected = expected
        self.inputs = inputs
        
        
    def print(self):
        newline = "\n"
        print(
                "=================================================================================\n"
                f"Test step {self.index} : {self.title}\n"
                "-------------------------------------------------------------------------------\n"
                f"Requirements: {self.requirements}\n"
                "-------------------------------------------------------------------------------\n"
                f'Description : {newline.join(f"{value}" for value in self.expected)}\n'
                "-------------------------------------------------------------------------------\n"
                f'Expected    : {newline.join(f"{value}" for value in self.expected)}\n'
                "=================================================================================\n"
                f'{newline.join(f"{value}" for value in self.inputs)}\n'
        )

class TestCase:
    def __init__(self, name, handler, test_steps):
        self.name = name
        self.handler = handler
        self.test_steps = test_steps
        
    def print(self):
        for step in self.test_steps:
            step.print()
            print("\n")


class cmd: 
    def __init__(self, name, description, arguments, default):
        self.name = name
        self.description = description
        self.arguments = arguments  # List of Argument objects
        self.default = default

class Filter:
    def __init__(self, name, description, arguments):
        self.name = name
        self.description = description
        self.arguments = arguments
        self.category = self.get_category()

    def get_category(self):
        # Implement a simple categorization system based on the command name
        if self.name.startswith("root_"):
            return "Root"
        elif self.name.startswith("sub_"):
            return "Sub"
        else:
            return "Other"

    