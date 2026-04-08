#!/usr/bin/env python3
"""
Fix XGBoost installation in virtual environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Fix XGBoost installation"""
    print("🔧 Fixing XGBoost Installation")
    print("=" * 40)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    venv_pip = project_root / ".venv" / "Scripts" / "pip.exe"
    
    if not venv_pip.exists():
        print("❌ Virtual environment not found")
        return 1
    
    steps = [
        (f"{venv_pip} uninstall -y xgboost", "Uninstall existing XGBoost"),
        (f"{venv_pip} install xgboost==2.0.3", "Install XGBoost 2.0.3"),
        (f"{venv_pip} install \"numpy<2.0\"", "Fix numpy version"),
    ]
    
    success_count = 0
    for command, description in steps:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"⚠️  Step failed: {description}")
            break
    
    print(f"\n📊 Summary:")
    print(f"   Steps completed: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        print("🎉 XGBoost installation fixed!")
        
        # Test installation
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
        test_cmd = f'{venv_python} -c "import xgboost; print(\'XGBoost version:\', xgboost.__version__)"'
        
        if run_command(test_cmd, "Test XGBoost installation"):
            print("✅ XGBoost is working correctly!")
            return 0
        else:
            print("❌ XGBoost test failed")
            return 1
    else:
        print("❌ Installation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
