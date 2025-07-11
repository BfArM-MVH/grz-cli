import json
import shutil
from pathlib import Path

import grz_cli.cli
from click.testing import CliRunner
from grz_common.workers.submission import SubmissionValidationError


def test_validate_submission(
    temp_identifiers_config_file_path,
    working_dir_path,
):
    submission_dir = Path("tests/mock_files/submissions/valid_submission")

    shutil.copytree(submission_dir / "files", working_dir_path / "files", dirs_exist_ok=True)
    shutil.copytree(submission_dir / "metadata", working_dir_path / "metadata", dirs_exist_ok=True)

    testargs = [
        "validate",
        "--config-file",
        temp_identifiers_config_file_path,
        "--submission-dir",
        str(working_dir_path),
    ]

    runner = CliRunner()
    cli = grz_cli.cli.build_cli()
    result = runner.invoke(cli, testargs, catch_exceptions=False)

    # check if re-validation is skipped
    result = runner.invoke(cli, testargs, catch_exceptions=False)

    # test if command has correctly checked for:
    # - mismatched md5sums
    # - all files existing

    assert result.exit_code == 0, result.output


def test_validate_submission_incorrect_grz_id(
    temp_identifiers_config_file_path,
    working_dir_path,
):
    submission_dir = Path("tests/mock_files/submissions/valid_submission")

    shutil.copytree(submission_dir / "files", working_dir_path / "files", dirs_exist_ok=True)
    shutil.copytree(submission_dir / "metadata", working_dir_path / "metadata", dirs_exist_ok=True)

    with open(working_dir_path / "metadata" / "metadata.json", mode="r+") as metadata_file:
        metadata = json.load(metadata_file)

        # put a GRZ id into the metadata that does not match what's in the config
        metadata["submission"]["genomicDataCenterId"] = "GRZX00000"

        metadata_file.seek(0)
        json.dump(metadata, metadata_file)
        metadata_file.truncate()

    testargs = [
        "validate",
        "--config-file",
        temp_identifiers_config_file_path,
        "--submission-dir",
        str(working_dir_path),
    ]

    runner = CliRunner()
    cli = grz_cli.cli.build_cli()
    # set catch_exceptions to True because we expect this to fail
    result = runner.invoke(cli, testargs, catch_exceptions=True)
    exc_type, exc, *_ = result.exc_info
    assert exc_type == SubmissionValidationError
    assert "does not match genomic data center identifier" in str(exc)

    assert result.exit_code == 1, result.output
