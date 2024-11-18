# GRZ CLI

A command-line tool for validating, encrypting, uploading and downloading submissions to/from a GDC/GRZ (Genomrechenzentrum).

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Exemplary submission procedure](#exemplary-submission-procedure)
- [Command-Line Interface](#command-line-interface)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

This tool provides a way to validate files, encrypt/decrypt files using the [crypt4gh](https://crypt4gh.readthedocs.io/en/latest/) library and upload/download the encrypted files to an S3 bucket of a GDC/GRZ. It also logs the progress and outcomes of these operations in a metadata file.

It is recommended to have the following folder structure for a single submission:

```
EXAMPLE_SUBMISSION
├── files
│   ├── aaaaaaaa00000000aaaaaaaa00000000_blood_normal.read1.fastq.gz
│   ├── aaaaaaaa00000000aaaaaaaa00000000_blood_normal.read2.fastq.gz
│   ├── aaaaaaaa00000000aaaaaaaa00000000_blood_normal.vcf
│   ├── aaaaaaaa00000000aaaaaaaa00000000_blood_tumor.read1.fastq.gz
│   ├── aaaaaaaa00000000aaaaaaaa00000000_blood_tumor.read2.fastq.gz
│   ├── aaaaaaaa00000000aaaaaaaa00000000_blood_tumor.vcf
│   ├── target_regions.bed
└── metadata
    └── metadata.json
```

The current version of the tool requires the `working_dir` to have at least as much free disk space as the total size of the data being submitted.
## Features

- **Validation**: Validate file checksums, basic file metadata and BfArM requirements.
- **Encryption**: Encrypt files using `crypt4gh`.
- **Decryption**: Encrypt files using `crypt4gh`.
- **Upload**: Upload encrypted files directly to a GRZ either (via built-in `boto3` or external `s3cmd`).
- **Download**: Download encrypted files from a GRZ.
- **Logging**: Log progress and results of operations

## Installation

### End-user
This tool uses the `conda` package manager.
If `conda` is not yet available on your system, you can install the [Miniforge conda distribution](https://github.com/conda-forge/miniforge) by running the following commands:
```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```
Next, install the `grz-cli` tool:
```bash
# TODO update: This requires membership in the repository
# download environment.yaml from the git repository:
git archive --remote=ssh://git@codebase.helmholtz.cloud/grz-mv-genomseq/grz-cli.git dev environment.yaml | tar -xv
# TODO update: This will work once the repository is publicly accessible:
# download environment.yaml from the git repository:
curl -L "https://codebase.helmholtz.cloud/grz-mv-genomseq/grz-cli/-/raw/v0.1.0/environment.yaml?ref_type=heads" > environment.yaml

# create conda environment and activate it
conda env create -f environment.yaml -n grz-tools
conda activate grz-tools

# install the grz-cli tool
# TODO update: This requires membership in the repository
pip install "git+ssh://git@codebase.helmholtz.cloud/grz-mv-genomseq/grz-cli.git@dev"
# TODO update: This will work once the repository is publicly accessible:
pip install "git+https://codebase.helmholtz.cloud/grz-mv-genomseq/grz-cli@v0.1.0"
```

### Development setup
For development purposes, you can clone the repository and install the package in editable mode:

```bash
git clone https://codebase.helmholtz.cloud/grz-mv-genomseq/grz-cli
# create conda environment and activate it
conda env create -f grz-cli/environment-dev.yaml -n grz-tools-dev
conda activate grz-tools-dev
# install the grz-cli tool
pip install -e grz-cli/
```

## Usage

### Configuration
**The configuration file will be provided by your associated GRZ, please place it into `~/.config/grz-cli/config.yaml`.**

The tool requires a configuration file in YAML format to specify the S3 bucket and other options.
For an exemplary configuration, see [resources/config.yaml](resources/config.yaml).

S3 access and secret key can be listed either in the config file or as environment variable (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

### Exemplary submission procedure
After preparing your submission as outlined above, you can use the following commands to validate, encrypt and upload the submission: 
```sh
# Validate the submission
grz-cli validate --submission-dir EXAMPLE_SUBMISSION

# Encrypt the submission
grz-cli encrypt --submission-dir EXAMPLE_SUBMISSION

# Upload the submission
grz-cli upload --submission-dir EXAMPLE_SUBMISSION
```

### Troubleshooting
**In case of issues, please re-run your commands with `grz-cli --log-level DEBUG --log-file <your-log-file.log> [...]` and submit the log file to the GRZ data steward!**

## Command-Line Interface

`grz-cli` provides a command-line interface with the following subcommands:

### validate

It is recommended to run this command before continuing with encryption and upload.
Progress files are stored relative to the submission directory.

- `--submission-dir`: Path to the submission directory containing both 'metadata/' and 'files/' directories [**Required**]

Example usage:

```bash
grz_cli validate --submission-dir foo
```

Option is for the usage at a hospital (Leistungserbringer) and GDC/GRZ.

### encrypt

If a working directory is not provided, then the current directory is used automatically. The log-files are going to be stored in the sub-folder of the working directory.
Files are stored in a folder named `encrypted_files` as a sub-folder of the working directory.

- `-s, --submission-dir`: Path to the submission directory containing both 'metadata/' and 'files/' directories [**Required**]
- `-c, --config-file`: Path to config file [_optional_]

```bash
grz-cli encrypt --submission-dir foo
```

Option is for the usage at a hospital (Leistungserbringer). Please approach your GDC/GRZ for a valid config file.

### decrypt

Decrypt a submission using the GRZ private key.

- `-s, --submission-dir`: Path to the submission directory containing both 'metadata/' and 'encrypted_files/' directories  [**Required**]
- `-c,--config-file`: Path to config file [_optional_]

```bash
grz-cli decrypt --submission-dir foo
```

Option is for the usage at a GDC/GRZ.

### upload

Upload the submission into a S3 structure of a GRZ.

- `-s, --submission-dir`: Path to the submission directory containing both 'metadata/' and 'encrypted_files/' directories [**Required**]
- `-c, --config-file`: Path to config file [_optional_]

Example usage:

```bash
grz-cli upload --submission-dir foo
```

Option is for the usage at a hospital (Leistungserbringer). Please approach your GDC/GRZ for a valid config file.

### download

Download a submission from a GRZ

- `-s, --submission-id`: S3 submission prefix [**Required**]
- `-o, --output-dir`: Path to the target submission output directory [**Required**]
- `-c, --config-file`: Path to config file [_optional_]

Example usage:

```bash
grz-cli download SUBMISSION_ID --submission-id foo --output-dir bar
```

Option is for the usage at a GDC/GRZ.

## Testing

To run the tests, navigate to the root directory of your project and invoke `pytest`.
Alternatively, install `uv` and `tox` and run `uv run tox`.

## Contributing

<!-- Add details about how others can contribute to the project -->

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

Parts of `cryp4gh` code is used in modified form

