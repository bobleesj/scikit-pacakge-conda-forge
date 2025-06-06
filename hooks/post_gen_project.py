import warnings
from hashlib import sha256
from pathlib import Path

import requests

# Generate the SHA256 hash from the distribution source
source_url = ""
source_yaml = ""
pep_name = "{{ cookiecutter.module_name }}".replace(".", "_").replace("-", "_").lower()
while "__" in pep_name:
    pep_name = pep_name.replace("__", "_")
if "{{ cookiecutter.source }}" == "PyPi":
    source_url = f"https://pypi.org/packages/source/{pep_name[0]}/{pep_name}/{pep_name}-{{ cookiecutter.version }}.tar.gz"
    source_yaml = f"https://pypi.org/packages/source/{pep_name[0]}/{pep_name}/{pep_name}-" + "{{ "{{ version }}" | safe }}" + ".tar.gz"
if "{{ cookiecutter.source }}" == "GitHub":
    source_url = "https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.repo_name }}/archive/{{ cookiecutter.version }}.tar.gz"
    source_yaml = "https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.repo_name }}/archive/" + "{{ "{{ version }}" | safe }}" + ".tar.gz"
tar_gz_dist = requests.get(source_url)
sha256_hash = sha256(tar_gz_dist.content).hexdigest()

if sha256_hash.strip() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" or sha256_hash.strip() == "0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5":
    warnings.warn("SHA256 Hash Returned Emtpy File Hash, make sure your .tar.gz is uploaded to {{ cookiecutter.source }}!")

# Read the main.yml file line by line
meta_yml_path = Path.cwd() / "meta.yaml"
with open(meta_yml_path, 'r') as mfile:
    mfile_txt = mfile.read()

    # Add the SHA256
    mfile_txt = mfile_txt.replace("GENERATE_SHA", f"{sha256_hash}")

    # Add the source
    mfile_txt = mfile_txt.replace("GENERATE_SOURCE", f"{source_yaml}")

    def add_list(csv, replace_string, txt):
        file_txt = txt
        csv_list = list(map(str.strip, csv.split(',')))
        csv_list_pruned = []
        for element in csv_list:
            if len(element) > 0:
                # Requirements version formatting
                while ">= " in element:
                    element = element.replace(">= ", ">=")
                csv_list_pruned.append(element)
        csv_list = csv_list_pruned
        if len(csv_list) == 0:
            # Depends on how the carriage return is stored
            file_txt = file_txt.replace(f"\r\n    - {replace_string}", "")
            file_txt = file_txt.replace(f"\n    - {replace_string}", "")
        else:
            csv_str = "\n    - ".join(csv_list)
            file_txt = file_txt.replace(f"{replace_string}", csv_str)
        return file_txt

    # Add the build requirements
    mfile_txt = add_list("{{ cookiecutter.build_requirements }}", "GENERATE_BUILD_REQUIREMENTS", mfile_txt)

    # Add the host requirements
    mfile_txt = add_list("{{ cookiecutter.host_requirements }}", "GENERATE_HOST_REQUIREMENTS", mfile_txt)

    # Add the runtime requirements
    mfile_txt = add_list("{{ cookiecutter.runtime_requirements }}", "GENERATE_RUN_REQUIREMENTS", mfile_txt)

    # Add the testing requirements
    mfile_txt = add_list("{{ cookiecutter.testing_requirements }}", "GENERATE_TEST_REQUIREMENTS", mfile_txt)

    # Add the maintainers
    mfile_txt = add_list("{{ cookiecutter.recipe_maintainers }}", "GENERATE_MAINTAINERS", mfile_txt)

with open(meta_yml_path, 'w') as mfile:
    mfile.write(mfile_txt)
