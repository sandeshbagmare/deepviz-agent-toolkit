import os
import sys
from pathlib import Path
source = Path(os.environ["R51_SOURCE"])
deps = Path(os.environ["R51_SITE_PACKAGES"])
sys.path[:0] = [str(deps), str(source / "python/deepviz/src"), str(source / "tests")]
import pytest
raise SystemExit(pytest.main(["-q", "-p", "no:cacheprovider", str(source / "tests/test_native_mapping.py")]))