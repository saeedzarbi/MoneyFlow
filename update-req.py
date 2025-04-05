import subprocess
import shutil
from pathlib import Path
import re

def clean_line(line):
    # Remove null characters and clean the line
    return line.replace('\x00', '').strip()

def update_packages():
    shutil.copy('requirements.txt', 'requirements.txt.backup')
    print("Updating package versions...")

    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'cp1256', 'ascii']
        requirements = None
        
        for encoding in encodings:
            try:
                with open('requirements.txt', 'r', encoding=encoding) as file:
                    # Read and clean each line
                    requirements = [clean_line(line) for line in file.readlines() if clean_line(line)]
                print(f"Successfully read file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if requirements is None:
            raise Exception("Could not read requirements.txt with any supported encoding")

        updated_requirements = []
        
        for req in requirements:
            # Skip empty lines or comments
            if not req or req.startswith('#'):
                updated_requirements.append(req + '\n')
                continue
                
            # Clean and extract package name
            package = re.split('==|>=|<=|~=', req)[0].strip()
            
            if not package:  # Skip if package name is empty
                continue
                
            try:
                # Get latest version using pip show
                result = subprocess.run(
                    ['pip', 'show', package],
                    capture_output=True,
                    text=True
                )
                
                # Extract version from pip show output
                version_match = re.search(r'Version: (.+)', result.stdout)
                if version_match:
                    latest_version = version_match.group(1)
                    updated_req = f"{package}=={latest_version}\n"
                    print(f"Updating {package}: {req} -> {updated_req.strip()}")
                else:
                    print(f"Could not find version info for {package}, keeping original")
                    updated_req = req + '\n'
                    
            except Exception as e:
                print(f"Error checking {package}: {str(e)}")
                updated_req = req + '\n'
                
            updated_requirements.append(updated_req)
        
        # Write updated requirements with UTF-8 encoding
        with open('requirements.txt', 'w', encoding='utf-8') as file:
            file.writelines(updated_requirements)
        
        print("\nUpdate complete!")
        print("Original requirements backed up to 'requirements.txt.backup'")
        
    except Exception as e:
        print(f"Error updating packages: {str(e)}")
        # Restore backup if update failed
        if Path('requirements.txt.backup').exists():
            shutil.copy('requirements.txt.backup', 'requirements.txt')
            print("Restored original requirements.txt from backup")

if __name__ == "__main__":
    update_packages()