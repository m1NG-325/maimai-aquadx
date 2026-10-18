"""Standalone alternate visual edition; shares compatible AquaSync data."""
if __name__=='__main__':
    from app.desktop_bootstrap import run
    raise SystemExit(run(studio=True))
