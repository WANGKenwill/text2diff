import subprocess
import toml

def get_direct_dependencies():
    # Read pyproject.toml file
    with open('pyproject.toml', 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    # Get dependencies
    dependencies = config.get('project', {}).get('dependencies', [])
    
    # Extract package names (remove version specifiers and extras)
    packages = []
    for dep in dependencies:
        # Remove extras (e.g., "ell-ai[all]" -> "ell-ai")
        if '[' in dep:
            dep = dep.split('[')[0]
        
        # Remove version specifiers (e.g., "gradio>=3.0.0" -> "gradio")
        package_name = dep.split('>')[0].split('<')[0].split('=')[0].strip()
        packages.append(package_name)
    
    return packages

def update_licenses():
  # Define the output file name
    LICENSES_FILE = 'LICENSES_THIRD_PARTY'

    # Get direct dependencies
    packages = get_direct_dependencies()
    print(f"Packages: {packages}")
    
    # If no dependencies, return early
    if not packages:
        print("No direct dependencies found in pyproject.toml")
        return

    # Update third-party licenses file
    with open(LICENSES_FILE, 'w', encoding='utf-8') as f:
        # Build pip-licenses command
        command = ['pip-licenses', '--format=markdown', '--with-urls']
        command.extend(['--packages'] + packages)
        
        # Run pip-licenses
        subprocess.run(command, stdout=f)

    # Add file header
    with open(LICENSES_FILE, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write("# Third-Party Licenses\n\nThis project uses the following third-party libraries:\n" + content)

    print("Third-party licenses have been updated successfully.")


if __name__ == "__main__":
    update_licenses()