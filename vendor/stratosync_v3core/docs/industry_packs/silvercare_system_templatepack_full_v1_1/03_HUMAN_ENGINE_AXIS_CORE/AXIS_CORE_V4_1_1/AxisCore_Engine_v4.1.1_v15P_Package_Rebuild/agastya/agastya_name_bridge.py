#!/usr/bin/env python3
"""
agastya_name_bridge.py
- Runtime import hook that maps legacy 'agastia.*' imports to 'agastya.*'.
- Drop this file into your project root (agastya_app/) and add:
    import agastya_name_bridge
  at the very top of your main entry-point (e.g., main.py).
"""
import sys, importlib, importlib.util, importlib.abc

class _AgastyaBridge(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith("agastia"):
            fixed = fullname.replace("agastia", "agastya", 1)
            return importlib.util.find_spec(fixed)
        return None
    def create_module(self, spec):  # pragma: no cover
        return None
    def exec_module(self, module):  # pragma: no cover
        return None

# Install once
if not any(isinstance(h, _AgastyaBridge) for h in sys.meta_path):
    sys.meta_path.insert(0, _AgastyaBridge())
    print("[AgastyaBridge] legacy 'agastia' imports will be mapped to 'agastya'.")
