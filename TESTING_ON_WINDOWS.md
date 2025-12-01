# Testing parse_function_workspace on Windows with Python 3.12

## Quick Start (Without Compiling SciPy)

Since compiling SciPy on Windows can be challenging, here's how to test the new `parse_function_workspace` feature without a full build:

### Prerequisites

1. **Python 3.12** (already installed)
2. **NumPy** - Install with:
   ```powershell
   pip install numpy
   ```

### Steps to Test

1. **Navigate to the scipy repository directory:**
   ```powershell
   cd path\to\scipy
   ```

2. **Run the standalone test script:**
   ```powershell
   python test_workspace_parsing.py
   ```

This script will:
- Import the modified Python modules directly (no compilation needed)
- Test the feature with the included `parabola.mat` test file
- Verify backward compatibility
- Show example output

### Expected Output

If everything works correctly, you should see:
```
======================================================================
Testing parse_function_workspace feature
======================================================================

✓ NumPy 1.XX.X found
✓ Successfully imported loadmat from scipy.io.matlab._mio
✓ Test file found: parabola.mat

----------------------------------------------------------------------
Test 1: Load without parsing (default behavior)
----------------------------------------------------------------------
✓ Successfully loaded parabola.mat
  Keys in file: ['__header__', '__version__', '__globals__', 'parabola', '__function_workspace__']
  __function_workspace__ present: dtype=uint8, shape=(XXX, XXX)
  Is raw bytes (uint8): True
  ✓ No parsed workspace variables (backward compatible)

----------------------------------------------------------------------
Test 2: Load WITH parsing (parse_function_workspace=True)
----------------------------------------------------------------------
✓ Successfully loaded parabola.mat with parse_function_workspace=True
  Keys in file: ['__header__', '__version__', '__globals__', 'parabola', '__function_workspace__', '__function_workspace__var_0', ...]
  ✓ Found X parsed workspace variable(s):
    - __function_workspace__var_0: dtype=..., shape=...
  ✓ Raw __function_workspace__ still available

----------------------------------------------------------------------
Test 3: Backward compatibility check
----------------------------------------------------------------------
✓ Default behavior matches explicit parse_function_workspace=False

======================================================================
All tests completed!
======================================================================
```

## Important Notes

### Cython Extensions

⚠️ **The standalone test might fail if the code depends on Cython extensions** (`.pyx` files that need compilation).

Looking at the implementation:
- `scipy/io/matlab/_mio.py` - Pure Python ✓
- `scipy/io/matlab/_mio5.py` - Pure Python ✓
- Uses `scipy/io/matlab/_mio5_utils.pyx` - **Cython module** ✗

The code imports `VarReader5` from `_mio5_utils`, which is a Cython extension. This means:

**The standalone test will only work if you have a SciPy installation with compiled extensions.**

### Alternative: Test with Pre-built SciPy

If the standalone test fails due to missing Cython extensions, you can:

1. **Install SciPy from conda-forge or PyPI** (pre-compiled binaries):
   ```powershell
   # Using conda (recommended for Windows)
   conda install scipy
   
   # Or using pip (may have issues on Windows)
   pip install scipy
   ```

2. **Copy your modified Python files** over the installed ones:
   ```powershell
   # Find your scipy installation
   python -c "import scipy; print(scipy.__file__)"
   # This will show something like: C:\Users\...\site-packages\scipy\__init__.py
   
   # Copy modified files to that location
   copy scipy\io\matlab\_mio.py C:\Users\...\site-packages\scipy\io\matlab\_mio.py
   copy scipy\io\matlab\_mio5.py C:\Users\...\site-packages\scipy\io\matlab\_mio5.py
   ```

3. **Run the test script:**
   ```powershell
   python test_workspace_parsing.py
   ```

## Manual Testing with Your Own .mat Files

If you have your own MATLAB files with classes or function handles, you can test directly:

```python
import scipy.io as sio

# Load your file with workspace parsing enabled
data = sio.loadmat('your_file.mat', parse_function_workspace=True)

# Check what was loaded
print("All keys:", list(data.keys()))

# Filter workspace variables
workspace_vars = {k: v for k, v in data.items() 
                  if k.startswith('__function_workspace__') 
                  and k != '__function_workspace__'}

print("Workspace variables:", list(workspace_vars.keys()))

# Examine each workspace variable
for key, value in workspace_vars.items():
    print(f"{key}: {type(value)}, shape={getattr(value, 'shape', 'N/A')}")
```

## Full Build (If You Need It)

If you absolutely need to compile SciPy from source on Windows:

1. **Install build tools:**
   ```powershell
   # Install Visual Studio Build Tools 2019 or later
   # Download from: https://visualstudio.microsoft.com/downloads/
   
   # Install required Python packages
   pip install meson-python ninja cython numpy pybind11
   ```

2. **Build SciPy:**
   ```powershell
   cd path\to\scipy
   python -m pip install --no-build-isolation -e .
   ```

3. **Run tests:**
   ```powershell
   # Run the specific tests for this feature
   python -m pytest scipy\io\matlab\tests\test_mio.py::test_parse_function_workspace -v
   python -m pytest scipy\io\matlab\tests\test_mio.py::test_parse_function_workspace_backward_compat -v
   ```

## Troubleshooting

### "No module named 'scipy._lib'"
- This means Cython extensions aren't compiled
- Use the "Alternative: Test with Pre-built SciPy" method above

### "ImportError: DLL load failed"
- Common on Windows when mixing build tools
- Try using conda instead of pip for dependencies
- Ensure Visual Studio Build Tools are properly installed

### "ModuleNotFoundError: No module named 'scipy.io.matlab._mio5_utils'"
- The Cython extension wasn't compiled
- Use pre-built SciPy as described above

## Example: Test with parabola.mat

The repository includes a test file you can use:

```python
import sys
sys.path.insert(0, r'path\to\scipy')  # Use your actual path

from scipy.io.matlab._mio import loadmat

# Test with included test file
test_file = r'scipy\io\matlab\tests\data\parabola.mat'

# Without parsing (default)
data1 = loadmat(test_file)
print("Default keys:", list(data1.keys()))

# With parsing
data2 = loadmat(test_file, parse_function_workspace=True)
print("With parsing keys:", list(data2.keys()))

# Show parsed variables
workspace_vars = [k for k in data2.keys() 
                  if k.startswith('__function_workspace__') 
                  and k != '__function_workspace__']
print("Parsed workspace variables:", workspace_vars)
```

## Questions?

If you encounter issues, please provide:
1. The exact error message
2. Your Python version: `python --version`
3. Whether you can `import scipy` successfully
4. Output of: `python -c "import scipy; print(scipy.__file__)"`
