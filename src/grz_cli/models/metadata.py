# generated by datamodel-codegen:
#   filename:  grz-schema.json
#   timestamp: 2024-10-22T09:41:51+00:00
#   version:   0.26.2
### Command run:
## datamodel-codegen --output-model-type pydantic_v2.BaseModel \
## --input src/grz_cli/resources/grz-schema.json \
## --use-schema-description --use-field-description --snake-case-field --use-standard-collections --use-union-operator \
## --field-constraints --use-annotated --enable-version-header --reuse-model --use-subclass-enum --union-mode smart \
## --class-name 'GrzSubmissionMetadata' --target-python-version 3.12
### Custom modifications:
### - disallow extra fields (no additional properties allowed)
### - validate_assignment (i.e. when setting properties, re-trigger validations)
### - use_enum_values (use values [strings] instead of enum variants)
### - remove those aliases which are covered by a global `alias_generator=to_camel` setting

from __future__ import annotations

from collections.abc import Generator
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)
from pydantic.alias_generators import to_camel

from ..file_operations import calculate_sha256


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        alias_generator=to_camel,
    )


class SubmissionType(StrEnum):
    """
    "initial" for first submission, "addition" for additional submission, "correction" for correction
    """

    initial = "initial"
    addition = "addition"
    correction = "correction"
    other = "other"


class Submission(StrictBaseModel):
    submission_date: date
    """
    Date of submission in ISO 8601 format YYYY-MM-DD
    """

    submission_type: SubmissionType
    """
    "initial" for first submission, "addition" for additional submission, "correction" for correction
    """

    index_case_id: Annotated[str, StringConstraints(pattern=r"^[a-fA-F0-9]{32}$")]
    """
    The VNg provided by RKI --> a unique 32-byte hex ID for the index case.
    """

    submitter_id: Annotated[str, StringConstraints(pattern=r"^[0-9]{9}$")]
    """
    Institutional ID of the submitter according to §293 SGB V
    """

    genomic_data_center_id: Annotated[
        str, StringConstraints(pattern=r"^GRZ[0-9]{6}$")
    ] = Field(..., alias="GenomicDataCenterId")
    """
    ID of the genomic data center node in format GRZXXXnnn
    """

    lab_name: str
    """
    Name of the sequencing lab
    """


class Gender(StrEnum):
    """
    Gender of the donor
    """

    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class MvConsentScope(StrictBaseModel):
    """
    the scope of the Modellvorhaben scope given by the patient
    """

    consent_mv_sequencing: bool = Field(..., alias="ConsentMVSequencing")
    """
    The patient's consent to participate in the Modellvorhaben and sequencing
    """

    consent_case_identification: bool = Field(..., alias="ConsentCaseIdentification")
    """
    The patient's consent to identify the case
    """

    consent_re_identification: bool = Field(..., alias="ConsentReIdentification")
    """
    The patient's consent to re-identify the case and to re-contact the patient in case of new findings
    """


class MvConsentTerminationScope(StrictBaseModel):
    """
    The scope of the termination of the Modellvorhaben consent
    """

    consent_mv_sequencing_termination: bool | None = Field(
        None, alias="ConsentMVSequencingTermination"
    )
    """
    The patient's termination of the Modellvorhaben consent to participate in the Modellvorhaben and sequencing
    """

    consent_case_identification_termination: bool | None = Field(
        None, alias="ConsentCaseIdentificationTermination"
    )
    """
    The patient's termination of the Modellvorhaben consent to identify the case
    """

    consent_re_identification_termination: bool | None = Field(
        None, alias="ConsentReIdentificationTermination"
    )
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
    Sample Conservation
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
    wes = "wes"
    wgs = "wgs"
    wgs_lr = "wgs_lr"
    wxs = "wxs"
    other = "other"
    unknown = "unknown"


class LibraryPrepkit(StrictBaseModel):
    name: str
    """
    Name of the library prepkit
    """
    version: str
    """
    Version of the library prepkit
    """


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


class SequencingLayout(StrEnum):
    """
    End type of sequencing
    """

    single_end = "single-end"
    paired_end = "paired-end"
    reverse = "reverse"
    other = "other"


class TumorCellCountmethod(StrEnum):
    """
    method used to determine cell count
    """

    pathology = "Pathology"
    bioinformatics = "Bioinformatics"
    other = "other"
    unknown = "unknown"


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
    Type of the file; if BED file is submitted, only 1 file is allowed
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


