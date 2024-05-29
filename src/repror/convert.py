import os
from pathlib import Path
import subprocess
import tempfile
import shutil
from repror import conf

def checkout_feedstock(package_name, dest_dir):
    """
    Check out the feedstock repository for the given package name.
    """
    repo_url = f"https://github.com/conda-forge/{package_name}-feedstock"
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
            recipe_dir = os.path.join(temp_dir, "recipe")
            dest_recipe_dir = os.path.join(dest_dir, "recipes", package_name)
            # os.makedirs(dest_recipe_dir, exist_ok=True)
            shutil.copytree(recipe_dir, dest_recipe_dir, dirs_exist_ok=True)
            return dest_recipe_dir
        except subprocess.CalledProcessError:
            print(f"Failed to clone repository: {repo_url}")
            return None

def apply_crm_convert(dest_recipe_dir, meta_yaml_path):
    """
    Apply the crm convert tool to the given meta.yaml file.
    """
    dest_file = os.path.join(dest_recipe_dir, "recipe.yaml")
    subprocess.run(["crm", "convert", meta_yaml_path, "--output", dest_file], check=False)

def save_new_recipe(dest_recipe_dir):
    """
    Save the new recipe in the specified directory.
    """
    meta_yaml_path = os.path.join(dest_recipe_dir, "meta.yaml")
    apply_crm_convert(dest_recipe_dir, meta_yaml_path)

def process_packages(package_names):
    """
    Process each package: check out feedstock, apply crm convert, and save new recipe.
    """
    base_dest_dir = os.getcwd()
    config = conf.load_config()
    all_existing_paths = {recipe['path'] for recipe in config['local']}
    for package_name in package_names:
        print(f"Processing package: {package_name}")
        dest_recipe_dir = checkout_feedstock(package_name, base_dest_dir)
        if dest_recipe_dir:
            save_new_recipe(dest_recipe_dir)
        else:
            print(f"Skipping package: {package_name} due to checkout failure")
            continue

        recipe_path = Path(os.path.join(dest_recipe_dir, "recipe.yaml"))
        if recipe_path.exists():
            rel_path = os.path.relpath(recipe_path, base_dest_dir)
            if rel_path not in all_existing_paths:
                config['local'].append({'path': rel_path})

    conf.save_config(config)

if __name__ == "__main__":
    package_names = [
        "certifi",
    "openssl",
    "ca-certificates",
    "conda",
    "python",
    "setuptools",
    "zlib",
    "pip",
    "sqlite",
    "wheel",
    "tk",
    "pytz",
    "six",
    "python-dateutil",
    "libpng",
    "jpeg",
    "numpy",
    "icu",
    "freetype",
    "openblas",
    "libzlib", "xz", "libblas", "_openmp_mutex", "liblapack", "libgcc-ng", "libcblas", "tk",
    "zlib", "libffi", "libgomp", "ncurses", "python-dateutil", "_libgcc_mutex", "six",
    "libopenblas", "libstdcxx-ng", "libgfortran-ng", "libgfortran5", "pthread-stubs",
    "xorg-libxdmcp", "bzip2", "lerc", "gettext", "python", "libnsl", "libbrotlienc",
    "libbrotlicommon", "libbrotlidec", "pcre2", "tomli", "libxcb", "brotli", "brotli-bin",
    "pyparsing", "pixman", "kiwisolver", "fonts-conda-forge", "fonts-conda-ecosystem",
    "cycler", "font-ttf-source-code-pro", "font-ttf-inconsolata", "font-ttf-dejavu-sans-mono",
    "font-ttf-ubuntu", "xorg-kbproto", "joblib", "munkres", "python_abi", "xorg-xproto", "toml"
]


    process_packages(package_names)
