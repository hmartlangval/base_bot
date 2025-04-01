"""
Nelvin:Script to build and prepare the executable with correct directory structure.
"""

import os
import shutil
import subprocess
import sys

def print_header(message):
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def build_exe():
    """Build the executable using PyInstaller"""
    print_header("Building executable with PyInstaller")
    
    # Run PyInstaller with the spec file
    result = subprocess.run(["pyinstaller", "pluggable_bot.spec"], 
                          capture_output=True, 
                          text=True)
    
    print(result.stdout)
    
    if result.returncode != 0:
        print("ERROR: PyInstaller failed!")
        print(result.stderr)
        return False
    
    return True

def prepare_output():
    """Prepare the output directory with required folders"""
    print_header("Preparing output directory structure")
    
    # Source directories
    dist_dir = os.path.join(os.getcwd(), "dist")
    exe_file = os.path.join(dist_dir, "PluggableBot.exe")
    
    plugins_src = os.path.join(os.getcwd(), "plugins")
    services_src = os.path.join(os.getcwd(), "services")
    
    # Create fresh output directory
    output_dir = os.path.join(os.getcwd(), "PluggableBot")
    if os.path.exists(output_dir):
        print(f"Removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")
    
    # Create subdirectories
    plugins_out = os.path.join(output_dir, "plugins")
    services_out = os.path.join(output_dir, "services")
    
    os.makedirs(plugins_out)
    os.makedirs(services_out)
    
    # Copy executable
    if os.path.exists(exe_file):
        shutil.copy2(exe_file, output_dir)
        print(f"Copied executable to: {output_dir}")
    else:
        print(f"ERROR: Executable not found at {exe_file}")
        return False
    
    # Copy plugins directory contents
    if os.path.exists(plugins_src):
        for file in os.listdir(plugins_src):
            if file.endswith(".py"):
                src_file = os.path.join(plugins_src, file)
                dst_file = os.path.join(plugins_out, file)
                shutil.copy2(src_file, dst_file)
                print(f"Copied plugin: {file}")
    else:
        print(f"Warning: Plugins directory not found at {plugins_src}")
    
    # Copy services directory contents
    if os.path.exists(services_src):
        for file in os.listdir(services_src):
            if file.endswith(".py"):
                src_file = os.path.join(services_src, file)
                dst_file = os.path.join(services_out, file)
                shutil.copy2(src_file, dst_file)
                print(f"Copied service: {file}")
    else:
        print(f"Warning: Services directory not found at {services_src}")
    
    print_header("Output prepared successfully!")
    print(f"The PluggableBot package is ready in: {output_dir}")
    print("It contains:")
    print(f" - PluggableBot.exe")
    print(f" - plugins/ directory")
    print(f" - services/ directory")
    
    return True

if __name__ == "__main__":
    if build_exe():
        prepare_output()
    else:
        print("Build failed. Output preparation skipped.")
        sys.exit(1) 