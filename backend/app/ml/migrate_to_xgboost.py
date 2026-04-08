#!/usr/bin/env python3
"""
Migration script: RandomForest → XGBoost
This script handles the complete migration process
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed")
        print(f"   Error: {e.stderr}")
        return False

def backup_current_model():
    """Backup existing RandomForest model"""
    model_path = Path(__file__).parent / "wait_time_model.pkl"
    backup_path = Path(__file__).parent / "wait_time_model_rf_backup.pkl"
    
    if model_path.exists():
        import shutil
        shutil.copy2(model_path, backup_path)
        print(f"Existing model backed up to {backup_path}")
        return True
    else:
        print("No existing model found - fresh installation")
        return True

def install_xgboost():
    """Install XGBoost dependency"""
    backend_dir = Path(__file__).parent.parent.parent
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("requirements.txt not found")
        return False
    
    return run_command(
        f"cd {backend_dir} && pip install xgboost==2.0.3",
        "Installing XGBoost"
    )

def validate_migration():
    """Run model validation to ensure migration success"""
    validate_script = Path(__file__).parent / "validate_models.py"
    
    if not validate_script.exists():
        print("Validation script not found")
        return False
    
    return run_command(
        f"cd {Path(__file__).parent} && python validate_models.py",
        "Running model validation"
    )

def main():
    """Main migration process"""
    print("XGBoost Migration: RandomForest → XGBoost")
    print("=" * 50)
    
    steps = [
        ("Backup current model", backup_current_model),
        ("Install XGBoost", install_xgboost),
        ("Validate migration", validate_migration),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\nStep: {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"Step failed: {step_name}")
            break
    
    print(f"\nMigration Summary:")
    print(f"   Steps completed: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        print("Migration completed successfully!")
        print("\nNext Steps:")
        print("1. Retrain your model with: python -m app.ml.train")
        print("2. Test the new model: python -m app.ml.validate_models.py test")
        print("3. Update your training data if needed")
        print("4. Monitor performance in production")
    else:
        print("Migration failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
