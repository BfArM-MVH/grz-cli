# generated by datamodel-codegen:
#   filename:  grz-schema.json
#   timestamp: 2024-11-21T12:40:39+00:00
#   version:   0.26.2
### Command run:
## datamodel-codegen --output-model-type pydantic_v2.BaseModel \
## --input src/grz_cli/resources/grz-schema.json \
## --use-schema-description --use-field-description --snake-case-field --use-standard-collections --use-union-operator \
## --field-constraints --use-annotated --enable-version-header --reuse-model --use-subclass-enum --union-mode smart \
## --class-name 'GrzSubmissionMetadata' --use-double-quotes --target-python-version 3.12
### Custom modifications:
### - disallow extra fields (no additional properties allowed)
### - validate_assignment (i.e. when setting properties, re-trigger validations)
### - use_enum_values (use values [strings] instead of enum variants)
### - remove those aliases which are covered by a global `alias_generator=to_camel` setting

from __future__ import annotations

import json
import logging
import typing
from collections.abc import Generator
from datetime import date
from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)
from pydantic.alias_generators import to_camel

from grz_cli.file_operations import calculate_sha256  # type: ignore

log = logging.getLogger(__name__)


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        alias_generator=to_camel,
    )


class SubmissionType(StrEnum):
    """
    The options are: 'initial' for first submission, 'followup' is for followup submissions, 'addition' for additional submission, 'correction' for correction
    """

    initial = "initial"
    followup = "followup"
    addition = "addition"
    correction = "correction"


class GenomicStudyType(StrEnum):
    """
    whether additional persons are tested as well
    """

    single = "single"
    duo = "duo"
    trio = "trio"


class GenomicStudySubtype(StrEnum):
    """
    whether tumor and/or germ-line are tested
    """

    tumor_only = "tumor-only"
    tumor_germline = "tumor+germline"
    germline_only = "germline-only"


class Submission(StrictBaseModel):
    submission_date: date
    """
    Date of submission in ISO 8601 format YYYY-MM-DD
    """

    submission_type: SubmissionType
    """
    The options are: 'initial' for first submission, 'followup' is for followup submissions, 'addition' for additional submission, 'correction' for correction
    """

    tan_g: Annotated[str, StringConstraints(pattern=r"^[a-fA-F0-9]{64}$")]
    """
    The VNg of the genomic data of the patient that will be reimbursed --> a unique 32-length byte code represented in a hex string of length 64.
    """

    local_case_id: str | None = None
    """
    A local case identifier for synchronizing locally
    """

    submitter_id: Annotated[str, StringConstraints(pattern=r"^[0-9]{9}$")]
    """
    Institutional ID of the submitter according to §293 SGB V.
    """

    genomic_data_center_id: Annotated[
        str,
        StringConstraints(pattern=r"^(GRZ)[A-Z0-9]{3}[0-9]{3}$"),
    ]
    """
    ID of the genomic data center in the format GRZXXXnnn.
    """

    clinical_data_node_id: Annotated[str, StringConstraints(pattern=r"^(KDK)[A-Z0-9]{3}[0-9]{3}$")]
    """
    ID of the clinical data node in the format KDKXXXnnn.
    """

    genomic_study_type: GenomicStudyType
    """
    whether additional persons are tested as well
    """

    genomic_study_subtype: GenomicStudySubtype
    """
    whether tumor and/or germ-line are tested
    """

    lab_name: str
    """
    Name of the sequencing lab.
    """


class Gender(StrEnum):
    """
    Gender of the donor.
    """

    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class Relation(StrEnum):
    """
    Relationship of the donor in respect to the index patient, e.g. 'index', 'brother', 'mother', etc.
    """

    mother = "mother"
    father = "father"
    brother = "brother"
    sister = "sister"
    child = "child"
    self = "self"
    other = "other"


class MvConsentScope(StrictBaseModel):
    """
    The scope of the Modellvorhaben consent given by the donor.
    """

    consent_mv_sequencing: bool
    """
    The donor's consent to participate in the Modellvorhaben and sequencing.
    """

    consent_case_identification: bool
    """
    The donor's consent to identify the case.
    """

    consent_re_identification: bool
    """
    The donor's consent to be re-identified and to be re-contacted in case of new findings.
    """


