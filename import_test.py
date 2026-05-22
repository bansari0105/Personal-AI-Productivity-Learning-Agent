import importlib, traceback

try:
    importlib.import_module('backend.myapi')
    print('IMPORT OK')
except Exception:
    traceback.print_exc()
