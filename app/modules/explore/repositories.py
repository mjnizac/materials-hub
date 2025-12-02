import re

import unidecode
from sqlalchemy import or_

from app.modules.dataset.models import Author, MaterialRecord, MaterialsDataset, DSMetaData, PublicationType
from core.repositories.BaseRepository import BaseRepository


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(MaterialsDataset)

    def filter(self, query="", sorting="newest", publication_type="any", tags=[], **kwargs):
        # Normalize and remove unwanted characters
        normalized_query = unidecode.unidecode(query).lower()
        cleaned_query = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query)

        filters = []
        for word in cleaned_query.split():
            filters.append(DSMetaData.title.ilike(f"%{word}%"))
            filters.append(DSMetaData.description.ilike(f"%{word}%"))
            filters.append(Author.name.ilike(f"%{word}%"))
            filters.append(Author.affiliation.ilike(f"%{word}%"))
            filters.append(Author.orcid.ilike(f"%{word}%"))
            filters.append(MaterialRecord.material_name.ilike(f"%{word}%"))
            filters.append(MaterialRecord.chemical_formula.ilike(f"%{word}%"))
            filters.append(MaterialRecord.property_name.ilike(f"%{word}%"))
            filters.append(MaterialRecord.description.ilike(f"%{word}%"))
            filters.append(DSMetaData.tags.ilike(f"%{word}%"))

        datasets = (
            self.model.query.join(MaterialsDataset.ds_meta_data)
            .join(DSMetaData.authors)
            .join(MaterialsDataset.material_records)
            .filter(or_(*filters))
            .filter(DSMetaData.dataset_doi.isnot(None))  # Exclude datasets with empty dataset_doi
        )

        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        if tags:
            tag_filters = [DSMetaData.tags.ilike(f"%{tag}%") for tag in tags]
            datasets = datasets.filter(or_(*tag_filters))

        # Order by created_at
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        else:
            datasets = datasets.order_by(self.model.created_at.desc())

        return datasets.all()