class MvConsentTerminationScope(StrictBaseModel):
    """
    The scope of the termination of the Modellvorhaben consent.
    """

    consent_mv_sequencing_termination: bool | None = None
    """
    The patient's termination of the Modellvorhaben consent to participate in the Modellvorhaben and sequencing
    """

    consent_case_identification_termination: bool | None = None
    """
    The patient's termination of the Modellvorhaben consent to identify the case
    """

    consent_re_identification_termination: bool | None = None
    """
    The patient's termination of the Modellvorhaben consent to re-identify the case and to re-contact the patient in case of new findings
    """


class TissueOntology(StrictBaseModel):
    name: str
    """
    Name of the tissue ontology
    """

    version: str
    """
    Version of the tissue ontology
    """


class SampleConservation(StrEnum):
    """
    Sample conservation
    """

    fresh_tissue = "fresh-tissue"
    cryo_frozen = "cryo-frozen"
    ffpe = "ffpe"
    other = "other"
    unknown = "unknown"


class SequenceType(StrEnum):
    """
    Type of sequence (DNA or RNA)
    """

    dna = "dna"
    rna = "rna"


class SequenceSubtype(StrEnum):
    """
    Subtype of sequence (germline, somatic, etc.)
    """

    germline = "germline"
    somatic = "somatic"
    other = "other"
    unknown = "unknown"


class FragmentationMethod(StrEnum):
    """
    Fragmentation method
    """

    sonication = "sonication"
    enzymatic = "enzymatic"
    none = "none"
    other = "other"
    unknown = "unknown"


class LibraryType(StrEnum):
    """
    Library type
    """

    panel = "panel"
    panel_lr = "panel_lr"
    wes = "wes"
    wes_lr = "wes_lr"
    wgs = "wgs"
    wgs_lr = "wgs_lr"
    wxs = "wxs"
    wxs_lr = "wxs_lr"
    other = "other"
    unknown = "unknown"


class EnrichmentKitManufacturer(StrEnum):
    """
    Manufacturer of the enrichment kit
    """

    illumina = "Illumina"
    agilent = "Agilent"
    twist = "Twist"
    neb = "NEB"
    other = "other"
    unknown = "unknown"
    none = "none"


class SequencingLayout(StrEnum):
    """
    The sequencing layout, aka the end type of sequencing.
    """

    single_end = "single-end"
    paired_end = "paired-end"
    reverse = "reverse"
    other = "other"


class TumorCellCountMethod(StrEnum):
    """
    Method used to determine cell count.
    """

    pathology = "Pathology"
    bioinformatics = "Bioinformatics"
    other = "other"
    unknown = "unknown"


class TumorCellCount(StrictBaseModel):
    """
    Tuple of tumor cell counts and how they were determined.
    """

    count: Annotated[float, Field(alias="tumorCellCount", ge=0.0, le=100.0)]
    """
    Tumor cell count in %
    """

    method: TumorCellCountMethod
    """
    Method used to determine cell count.
    """


class CallerUsedItem(StrictBaseModel):
    name: str
    """
    Name of the caller used
    """

    version: str
    """
    Version of the caller used
    """


class FileType(StrEnum):
    """
    Type of the file; if BED file is submitted, only 1 file is allowed.
    """

    bam = "bam"
    vcf = "vcf"
    bed = "bed"
    fastq = "fastq"


class ChecksumType(StrEnum):
    """
    Type of checksum algorithm used
    """

    sha256 = "sha256"


class ReadOrder(StrEnum):
    """
    Indicates the read order for paired-end reads.
    """

    r1 = "R1"
    r2 = "R2"


