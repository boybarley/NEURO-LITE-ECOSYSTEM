#!/usr/bin/env python3
import os
import tarfile
import logging
import shutil
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class ReleaseBuilder:
    def __init__(self):
        self.base_dir = os.getcwd()
        self.release_dir = os.path.join(self.base_dir, "release_artifact")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tar_name = f"neuro-lite-v1.0-{self.timestamp}.tar.gz"

    def validate_structure(self):
        required_files = [
            "install.sh",
            "config.env",
            "core/main_server.py",
            "core/emotional_state.py",
            "core/context_manager.py",
            "core/rag_engine.py",
            "core/post_processor.py",
            "modules/01_os_tuning.sh",
            "modules/02_install_deps.sh",
            "modules/03_download_model.sh",
            "modules/04_setup_service.sh"
        ]
        
        for f in required_files:
            if not os.path.exists(f):
                logging.error(f"Missing required file: {f}")
                return False
        return True

    def build(self):
        if not self.validate_structure():
            logging.error("Validation failed. Aborting build.")
            return

        logging.info("Building release bundle...")
        
        # Create temp dir
        if os.path.exists(self.release_dir):
            shutil.rmtree(self.release_dir)
        
        # We don't copy model to save space/time, user downloads it.
        # We copy scripts and core code.
        
        # Create Tarball directly
        with tarfile.open(self.tar_name, "w:gz") as tar:
            # Add files maintaining structure
            for root, dirs, files in os.walk(self.base_dir):
                # Exclude venv, __pycache__, git, model files
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'models', 'data', 'release_artifact']]
                
                for file in files:
                    if file.endswith('.pyc') or file.endswith('.gguf'):
                        continue
                    
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, self.base_dir)
                    tar.add(filepath, arcname=arcname)

        logging.info(f"Release bundle created: {self.tar_name}")

if __name__ == "__main__":
    builder = ReleaseBuilder()
    builder.build()
