import subprocess
import sys
import os

def main():
    try:
        # Install python-telegram-bot
        print("Installing python-telegram-bot library...")
        pip_install_command = [sys.executable, "-m", "pip", "install", "python-telegram-bot"]
        subprocess.run(pip_install_command, check=True)
        print("python-telegram-bot installed successfully.")

        # Compile the C file
        print("Compiling shan.c with gcc...")
        compile_command = ["gcc", "-o", "shan", "shan.c", "-lpthread"]
        subprocess.run(compile_command, check=True)
        print("Compilation successful: shan executable created.")
        
        # Run the Python script
        print("Running g.py...")
        run_python_command = [sys.executable, "g.py"]  # sys.executable ensures the script runs with the current Python interpreter
        subprocess.run(run_python_command, check=True)
        print("Python script g.py executed successfully.")
    
    except subprocess.CalledProcessError as e:
        print(f"Command '{' '.join(e.cmd)}' failed with return code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