class File(StrictBaseModel):
    file_path: str
    """
    Path relative to the submission root, e.g.: sequencing_data/patient_001/patient_001_dna.bam
    """

    file_type: FileType
    """
    Type of the file; if BED file is submitted, only 1 file is allowed.
    """

    checksum_type: ChecksumType | None = ChecksumType.sha256
    """
    Type of checksum algorithm used
    """

    file_checksum: Annotated[str, StringConstraints(pattern=r"^[a-fA-F0-9]{64}$")]
    """
    checksum of the file
    """

    file_size_in_bytes: Annotated[int, Field(strict=True, ge=0)]
    """
    Size of the file in bytes
    """

    read_order: ReadOrder | None = None
    """
    Indicates the read order for paired-end reads.
    """

    flowcell_id: str | None = None
    """
    Indicates the flow cell.
    """

    lane_id: str | None = None
    """
    Indicates the lane
    """

    def validate_data(self, local_file_path: Path) -> Generator[str]:
        """
        Validates whether the provided file matches this metadata.

        :param local_file_path: Path to the actual file (resolved if symlinked)
        :return: Generator of errors
        """
        # Resolve file path
        local_file_path = local_file_path.resolve()

        # Check if path exists
        if not local_file_path.exists():
            yield f"{str(self.file_path)} does not exist!"
            # Return here as following tests cannot work
            return

        # Check if path is a file
        if not local_file_path.is_file():
            yield f"{str(self.file_path)} is not a file!"
            # Return here as following tests cannot work
            return

        # Check if the checksum is correct
        if self.checksum_type == "sha256":
            calculated_checksum = calculate_sha256(local_file_path)
            if self.file_checksum != calculated_checksum:
                yield (
                    f"{str(self.file_path)}: Checksum mismatch! "
                    f"Expected: '{self.file_checksum}', calculated: '{calculated_checksum}'."
                )
        else:
            yield (
                f"{str(self.file_path)}: Unsupported checksum type: {self.checksum_type}. "
                f"Supported types: {[e.value for e in ChecksumType]}"
            )

        # Check file size
        if self.file_size_in_bytes != local_file_path.stat().st_size:
            yield (
                f"{str(self.file_path)}: File size mismatch! "
                f"Expected: '{self.file_size_in_bytes}', observed: '{local_file_path.stat().st_size}'."
            )

    def encrypted_file_path(self):
        return self.file_path + ".c4gh"


class PercentBasesAboveQualityThreshold(StrictBaseModel):
    """Percentage of bases with a specified minimum quality threshold"""

    minimum_quality: Annotated[float, Field(strict=True, ge=0.0)]
    """The minimum quality score threshold"""

    percent: Annotated[float, Field(strict=True, ge=0.0, le=100.0)]
    """
    Percentage of bases with a specified minimum quality threshold, according to https://www.bfarm.de/SharedDocs/Downloads/DE/Forschung/modellvorhaben-genomsequenzierung/Qs-durch-GRZ.pdf?__blob=publicationFile
    """


class SequenceData(StrictBaseModel):
    bioinformatics_pipeline_name: str
    """
    Name of the bioinformatics pipeline used
    """

    bioinformatics_pipeline_version: str
    """
    Version or commit hash of the bioinformatics pipeline
    """

    reference_genome: str
    """
    Reference genome used
    """

    percent_bases_above_quality_threshold: PercentBasesAboveQualityThreshold
    """
    Percentage of bases with a specified minimum quality threshold
    """

    mean_depth_of_coverage: Annotated[float, Field(strict=True, ge=0.0)]
    """
    Mean depth of coverage
    """

    min_coverage: Annotated[float, Field(strict=True, ge=0.0)]
    """
    Minimum coverage
    """

    targeted_regions_above_min_coverage: Annotated[float, Field(strict=True, ge=0.0, le=1.0)]
    """
    Fraction of targeted regions that are above minimum coverage
    """

    read_length: Annotated[int, Field(strict=True, ge=0)]
    """
    The read length; in the case of long-read sequencing it is the rounded average read length.
    """

    non_coding_variants: bool
    """
    The analysis includes non-coding variants -> true or false
    """

    caller_used: list[CallerUsedItem]
    """
    Caller that is used in the pipeline
    """

    files: list[File]
    """
    List of files generated and required in this analysis.
    """

    def contains_files(self, file_type: FileType) -> bool:
        return any(f.file_type == file_type for f in self.files)

    def list_files(self, file_type: FileType) -> list[File]:
        return [f for f in self.files if f.file_type == file_type]


