from datetime import datetime
from enum import Enum

from flask import request
from sqlalchemy import Enum as SQLAlchemyEnum

from app import db


class PublicationType(Enum):
    NONE = "none"
    ANNOTATION_COLLECTION = "annotationcollection"
    BOOK = "book"
    BOOK_SECTION = "section"
    CONFERENCE_PAPER = "conferencepaper"
    DATA_MANAGEMENT_PLAN = "datamanagementplan"
    JOURNAL_ARTICLE = "article"
    PATENT = "patent"
    PREPRINT = "preprint"
    PROJECT_DELIVERABLE = "deliverable"
    PROJECT_MILESTONE = "milestone"
    PROPOSAL = "proposal"
    REPORT = "report"
    SOFTWARE_DOCUMENTATION = "softwaredocumentation"
    TAXONOMIC_TREATMENT = "taxonomictreatment"
    TECHNICAL_NOTE = "technicalnote"
    THESIS = "thesis"
    WORKING_PAPER = "workingpaper"
    OTHER = "other"


class DataSource(Enum):
    EXPERIMENTAL = "experimental"
    COMPUTATIONAL = "computational"
    LITERATURE = "literature"
    DATABASE = "database"
    OTHER = "other"


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    affiliation = db.Column(db.String(120))
    orcid = db.Column(db.String(120))
    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"))

    def to_dict(self):
        return {"name": self.name, "affiliation": self.affiliation, "orcid": self.orcid}


class DSMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_models = db.Column(db.String(120))
    number_of_features = db.Column(db.String(120))

    def __repr__(self):
        return f"DSMetrics<models={self.number_of_models}, features={self.number_of_features}>"


class DSMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deposition_id = db.Column(db.Integer)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_type = db.Column(SQLAlchemyEnum(PublicationType), nullable=False)
    publication_doi = db.Column(db.String(120))
    dataset_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))
    ds_metrics_id = db.Column(db.Integer, db.ForeignKey("ds_metrics.id"))
    ds_metrics = db.relationship("DSMetrics", uselist=False, backref="ds_meta_data", cascade="all, delete")
    authors = db.relationship("Author", backref="ds_meta_data", lazy=True, cascade="all, delete")


# Base abstract class for all dataset types
class BaseDataset(db.Model):
    __abstract__ = True

    # Common fields for all dataset types
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Common relationships (defined in subclasses with specific backrefs)

    # Common methods
    def name(self):
        return self.ds_meta_data.title

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_cleaned_publication_type(self):
        return self.ds_meta_data.publication_type.name.replace("_", " ").title()

    def get_zenodo_url(self):
        return f"https://zenodo.org/record/{self.ds_meta_data.deposition_id}" if self.ds_meta_data.dataset_doi else None

    def get_uvlhub_doi(self):
        import os

        domain = os.getenv("DOMAIN", "localhost")
        return f"http://{domain}/doi/{self.ds_meta_data.dataset_doi}"

    # Abstract methods to be implemented by subclasses
    def validate(self):
        """Validation specific to dataset type"""
        raise NotImplementedError("Subclasses must implement validate()")

    def files(self):
        """Get files associated with this dataset"""
        raise NotImplementedError("Subclasses must implement files()")

    def get_files_count(self):
        """Get count of files in this dataset"""
        raise NotImplementedError("Subclasses must implement get_files_count()")

    def get_file_total_size(self):
        """Get total size of all files"""
        raise NotImplementedError("Subclasses must implement get_file_total_size()")

    def get_file_total_size_for_human(self):
        from app.modules.dataset.services import SizeService

        return SizeService().get_human_readable_size(self.get_file_total_size())

    def to_dict(self):
        """Base dictionary representation"""
        return {
            "title": self.ds_meta_data.title,
            "id": self.id,
            "created_at": self.created_at,
            "created_at_timestamp": int(self.created_at.timestamp()),
            "description": self.ds_meta_data.description,
            "authors": [author.to_dict() for author in self.ds_meta_data.authors],
            "publication_type": self.get_cleaned_publication_type(),
            "publication_doi": self.ds_meta_data.publication_doi,
            "dataset_doi": self.ds_meta_data.dataset_doi,
            "tags": self.ds_meta_data.tags.split(",") if self.ds_meta_data.tags else [],
            "url": self.get_uvlhub_doi(),
            "download": f'{request.host_url.rstrip("/")}/dataset/download/{self.id}',
            "zenodo": self.get_zenodo_url(),
        }

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.id}>"


# Material record model - represents a single row in the materials CSV
class MaterialRecord(db.Model):
    __tablename__ = "material_record"

    id = db.Column(db.Integer, primary_key=True)
    materials_dataset_id = db.Column(db.Integer, db.ForeignKey("materials_dataset.id"), nullable=False)

    # CSV column fields
    material_name = db.Column(db.String(256), nullable=False)
    chemical_formula = db.Column(db.String(256))
    structure_type = db.Column(db.String(256))
    composition_method = db.Column(db.String(256))
    property_name = db.Column(db.String(256), nullable=False)
    property_value = db.Column(db.String(256), nullable=False)
    property_unit = db.Column(db.String(128))
    temperature = db.Column(db.Float)  # Changed from Integer to support decimal temperatures
    pressure = db.Column(db.Float)  # Changed from Integer to support decimal pressures
    data_source = db.Column(SQLAlchemyEnum(DataSource))
    uncertainty = db.Column(db.Float)  # Changed from Integer to support decimal uncertainty values
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "material_name": self.material_name,
            "chemical_formula": self.chemical_formula,
            "structure_type": self.structure_type,
            "composition_method": self.composition_method,
            "property_name": self.property_name,
            "property_value": self.property_value,
            "property_unit": self.property_unit,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "data_source": self.data_source.value if self.data_source else None,
            "uncertainty": self.uncertainty,
            "description": self.description,
        }

    def __repr__(self):
        return f"MaterialRecord<{self.id}: {self.material_name} - {self.property_name}>"


