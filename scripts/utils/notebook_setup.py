# ---
# description: |
#   Core notebook setup utility. Configures matplotlib with publication-quality
#   RC params and the Okabe-Ito 8-color colorblind-safe palette, enables
#   autoreload, and returns common library handles.
# entry_point: from scripts.utils import setup_notebook; PROJECT_ROOT, np, pd, plt, Path = setup_notebook()
# dependencies:
#   - matplotlib
#   - numpy
#   - pandas
#   - IPython (optional, for autoreload)
# input: |
#   No CLI arguments. Called from Jupyter notebooks. Uses VS Code's
#   __vsc_ipynb_file__ kernel variable (or IPython.starting_dir as fallback)
#   to locate the calling notebook and resolve the correct project root.
# process: |
#   Resolves project root via __vsc_ipynb_file__ (handles multiple editable
#   installs), patches scripts.__path__ and sys.path so subsequent imports of
#   scripts.data_loader etc. resolve to this project. Enables autoreload,
#   imports np/pd/plt, sets Okabe-Ito RC params.
# output: |
#   Returns (PROJECT_ROOT, np, pd, plt, Path). Side effect: matplotlib global
#   RC params are updated; scripts.* module cache is corrected for this project.
# last_updated: 2026-04-12
# ---

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Okabe & Ito (2008) colorblind-safe palette — 8 colors
# Source: Okabe, M. & Ito, K. (2008). Color Universal Design (CUD).
#         https://jfly.uni-koeln.de/color/
# ---------------------------------------------------------------------------
OKABE_ITO = {
    'orange':         '#E69F00',
    'sky_blue':       '#56B4E9',
    'bluish_green':   '#009E73',
    'yellow':         '#F0E442',
    'blue':           '#0072B2',
    'vermillion':     '#D55E00',
    'reddish_purple': '#CC79A7',
    'black':          '#000000',
}

# Ordered list for matplotlib prop_cycle (yellow last — low contrast on white)
OKABE_ITO_CYCLE = [
    '#E69F00',  # orange
    '#56B4E9',  # sky blue
    '#009E73',  # bluish green
    '#0072B2',  # blue
    '#D55E00',  # vermillion
    '#CC79A7',  # reddish purple
    '#F0E442',  # yellow
    '#000000',  # black
]


def setup_notebook():
    """
    Set up notebook environment.

    1. Finds the correct project root (handles multiple projects with 'scripts' packages)
    2. Fixes sys.path and patches scripts.__path__ so subsequent imports resolve correctly
    3. Enables IPython autoreload
    4. Imports and returns common scientific libraries
    5. Configures matplotlib for publication-quality plots

    Returns:
        tuple: (PROJECT_ROOT, np, pd, plt, Path)

    Usage:
        from scripts.utils import setup_notebook
        PROJECT_ROOT, np, pd, plt, Path = setup_notebook()
        # Then import project-specific modules:
        from scripts.data_loader import AHE_hysteresis
    """
    PROJECT_ROOT = _find_project_root()
    _fix_scripts_path(PROJECT_ROOT)

    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic('load_ext', 'autoreload')
            ipython.run_line_magic('autoreload', '2')
            print("[OK] Autoreload enabled")
    except Exception as e:
        print(f"[WARNING] Could not enable autoreload: {e}")

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    configure_plot_style()
    print(f"[OK] Project root: {PROJECT_ROOT}")
    print("[OK] Matplotlib configured (Okabe-Ito palette, publication style)")
    print("=" * 50)
    print("Setup complete!")
    print("=" * 50)

    return PROJECT_ROOT, np, pd, plt, Path