class LabDatum(StrictBaseModel):
    lab_data_name: str
    """
    Name/ID of the biospecimen e.g. 'Blut DNA normal'
    """

    tissue_ontology: TissueOntology

    tissue_type_id: str
    """
    Tissue ID according to the ontology in use.
    """

    tissue_type_name: str
    """
    Tissue name according to the ontology in use.
    """

    sample_date: date
    """
    Date of sample in ISO 8601 format YYYY-MM-DD
    """

    sample_conservation: SampleConservation
    """
    Sample conservation
    """

    sequence_type: SequenceType
    """
    Type of sequence (DNA or RNA)
    """

    sequence_subtype: SequenceSubtype
    """
    Subtype of sequence (germline, somatic, etc.)
    """

    fragmentation_method: FragmentationMethod
    """
    Fragmentation method
    """

    library_type: LibraryType
    """
    Library type
    """

    library_prep_kit: str
    """
    Name/version of the library prepkit
    """

    library_prep_kit_manufacturer: str
    """
    Library prep kit manufacturer
    """

    sequencer_model: str
    """
    Name/version of the sequencer model
    """

    sequencer_manufacturer: str
    """
    Sequencer manufacturer
    """

    kit_name: str
    """
    Name/version of the sequencing kit
    """

    kit_manufacturer: str
    """
    Sequencing kit manufacturer
    """

    enrichment_kit_manufacturer: EnrichmentKitManufacturer
    """
    Manufacturer of the enrichment kit
    """

    enrichment_kit_description: str
    """
    Name/version of the enrichment kit
    """

    barcode: str
    """
    The barcode used or 'na'
    """

    sequencing_layout: SequencingLayout
    """
    The sequencing layout, aka the end type of sequencing.
    """

    tumor_cell_count: list[TumorCellCount] | None = None
    """
    Tuple of tumor cell counts and how they were determined.
    """

    sequence_data: SequenceData | None = None
    """
    Sequence data generated from the wet lab experiment.
    """

    def has_sequence_data(self) -> bool:
        return self.sequence_data is not None

    @model_validator(mode="after")
    def validate_sequencing_setup(self) -> Self:
        if self.library_type in {LibraryType.wxs, LibraryType.wxs_lr} and self.sequence_type != SequenceType.rna:
            raise ValueError(
                f"Error in lab datum '{self.lab_data_name}': "
                f"WXS requires RNA sequencing, but got '{self.sequence_type}'."
            )
        return self


