# Simulator Generator Executable

This repository contains the Simulator Generator application executable.

## Directory Structure

The application expects a specific directory structure:

```
Project Root/
├── SimulatorApp.exe
├── ...
└── Test/
    └── Simulation/
        └── Input/
            ├── test1.in
            ├── test2.in
            └── ...
```

## For Using 

1. Run the `build_with_py311.bat` file
2. Wait for the process to complete
3. The executable will be created in the root folder 


It is strongly recommended to maintain the standard directory structure.

## Troubleshooting

If you encounter any file not found errors:
1. Verify the executable is placed in the correct location
2. Check that the Test/Simulation/Input directory exists with proper permissions
3. Ensure test files have .in extension 
