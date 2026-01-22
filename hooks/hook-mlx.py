# PyInstaller hook for mlx
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = collect_all('mlx')
hiddenimports += collect_submodules('mlx')