class Donor(StrictBaseModel):
    tan_g: Annotated[str, StringConstraints(pattern=r"^[a-fA-F0-9]{64}$")]
    """
    The VNg of the genomic data of the donor --> a unique 32-length byte code represented in a hex string of length 64.
    """

    local_case_id: str | None = None
    """
    A local case identifier for synchronizing locally
    """

    gender: Gender
    """
    Gender of the donor.
    """

    relation: Relation
    """
    Relationship of the donor in respect to the index patient, e.g. 'index', 'brother', 'mother', etc.
    """

    mv_consent_date: date
    """
    Date of the signature of the Modellvorhaben consent; Date in ISO 8601 format YYYY-MM-DD
    """

    mv_consent_presented_date: date | None = None
    """
    Date of the presentation of the Modellvorhaben consent; Date in ISO 8601 format YYYY-MM-DD
    """

    mv_consent_version: str
    """
    Version of the research consent
    """

    mv_consent_scope: MvConsentScope
    """
    The scope of the Modellvorhaben consent given by the donor.
    """

    mv_consent_termination_date: date | None = None
    """
    Date of the termination of the Modellvorhaben consent; Date in ISO 8601 format YYYY-MM-DD
    """

    mv_consent_termination_scope: MvConsentTerminationScope | None = None
    """
    The scope of the termination of the Modellvorhaben consent.
    """

    research_consent_date: date | None = None
    """
    Date of the signature of the research consent; Date in ISO 8601 format YYYY-MM-DD
    """

    research_consent_presented_date: date | None = None
    """
    Date of the presentation of the research consent; Date in ISO 8601 format YYYY-MM-DD
    """

    research_consent_version: str | None = None
    """
    Version of the research consent
    """

    research_consent_scope: dict[str, Any] | None = None
    """
    Scope of the research consent given by the patient; shall be given in JSON format.
    """

    research_consent_revocation_date: date | None = None
    """
    Date of the revocation of the research consent; Date in ISO 8601 format YYYY-MM-DD
    """

    research_consent_revocation_scope: dict[str, Any] | None = None
    """
    Scope of the revocation of the research consent given by the patient; shall be given in JSON format
    """

    lab_data: list[LabDatum]
    """
    Lab data related to the donor.
    """

    @model_validator(mode="after")
    def warn_empty_sequence_data(self):
        for lab_datum in self.lab_data:
            if not lab_datum.has_sequence_data():
                log.warning(
                    f"No sequence data found for lab datum '{lab_datum.lab_data_name}' in donor '{self.tan_g}'. "
                    "Is this a submission without sequence data?"
                )
        return self

    @model_validator(mode="after")
    def validate_target_bed_files_exist(self):
        """
        Check if the submission has the required bed files for panel sequencing.
        """
        lib_types = {
            LibraryType.panel,
            LibraryType.wes,
            LibraryType.wxs,
            LibraryType.panel_lr,
            LibraryType.wes_lr,
            LibraryType.wxs_lr,
        }

        for lab_datum in self.lab_data:
            if (
                lab_datum.has_sequence_data()
                and lab_datum.library_type in lib_types
                and not lab_datum.sequence_data.contains_files(FileType.bed)
            ):
                raise ValueError(f"BED file missing for lab datum '{lab_datum.lab_data_name}' in donor '{self.tan_g}'.")

        return self

    @model_validator(mode="after")
    def validate_vcf_file_exists(self):
        """
        Check if there is a VCF file
        """
        for lab_datum in self.lab_data:
            if lab_datum.has_sequence_data() and not lab_datum.sequence_data.contains_files(FileType.vcf):
                raise ValueError(f"VCF file missing for lab datum '{lab_datum.lab_data_name}' in donor '{self.tan_g}'.")

        return self

    @model_validator(mode="after")
    def validate_fastq_file_exists(self):
        """
        Check if there is a FASTQ file
        """
        for lab_datum in self.lab_data:
            if not lab_datum.has_sequence_data():
                # Skip if no sequence data is present
                continue
            fastq_files = lab_datum.sequence_data.list_files(FileType.fastq)

            if len(fastq_files) == 0:
                raise ValueError("No FASTQ file found!")
            elif lab_datum.sequencing_layout == SequencingLayout.paired_end:
                # check if read order is specified
                for i in fastq_files:
                    if i.read_order is None:
                        raise ValueError(
                            f"Error in lab datum '{lab_datum.lab_data_name}' of donor '{self.tan_g}': "
                            f"No read order specified for FASTQ file '{i.file_path}'!"
                        )

                # check if there is an equal number of R1 and R2 files
                r1_fastq_files = [i for i in fastq_files if i.read_order == ReadOrder.r1]
                r2_fastq_files = [i for i in fastq_files if i.read_order == ReadOrder.r2]

                if len(r1_fastq_files) != len(r2_fastq_files):
                    raise ValueError(
                        f"Error in lab datum '{lab_datum.lab_data_name}' of donor '{self.tan_g}': "
                        f"Paired end sequencing layout but number of R1 FASTQ files ({len(r1_fastq_files)})"
                        f" differs from number of R2 FASTQ files ({len(r2_fastq_files)})!"
                    )
        return self