# Materials-specific dataset (for CSV materials data)
class MaterialsDataset(BaseDataset):
    __tablename__ = "materials_dataset"

    # Fields specific to materials datasets
    csv_file_path = db.Column(db.String(512))

    # Relationships specific to Materials datasets
    user = db.relationship("User", backref=db.backref("materials_datasets", lazy=True))
    ds_meta_data = db.relationship(
        "DSMetaData", backref=db.backref("materials_dataset", uselist=False), cascade="all, delete"
    )
    material_records = db.relationship("MaterialRecord", backref="materials_dataset", lazy=True, cascade="all, delete")
    download_records = db.relationship(
        "DSDownloadRecord", backref="materials_dataset", lazy=True, cascade="all, delete"
    )
    view_records = db.relationship("DSViewRecord", backref="materials_dataset", lazy=True, cascade="all, delete")

    def files(self):
        """Get CSV files for materials dataset"""
        # TODO: Implement file retrieval for materials datasets
        # This will depend on how you store CSV files
        return []

    def get_files_count(self):
        """Count CSV files in materials dataset"""
        return len(self.files())

    def get_file_total_size(self):
        """Calculate total size of CSV files"""
        # TODO: Implement size calculation for materials files
        return 0

    def get_materials_count(self):
        """Get count of material records in this dataset"""
        return len(self.material_records)

    def get_unique_materials(self):
        """Get unique material names in this dataset"""
        return list(set(record.material_name for record in self.material_records))

    def get_unique_properties(self):
        """Get unique property names measured in this dataset"""
        return list(set(record.property_name for record in self.material_records))

    def validate(self):
        """Validate materials dataset structure"""
        # Validations specific to materials CSV:
        # - Verify material records exist
        # - Validate required fields in records
        # - Check data consistency

        if not self.csv_file_path:
            raise ValueError("Materials dataset must have a CSV file path")

        if not self.material_records or len(self.material_records) == 0:
            raise ValueError("Materials dataset must have at least one material record")

        # Validate that all records have required fields
        for record in self.material_records:
            if not record.material_name:
                raise ValueError(f"Material record {record.id} is missing material_name")
            if not record.property_name:
                raise ValueError(f"Material record {record.id} is missing property_name")
            if not record.property_value:
                raise ValueError(f"Material record {record.id} is missing property_value")

        return True

    def to_dict(self):
        """Extended dictionary with materials-specific data"""
        from flask import url_for

        base_dict = super().to_dict()
        base_dict.update(
            {
                "csv_file_path": self.csv_file_path,
                "materials_count": self.get_materials_count(),
                "unique_materials": self.get_unique_materials(),
                "unique_properties": self.get_unique_properties(),
                "material_records": [record.to_dict() for record in self.material_records],
                "files": [file.to_dict() for file in self.files()] if self.files() else [],
                "files_count": self.get_files_count(),
                "total_size_in_bytes": self.get_file_total_size(),
                "total_size_in_human_format": self.get_file_total_size_for_human(),
                "dataset_type": "materials",
                "url": url_for("dataset.view_materials_dataset", dataset_id=self.id, _external=True),
            }
        )
        return base_dict


class DSDownloadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("materials_dataset.id"))
    download_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    download_cookie = db.Column(db.String(36), nullable=False)  # Assuming UUID4 strings

    def __repr__(self):
        return (
            f"<Download id={self.id} "
            f"dataset_id={self.dataset_id} "
            f"date={self.download_date} "
            f"cookie={self.download_cookie}>"
        )


class DSViewRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("materials_dataset.id"))
    view_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    view_cookie = db.Column(db.String(36), nullable=False)  # Assuming UUID4 strings

    def __repr__(self):
        return f"<View id={self.id} dataset_id={self.dataset_id} date={self.view_date} cookie={self.view_cookie}>"


class DOIMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_doi_old = db.Column(db.String(120))
    dataset_doi_new = db.Column(db.String(120))


class DatasetVersion(db.Model):
    """Model for storing dataset version snapshots"""

    __tablename__ = "dataset_version"

    id = db.Column(db.Integer, primary_key=True)
    materials_dataset_id = db.Column(db.Integer, db.ForeignKey("materials_dataset.id"), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Snapshots
    csv_snapshot_path = db.Column(db.String(512), nullable=False)
    metadata_snapshot = db.Column(db.JSON, nullable=False)

    # Change tracking
    changelog = db.Column(db.JSON, nullable=True)

    # Stats at version time
    records_count = db.Column(db.Integer)

    # Relationships
    materials_dataset = db.relationship(
        "MaterialsDataset",
        backref=db.backref(
            "versions", lazy=True, cascade="all, delete", order_by="DatasetVersion.version_number.desc()"
        ),
    )
    created_by = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "version_number": self.version_number,
            "created_at": self.created_at,
            "created_at_timestamp": int(self.created_at.timestamp()),
            "created_by": (
                f"{self.created_by.profile.name} {self.created_by.profile.surname}"
                if self.created_by and self.created_by.profile
                else "Unknown"
            ),
            "records_count": self.records_count,
            "changelog": self.changelog,
            "csv_snapshot_path": self.csv_snapshot_path,
        }

    def __repr__(self):
        return f"DatasetVersion<{self.id}: v{self.version_number} of dataset {self.materials_dataset_id}>"
