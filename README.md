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

## For Developers (Building)

1. Run the `build_exe.bat` file
2. Wait for the process to complete
3. The executable will be created in the `dist` folder as `SimulatorApp.exe`

## For Users (Running)

1. Place the `SimulatorApp.exe` in the correct location in your directory structure
2. Ensure the Test/Simulation/Input directory exists with your test files
3. Run the executable

## Path Resolution

The application will look for test files in this order:
1. Standard path: `../../../Test/Simulation/Input`
2. The same relative path from the executable location
3. A `Test/Simulation/Input` directory in the same folder as the executable

It is strongly recommended to maintain the standard directory structure.

## Troubleshooting

If you encounter any file not found errors:
1. Verify the executable is placed in the correct location
2. Check that the Test/Simulation/Input directory exists with proper permissions
3. Ensure test files have .in extension 