class GrzSubmissionMetadata(StrictBaseModel):
    """
    General metadata schema for submissions to the GRZ
    """

    submission: Submission

    donors: list[Donor]
    """
    List of donors including the index patient.
    """

    @model_validator(mode="after")
    def validate_donor_count(self):
        """
        Check whether the submission has the required number of donors based on the study type.
        """
        study_type = self.submission.genomic_study_type

        match study_type:
            case GenomicStudyType.single:
                # Check if the submission has at least one donor
                if not self.donors:
                    raise ValueError("At least one donor is required for a single study.")
            case GenomicStudyType.duo:
                # Check if the submission has at least two donors
                if len(self.donors) < 2:
                    raise ValueError("At least two donors are required for a duo study.")
            case GenomicStudyType.trio:
                # Check if the submission has at least three donors
                if len(self.donors) < 3:
                    raise ValueError("At least three donors are required for a trio study.")

        return self

    @model_validator(mode="after")
    def check_for_tumor_cell_count(self):
        """
        Check if oncology samples have tumor cell counts.
        """
        for donor in self.donors:
            case_id = donor.tan_g
            for lab_datum in donor.lab_data:
                if lab_datum.sequence_subtype == SequenceSubtype.somatic and lab_datum.tumor_cell_count is None:
                    raise ValueError(
                        f"Missing tumor cell count for donor '{case_id}', lab datum '{lab_datum.lab_data_name}'!"
                    )

        return self

    @model_validator(mode="after")
    def validate_thresholds(self):
        """
        Check if the submission meets the minimum mean coverage requirements.
        """
        threshold_definitions = _load_thresholds()

        for donor in self.donors:
            for lab_datum in donor.lab_data:
                key = (
                    self.submission.genomic_study_subtype,
                    lab_datum.library_type,
                    lab_datum.sequence_subtype,
                )
                thresholds = threshold_definitions.get(key)
                if thresholds is None:
                    log.warning(f"Thresholds for {key} not found! Skipping.")
                    continue

                _check_thresholds(donor, lab_datum, thresholds)

        return self


def _check_thresholds(donor: Donor, lab_datum: LabDatum, thresholds: dict[str, Any]):
    if not lab_datum.has_sequence_data():
        # Skip if no sequence data is present; warning issues in the validator `warn_empty_sequence_data` of `Donor`.
        return
    case_id = donor.tan_g
    lab_data_name = lab_datum.lab_data_name
    # mypy cannot reason about the `has_sequence_data` check
    sequence_data = typing.cast(SequenceData, lab_datum.sequence_data)

    mean_depth_of_coverage_t = thresholds.get("meanDepthOfCoverage")
    mean_depth_of_coverage_v = sequence_data.mean_depth_of_coverage
    if mean_depth_of_coverage_t and mean_depth_of_coverage_v < mean_depth_of_coverage_t:
        raise ValueError(
            f"Mean depth of coverage for donor '{case_id}', lab datum '{lab_data_name}' "
            f"below threshold: {mean_depth_of_coverage_v} < {mean_depth_of_coverage_t}"
        )

    read_length_t = thresholds.get("readLength")
    read_length_v = sequence_data.read_length
    if read_length_t and read_length_v < read_length_t:
        raise ValueError(
            f"Read length for donor '{case_id}', lab datum '{lab_data_name}' "
            f"below threshold: {read_length_v} < {read_length_t}"
        )

    if t := thresholds.get("targetedRegionsAboveMinCoverage"):
        min_coverage_t = t.get("minCoverage")
        min_coverage_v = sequence_data.min_coverage

        fraction_above_t = t.get("fractionAbove")
        fraction_above_v = sequence_data.targeted_regions_above_min_coverage

        if min_coverage_t and min_coverage_v < min_coverage_t:
            raise ValueError(
                f"Minimum coverage for donor '{case_id}', lab datum '{lab_data_name}' "
                f"below threshold: {min_coverage_v} < {min_coverage_t}"
            )
        if fraction_above_t and fraction_above_v < fraction_above_t:
            raise ValueError(
                f"Fraction of targeted regions above minimum coverage for donor '{case_id}', "
                f"lab datum '{lab_data_name}' below threshold: "
                f"{fraction_above_v} < {fraction_above_t}"
            )


type Thresholds = dict[tuple[str, str, str], dict[str, Any]]


def _load_thresholds() -> Thresholds:
    threshold_definitions = json.load(
        files("grz_cli").joinpath("resources", "thresholds.json").open("r", encoding="utf-8")
    )
    threshold_definitions = {
        (d["genomicStudySubtype"], d["libraryType"], d["sequenceSubtype"]): d["thresholds"]
        for d in threshold_definitions
    }
    return threshold_definitions
