#!/usr/bin/env python3
"""
Demo script showing what happens when you clone the project fresh from GitHub.
This simulates the experience of someone who just cloned your repo.
"""

import os
import sys
from pathlib import Path

def check_project_state():
    """Check what's available in the project."""
    print("🔍 Checking Project State (Fresh Clone Simulation)")
    print("=" * 60)
    
    # Check if models exist
    models_dir = Path("models")
    if models_dir.exists():
        model_files = list(models_dir.glob("*.pkl"))
        print(f"✅ Models directory exists with {len(model_files)} trained models")
        for model_file in model_files:
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"   - {model_file.name} ({size_mb:.1f}MB)")
    else:
        print("❌ Models directory does not exist")
        print("   This means no trained models are available")
    
    # Check if data exists
    data_file = Path("data/raw/Online Retail.csv")
    if data_file.exists():
        size_mb = data_file.stat().st_size / (1024 * 1024)
        print(f"✅ Dataset exists: {data_file.name} ({size_mb:.1f}MB)")
    else:
        print("❌ Dataset not found")
    
    # Check source code
    src_dir = Path("src")
    if src_dir.exists():
        print("✅ Source code exists")
    else:
        print("❌ Source code not found")
    
    return models_dir.exists()

def simulate_fresh_clone():
    """Simulate what a fresh clone would look like."""
    print("\n🔄 Simulating Fresh Clone from GitHub")
    print("=" * 60)
    
    # Temporarily rename models directory to simulate fresh clone
    models_dir = Path("models")
    temp_models_dir = Path("models_backup")
    
    if models_dir.exists():
        print("📁 Temporarily moving models directory...")
        models_dir.rename(temp_models_dir)
        
        print("✅ Fresh clone simulation active")
        print("   (models/ directory is now hidden)")
        
        return temp_models_dir
    else:
        print("❌ No models directory to simulate")
        return None

def test_application_startup():
    """Test if the application can start without models."""
    print("\n🚀 Testing Application Startup")
    print("=" * 60)
    
    # Check if API can start
    try:
        # Import the API module
        sys.path.append("src")
        from api.main import app
        print("✅ API module imports successfully")
        
        # Check if model loading works
        from api.main import load_model
        print("✅ Model loading function exists")
        
        # Try to load model (should fail gracefully)
        try:
            load_model()
            print("⚠️  Model loading attempted (may use dummy model)")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
        
    except ImportError as e:
        print(f"❌ API module import failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def restore_models(backup_dir):
    """Restore the models directory."""
    if backup_dir and backup_dir.exists():
        print("\n🔄 Restoring models directory...")
        current_models = Path("models")
        if current_models.exists():
            current_models.rmdir()  # Remove empty directory
        backup_dir.rename("models")
        print("✅ Models directory restored")

def main():
    """Main demonstration function."""
    print("🎯 Fresh Clone Simulation Demo")
    print("This shows what happens when someone clones your project from GitHub")
    print("=" * 80)
    
    # Check current state
    has_models = check_project_state()
    
    if has_models:
        # Simulate fresh clone
        backup_dir = simulate_fresh_clone()
        
        # Test application startup
        test_application_startup()
        
        # Restore models
        restore_models(backup_dir)
        
        print("\n" + "=" * 80)
        print("📚 Key Takeaways:")
        print("1. ✅ Fresh clone will have source code and data")
        print("2. ❌ Fresh clone will NOT have trained models")
        print("3. ⚠️  Application will need to train models first")
        print("4. 🚀 After training once, no more training needed!")
        
        print("\n🎯 Recommendations:")
        print("Option A: Train once after cloning")
        print("   git clone <repo> && python run_pipeline.py")
        print("")
        print("Option B: Include models in repo")
        print("   git add models/ && git commit -m 'Add trained models'")
        print("")
        print("Option C: Provide pre-trained models separately")
        print("   Download models.zip and extract to project root")
        
    else:
        print("\n❌ No models found - this is already a fresh clone!")
        print("Run: python run_pipeline.py to train models")

if __name__ == "__main__":
    main()
