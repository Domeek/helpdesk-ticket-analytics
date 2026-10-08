import sys
from pathlib import Path

# Make `import load_data` work: the code lives in src/, which is not a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
