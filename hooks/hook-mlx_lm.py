# PyInstaller hook for mlx_lm
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = collect_all('mlx_lm')
hiddenimports += collect_submodules('mlx_lm')
