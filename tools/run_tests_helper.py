import os
import sys
import importlib.util
import unittest

# Ensure project root is in sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Configure Django settings and setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
import django
try:
    django.setup()
except Exception as e:
    print('Failed to setup Django:', e)
    sys.exit(2)

# Load the standalone test script as a module
TEST_FILE = os.path.join(ROOT, 'test_delete_and_preview.py')
if not os.path.exists(TEST_FILE):
    print('Test file not found:', TEST_FILE)
    sys.exit(2)

spec = importlib.util.spec_from_file_location('test_delete_and_preview_module', TEST_FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Get the TestCase class
if not hasattr(mod, 'DeleteAndPreviewTests'):
    print('No DeleteAndPreviewTests found in test file')
    sys.exit(2)

TestCaseClass = getattr(mod, 'DeleteAndPreviewTests')

# Run the tests
suite = unittest.TestLoader().loadTestsFromTestCase(TestCaseClass)
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

if result.wasSuccessful():
    print('\nALL TESTS PASSED')
    sys.exit(0)
else:
    print('\nSOME TESTS FAILED')
    sys.exit(1)
