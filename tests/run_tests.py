import importlib.util
import sys
from pathlib import Path

test_path = Path(__file__).parent / "test_api.py"
spec = importlib.util.spec_from_file_location("test_api", str(test_path))
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

tests = [
    getattr(mod, name)
    for name in dir(mod)
    if name.startswith('test_') and callable(getattr(mod, name))
]

failed = []
for t in tests:
    try:
        t()
        print(f'OK: {t.__name__}')
    except AssertionError as e:
        print(f'FAIL: {t.__name__} -> {e}')
        failed.append(t.__name__)
    except Exception as e:
        print(f'ERROR: {t.__name__} -> {type(e).__name__}: {e}')
        failed.append(t.__name__)

if failed:
    print('\nSome tests failed:', failed)
    raise SystemExit(1)
else:
    print('\nAll tests passed')