class File(StrictBaseModel):
    file_path: str
    """
    Path relative to the submission root, e.g.: sequencing_data/patient_001/patient_001_dna.bam
    """

    file_type: FileType
    """
    Type of the file; if BED file is submitted, only 1 file is allowed
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


class SequenceDatum(StrictBaseModel):
    bioinformatics_pipeline_name: str
    """
    Name of the bioinformatics pipeline used
    """

    reference_genome: str
    """
    Reference genome used
    """

    bioinformatics_pipeline_version: str
    """
    Version or commit hash of the bioinformatics pipeline
    """

    percent_bases_q30: Annotated[float, Field(strict=True, ge=0.0, le=100.0)]
    """
    Percentage of bases with Q30 or higher
    """

    mean_depth_of_coverage: Annotated[float, Field(strict=True, ge=0.0)]
    """
    Mean depth of coverage
    """

    min_coverage: Annotated[float, Field(strict=True, ge=0.0)]
    """
    Minimum coverage
    """

    targeted_regions_above_min_coverage: Annotated[
        float, Field(strict=True, ge=0.0, le=1.0)
    ]
    """
    Fraction of targeted regions that are above minimum coverage
    """

    read_length: Annotated[int, Field(strict=True, ge=0)]
    """
    An integer [0-inf]
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
    List of files generated
    """


class LabDatum(StrictBaseModel):
    lab_data_name: str
    """
    Name/ID of the biospecimen e.g. 'Blut DNA normal'
    """

    tissue_ontology: TissueOntology

    tissue_type_id: str
    """
    Tissue ID according to the Ontology in use
    """

    tissue_type_name: str
    """
    Tissue name according to the Ontology in use
    """

    sample_conservation: SampleConservation
    """
    Sample Conservation
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

    library_prepkit: LibraryPrepkit

    library_prepkit_manufacturer: str
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

    enrichment_kitdescription: str
    """
    Name/version of the enrichment kit
    """

    barcode: str
    """
    The barcode used or 'na'
    """

    sequencing_layout: SequencingLayout
    """
    End type of sequencing
    """

    tumor_cell_count: float | None = None
    """
    Tumor cell count in %
    """

    tumor_cell_countmethod: TumorCellCountmethod | None = None
    """
    method used to determine cell count
    """

    sequence_data: list[SequenceDatum]
    """
    Sequence data generated from the wet lab experiment
    """


class Donor(StrictBaseModel):
    case_id: str = Field(..., alias="caseID")
    """
    The VNg provided by RKI --> a unique 32-byte hex ID for the given donor.
    """

    gender: Gender
    """
    Gender of the donor
    """

    relation: str
    """
    Relation of the patient to the pedigree e.g. 'index', 'brother', etc.
    """

    mv_consent_date: date = Field(..., alias="MVConsentDate")
    """
    Date of the signature of the Modellvorhaben consent; Date in ISO 8601 format YYYY-MM-DD
    """

    mv_consent_presented_date: date | None = Field(None, alias="MVConsentPresentedDate")
    """
    Date of the presentation of the Modellvorhaben consent; Date in ISO 8601 format YYYY-MM-DD
    """

    mv_consent_version: str = Field(..., alias="MVConsentVersion")
    """
    Version of the research consent
    """

    mv_consent_scope: MvConsentScope = Field(..., alias="MVConsentScope")
    """
    the scope of the Modellvorhaben scope given by the patient
    """

    mv_consent_termination_date: date | None = Field(
        None, alias="MVConsentTerminationDate"
    )
    """
    Date of the termination of the Modellvorhaben consent; Date in ISO 8601 format YYYY-MM-DD
    """

    mv_consent_termination_scope: MvConsentTerminationScope | None = Field(
        None, alias="MVConsentTerminationScope"
    )
    """
    The scope of the termination of the Modellvorhaben consent
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
    Scope of the research consent given by the patient; shall be given in .json format
    """

    research_consent_revocationl_date: date | None = None
    """
    Date of the revocation of the research consent; Date in ISO 8601 format YYYY-MM-DD
    """

    research_consent_revocation_scope: dict[str, Any] | None = None
    """
    Scope of the revocation of the research consent given by the patient; shall be given in .json format
    """

    lab_data: list[LabDatum]
    """
    Lab data related to the donor
    """


class GrzSubmissionMetadata(StrictBaseModel):
    """
    General metadata schema for submissions to the GRZ
    """

    submission: Submission = Field(..., alias="Submission")

    donors: list[Donor] = Field(..., alias="Donors")
    """
    List of donors
    """
