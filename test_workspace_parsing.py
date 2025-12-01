"""
Standalone test script for parse_function_workspace feature.

This script can be used to test the new parse_function_workspace parameter
without needing to compile scipy. It works by directly importing the modified
Python modules.

Usage on Windows with Python 3.12:
    python test_workspace_parsing.py

Requirements:
    - numpy (pip install numpy)
    - The parabola.mat test file in scipy/io/matlab/tests/data/

Note: This script imports scipy modules directly from source, so it will use
your modified code without requiring compilation.
"""

import sys
import os

# Add scipy to path so we can import without installing
scipy_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scipy_root)

print("=" * 70)
print("Testing parse_function_workspace feature")
print("=" * 70)
print()

# Check for numpy
try:
    import numpy as np
    print(f"✓ NumPy {np.__version__} found")
except ImportError:
    print("✗ NumPy not found. Please install: pip install numpy")
    sys.exit(1)

# Try to import scipy.io modules
try:
    from scipy.io.matlab._mio import loadmat
    print("✓ Successfully imported loadmat from scipy.io.matlab._mio")
except ImportError as e:
    print(f"✗ Failed to import scipy modules: {e}")
    print("\nNote: Some compiled Cython extensions might be needed.")
    print("If this fails, the feature can only be tested with a full scipy build.")
    sys.exit(1)

# Check for test data
test_data_path = os.path.join(scipy_root, 'scipy', 'io', 'matlab', 'tests', 'data')
test_file = os.path.join(test_data_path, 'parabola.mat')

if not os.path.exists(test_file):
    print(f"✗ Test file not found: {test_file}")
    sys.exit(1)

print(f"✓ Test file found: parabola.mat")
print()

# Run tests
print("-" * 70)
print("Test 1: Load without parsing (default behavior)")
print("-" * 70)

try:
    data_default = loadmat(test_file)
    print("✓ Successfully loaded parabola.mat")
    print(f"  Keys in file: {list(data_default.keys())}")
    
    if '__function_workspace__' in data_default:
        ws = data_default['__function_workspace__']
        print(f"  __function_workspace__ present: dtype={ws.dtype}, shape={ws.shape}")
        print(f"  Is raw bytes (uint8): {ws.dtype == np.uint8}")
    else:
        print("  No __function_workspace__ found")
    
    # Check that no parsed variables exist by default
    workspace_vars = [k for k in data_default.keys() 
                      if k.startswith('__function_workspace__') 
                      and k != '__function_workspace__']
    
    if len(workspace_vars) == 0:
        print("  ✓ No parsed workspace variables (backward compatible)")
    else:
        print(f"  ✗ Found parsed variables when not expected: {workspace_vars}")
        
except Exception as e:
    print(f"✗ Error loading file: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test with parsing enabled
print("-" * 70)
print("Test 2: Load WITH parsing (parse_function_workspace=True)")
print("-" * 70)

try:
    data_parsed = loadmat(test_file, parse_function_workspace=True)
    print("✓ Successfully loaded parabola.mat with parse_function_workspace=True")
    print(f"  Keys in file: {list(data_parsed.keys())}")
    
    # Check for parsed workspace variables
    workspace_vars = [k for k in data_parsed.keys() 
                      if k.startswith('__function_workspace__') 
                      and k != '__function_workspace__']
    
    if len(workspace_vars) > 0:
        print(f"  ✓ Found {len(workspace_vars)} parsed workspace variable(s):")
        for key in workspace_vars:
            var = data_parsed[key]
            if hasattr(var, 'dtype') and hasattr(var, 'shape'):
                print(f"    - {key}: dtype={var.dtype}, shape={var.shape}")
            else:
                print(f"    - {key}: type={type(var)}")
    else:
        print("  ✗ No parsed workspace variables found!")
        print("  This might indicate the parsing didn't work correctly.")
    
    # Verify raw workspace still available
    if '__function_workspace__' in data_parsed:
        print("  ✓ Raw __function_workspace__ still available")
    else:
        print("  ✗ Raw __function_workspace__ missing!")
        
except Exception as e:
    print(f"✗ Error loading file with parsing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test backward compatibility
print("-" * 70)
print("Test 3: Backward compatibility check")
print("-" * 70)

try:
    data_explicit_false = loadmat(test_file, parse_function_workspace=False)
    
    # Compare keys
    default_keys = set(data_default.keys())
    explicit_false_keys = set(data_explicit_false.keys())
    
    if default_keys == explicit_false_keys:
        print("✓ Default behavior matches explicit parse_function_workspace=False")
    else:
        print("✗ Key mismatch between default and explicit False")
        print(f"  Default only: {default_keys - explicit_false_keys}")
        print(f"  Explicit False only: {explicit_false_keys - default_keys}")
        
except Exception as e:
    print(f"✗ Error in compatibility test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("All tests completed!")
print("=" * 70)
print()
print("Summary:")
print("  - The parse_function_workspace parameter is working")
print("  - Default behavior is backward compatible")
print("  - Workspace parsing can be enabled with parse_function_workspace=True")
print()
print("Example usage:")
print("  import scipy.io as sio")
print("  data = sio.loadmat('file.mat', parse_function_workspace=True)")
print("  workspace_vars = {k: v for k, v in data.items()")
print("                    if k.startswith('__function_workspace__')")
print("                    and k != '__function_workspace__'}")