def _find_project_root() -> Path:
    """
    Find the correct project root, prioritising the calling notebook's location.

    When multiple projects with a 'scripts' package are pip-installed in editable
    mode, scripts.__file__ may resolve to the wrong project. This function uses
    VS Code's __vsc_ipynb_file__ kernel variable (set automatically by the VS Code
    Jupyter extension) to identify which notebook is running, then walks up to find
    the project root (identified by pyproject.toml or CLAUDE.md).

    Strategy order:
      1. __vsc_ipynb_file__ in IPython namespace (VS Code Jupyter)
      2. IPython.starting_dir (Jupyter Lab / classic notebook)
      3. scripts.__file__ (may be wrong with multiple editable installs)
      4. Walk up from cwd
    """
    # Strategy 1: VS Code sets __vsc_ipynb_file__ in the kernel namespace
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None:
            nb_file = ip.user_ns.get('__vsc_ipynb_file__')
            if nb_file:
                nb_path = Path(nb_file)
                for candidate in [nb_path.parent, nb_path.parent.parent]:
                    if (candidate / "pyproject.toml").exists() or (candidate / "CLAUDE.md").exists():
                        return candidate
    except Exception:
        pass

    # Strategy 2: IPython starting directory (Jupyter Lab / classic)
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip is not None and hasattr(ip, 'starting_dir'):
            candidate = Path(ip.starting_dir)
            for p in [candidate, candidate.parent]:
                if (p / "pyproject.toml").exists() or (p / "CLAUDE.md").exists():
                    return p
    except Exception:
        pass

    # Strategy 3: scripts.__file__ (fallback — may be wrong with multiple installs)
    try:
        import scripts as _s
        if hasattr(_s, '__file__') and _s.__file__ is not None:
            candidate = Path(_s.__file__).parent.parent
            if (candidate / "pyproject.toml").exists():
                return candidate
    except ImportError:
        pass

    # Strategy 4: Walk up from cwd
    for p in [Path.cwd()] + list(Path.cwd().parents):
        if (p / "pyproject.toml").exists() or (p / "CLAUDE.md").exists():
            return p

    raise RuntimeError(
        "Could not find project root. "
        "Ensure pyproject.toml or CLAUDE.md exists at the project root."
    )


def _fix_scripts_path(project_root: Path) -> None:
    """
    Ensure that imports of scripts.* submodules resolve to project_root/scripts/.

    When multiple projects have a 'scripts' package installed in editable mode,
    Python may have loaded the wrong project's 'scripts' package. This function:
      1. Inserts project_root at the front of sys.path
      2. Patches scripts.__path__ to point to the correct scripts/ directory
      3. Clears stale scripts.* submodule cache entries (except scripts.utils,
         which is already loaded correctly and identical across projects)

    This means any 'from scripts.data_loader import ...' that runs AFTER
    setup_notebook() will import from the correct project.
    """
    root_str = str(project_root)

    # Put correct project root at front of sys.path
    sys.path = [p for p in sys.path if p != root_str]
    sys.path.insert(0, root_str)

    # Patch the scripts package object's __path__ to the correct directory
    if 'scripts' in sys.modules:
        correct_scripts_dir = str(project_root / "scripts")
        sys.modules['scripts'].__path__ = [correct_scripts_dir]
        sys.modules['scripts'].__file__ = str(project_root / "scripts" / "__init__.py")

    # Evict stale submodule cache so they reimport from the patched path
    # Keep scripts.utils.* — it's already loaded and is identical across projects
    for key in list(sys.modules.keys()):
        if key.startswith('scripts.') and not key.startswith('scripts.utils'):
            del sys.modules[key]


def configure_plot_style():
    """Configure matplotlib RC params for publication-quality, colorblind-safe plots."""
    import matplotlib as mpl

    mpl.rcParams.update({
        # Figure
        'figure.dpi':          150,
        'savefig.dpi':         600,
        'figure.figsize':      (10, 7),
        'figure.facecolor':    'white',
        'savefig.facecolor':   'white',
        'savefig.bbox':        'tight',
        'savefig.pad_inches':  0.1,
        'savefig.format':      'png',

        # Font — STIX Two (serif, Times-like, full LaTeX math support)
        'font.family':         'STIXGeneral',
        'mathtext.fontset':    'stix',
        'font.size':           16,
        'axes.labelsize':      22,
        'axes.titlesize':      22,
        'xtick.labelsize':     18,
        'ytick.labelsize':     18,
        'legend.fontsize':     18,
        'legend.title_fontsize': 18,

        # Axes
        'axes.linewidth':      2,
        'axes.edgecolor':      'black',
        'axes.labelcolor':     'black',
        'axes.grid':           False,

        # Ticks — all four sides, inward (physics convention)
        'xtick.major.width':   2,    'ytick.major.width':   2,
        'xtick.minor.width':   1.5,  'ytick.minor.width':   1.5,
        'xtick.major.size':    6,    'ytick.major.size':    6,
        'xtick.minor.size':    4,    'ytick.minor.size':    4,
        'xtick.direction':     'in', 'ytick.direction':     'in',
        'xtick.top':           True, 'xtick.bottom':        True,
        'ytick.left':          True, 'ytick.right':         True,

        # Lines
        'lines.linewidth':     2,
        'lines.markersize':    7,

        # Legend
        'legend.frameon':      True,
        'legend.framealpha':   0.9,
        'legend.edgecolor':    '0.8',
        'legend.fancybox':     False,

        # Okabe-Ito color cycle + viridis colormap
        'axes.prop_cycle':     mpl.cycler(color=OKABE_ITO_CYCLE),
        'image.cmap':          'viridis',
    })


__all__ = ['setup_notebook', 'configure_plot_style', 'OKABE_ITO', 'OKABE_ITO_CYCLE']
