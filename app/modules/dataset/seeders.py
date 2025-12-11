import csv
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from app.modules.auth.models import User
from app.modules.dataset.models import (
    Author,
    DataSource,
    DSDownloadRecord,
    DSMetaData,
    DSMetrics,
    DSViewRecord,
    MaterialRecord,
    MaterialsDataset,
    PublicationType,
)
from core.seeders.BaseSeeder import BaseSeeder


class DataSetSeeder(BaseSeeder):

    priority = 2  # Lower priority

    def _create_dataset_versions(self, datasets, user1, user2):
        """Create creative versions for datasets with different types of changes"""
        from app import db
        from app.modules.dataset.routes import create_version_snapshot, regenerate_csv_for_dataset

        # Version 1: Dataset 0 (Ceramic Oxides) - Add new records
        dataset = datasets[0]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")

        # Create initial version
        create_version_snapshot(dataset.id, user1.id, "Initial dataset creation")

        # Add 2 new records
        new_records = [
            MaterialRecord(
                materials_dataset_id=dataset.id,
                material_name="Silicon Dioxide",
                chemical_formula="SiO2",
                structure_type="Amorphous",
                composition_method="Melting",
                property_name="thermal_expansion",
                property_value=0.55,
                property_unit="10^-6/K",
                temperature=298,
                pressure=101325,
                data_source=DataSource.EXPERIMENTAL,
                uncertainty=0.05,
                description="Fused silica low expansion",
            ),
            MaterialRecord(
                materials_dataset_id=dataset.id,
                material_name="Magnesia",
                chemical_formula="MgO",
                structure_type="Cubic",
                composition_method="Sintering",
                property_name="melting_point",
                property_value=2852,
                property_unit="°C",
                temperature=None,
                pressure=101325,
                data_source=DataSource.LITERATURE,
                uncertainty=10,
                description="Refractory oxide",
            ),
        ]
        self.seed(new_records)
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user1.id, "Added 2 new oxide materials")

        # Version 2: Dataset 1 (Carbides) - Modify title and description
        dataset = datasets[1]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user2.id, "Initial dataset creation")

        dataset.ds_meta_data.title = "Ultra-Hard Carbides and Nitrides Database"
        dataset.ds_meta_data.description = (
            "Comprehensive mechanical and thermal properties of ultra-hard carbides and nitrides "
            "for extreme environment applications including cutting tools and protective coatings"
        )
        db.session.commit()
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user2.id, "Enhanced title and description for clarity")

        # Version 3: Dataset 2 (Metallic Alloys) - Delete a record
        dataset = datasets[2]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user1.id, "Initial dataset creation")

        # Delete one record (Aluminum 6061)
        record_to_delete = MaterialRecord.query.filter_by(
            materials_dataset_id=dataset.id, material_name="Aluminum 6061"
        ).first()
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user1.id, "Removed outdated aluminum alloy data")

        # Version 4: Dataset 3 (Semiconductors) - Modify values and add record
        dataset = datasets[3]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user2.id, "Initial dataset creation")

        # Update Silicon bandgap value
        silicon_record = MaterialRecord.query.filter_by(
            materials_dataset_id=dataset.id, material_name="Silicon"
        ).first()
        if silicon_record:
            silicon_record.property_value = 1.14  # Updated value
            silicon_record.description = "Indirect bandgap - revised measurement"
            silicon_record.uncertainty = 0.005
            db.session.commit()

        # Add new semiconductor
        new_record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name="Indium Phosphide",
            chemical_formula="InP",
            structure_type="Zinc Blende",
            composition_method="Czochralski",
            property_name="bandgap",
            property_value=1.35,
            property_unit="eV",
            temperature=298,
            pressure=101325,
            data_source=DataSource.EXPERIMENTAL,
            uncertainty=0.02,
            description="Direct bandgap semiconductor",
        )
        self.seed([new_record])
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user2.id, "Updated Silicon bandgap and added InP data")

        # Version 5: Dataset 4 (2D Materials) - Major update with title change and records
        dataset = datasets[4]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user1.id, "Initial dataset creation")

        dataset.ds_meta_data.title = "2D Materials & van der Waals Heterostructures"
        dataset.ds_meta_data.description = (
            "Mechanical, electronic, and optical properties of graphene, TMDs, "
            "and van der Waals heterostructures for next-generation electronics"
        )
        dataset.ds_meta_data.tags = "2D materials, graphene, TMD, heterostructures, electronic"
        db.session.commit()

        # Add new 2D material
        new_record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name="WSe2",
            chemical_formula="WSe2",
            structure_type="2D Hexagonal",
            composition_method="CVD",
            property_name="bandgap",
            property_value=1.65,
            property_unit="eV",
            temperature=298,
            pressure=101325,
            data_source=DataSource.EXPERIMENTAL,
            uncertainty=0.08,
            description="p-type TMD semiconductor",
        )
        self.seed([new_record])
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user1.id, "Expanded scope to include heterostructures and added WSe2")

        # Version 6: Dataset 7 (High Entropy Alloys) - Multiple changes
        dataset = datasets[7]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user2.id, "Initial dataset creation")

        # Update description
        dataset.ds_meta_data.description = (
            "Mechanical properties and phase stability of high entropy alloys "
            "across temperature ranges from cryogenic to high temperature"
        )
        db.session.commit()

        # Modify a record
        hea_record = MaterialRecord.query.filter_by(materials_dataset_id=dataset.id, material_name="AlCoCrFeNi").first()
        if hea_record:
            hea_record.property_value = 5.5  # Updated hardness
            hea_record.description = "High hardness HEA - after annealing"
            db.session.commit()

        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(
            dataset.id, user2.id, "Updated description and revised AlCoCrFeNi hardness after heat treatment"
        )

        # Add another version with new data
        new_record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name="TiZrNbHfTa",
            chemical_formula="TiZrNbHfTa",
            structure_type="BCC",
            composition_method="Arc Melting",
            property_name="density",
            property_value=10.2,
            property_unit="g/cm³",
            temperature=298,
            pressure=101325,
            data_source=DataSource.EXPERIMENTAL,
            uncertainty=0.1,
            description="Refractory HEA composition",
        )
        self.seed([new_record])
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user2.id, "Added refractory HEA composition")

        # Version 7: Dataset 10 (Battery Materials) - Comprehensive update
        dataset = datasets[10]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user1.id, "Initial dataset creation")

        dataset.ds_meta_data.title = "Next-Generation Battery Materials Database"
        dataset.ds_meta_data.description = (
            "Electrochemical properties of cathode, anode, and solid electrolyte materials "
            "for lithium-ion, sodium-ion, and solid-state batteries"
        )
        dataset.ds_meta_data.tags = "battery, electrochemical, energy storage, cathode, anode, solid-state"
        db.session.commit()

        # Delete one record (LiCoO2)
        record_to_delete = MaterialRecord.query.filter_by(
            materials_dataset_id=dataset.id, material_name="LiCoO2"
        ).first()
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()

        # Add two new materials
        new_records = [
            MaterialRecord(
                materials_dataset_id=dataset.id,
                material_name="LiNi0.8Co0.1Mn0.1O2",
                chemical_formula="LiNi0.8Co0.1Mn0.1O2",
                structure_type="Layered",
                composition_method="Co-precipitation",
                property_name="specific_capacity",
                property_value=200,
                property_unit="mAh/g",
                temperature=298,
                pressure=101325,
                data_source=DataSource.EXPERIMENTAL,
                uncertainty=10,
                description="High nickel cathode NMC811",
            ),
            MaterialRecord(
                materials_dataset_id=dataset.id,
                material_name="LLZO",
                chemical_formula="Li7La3Zr2O12",
                structure_type="Garnet",
                composition_method="Solid State",
                property_name="ionic_conductivity",
                property_value=0.5,
                property_unit="mS/cm",
                temperature=298,
                pressure=101325,
                data_source=DataSource.LITERATURE,
                uncertainty=0.05,
                description="Solid electrolyte",
            ),
        ]
        self.seed(new_records)
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user1.id, "Replaced legacy LiCoO2 with NMC811 and added solid electrolyte")

        # Version 8: Dataset 17 (Perovskite) - Fix data errors
        dataset = datasets[17]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user2.id, "Initial dataset creation")

        # Update all records with corrected temperature
        perovskite_records = MaterialRecord.query.filter_by(materials_dataset_id=dataset.id).all()
        for record in perovskite_records:
            record.temperature = 300  # Corrected temperature
        db.session.commit()

        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user2.id, "Corrected temperature measurements (298K -> 300K)")

        # Another version with title refinement
        dataset.ds_meta_data.title = "Halide Perovskite Materials for Photovoltaics"
        db.session.commit()
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user2.id, "Refined title to specify halide perovskites")

        # Version 9: Dataset 19 (Thermal Barrier Coatings) - Delete and modify
        dataset = datasets[19]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user1.id, "Initial dataset creation")

        # Delete a record
        record_to_delete = MaterialRecord.query.filter_by(
            materials_dataset_id=dataset.id, material_name="YSZ", composition_method="EB-PVD"
        ).first()
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()

        # Modify remaining YSZ record
        ysz_record = MaterialRecord.query.filter_by(
            materials_dataset_id=dataset.id, material_name="YSZ", composition_method="APS"
        ).first()
        if ysz_record:
            ysz_record.property_value = 2.1  # Updated thermal conductivity
            ysz_record.uncertainty = 0.15
            ysz_record.description = "Standard TBC - revised measurement"
            db.session.commit()

        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user1.id, "Removed EB-PVD data and updated APS thermal conductivity")

        # Version 10: Dataset 5 (Polymers) - Add new polymers
        dataset = datasets[5]
        print(f"  - Creating versions for {dataset.ds_meta_data.title}...")
        create_version_snapshot(dataset.id, user1.id, "Initial dataset creation")

        new_records = [
            MaterialRecord(
                materials_dataset_id=dataset.id,
                material_name="PLA",
                chemical_formula="(C3H4O2)n",
                structure_type="Semi-crystalline",
                composition_method="Extrusion",
                property_name="glass_transition",
                property_value=60,
                property_unit="°C",
                temperature=None,
                pressure=101325,
                data_source=DataSource.LITERATURE,
                uncertainty=3,
                description="Biodegradable polymer",
            ),
            MaterialRecord(
                materials_dataset_id=dataset.id,
                material_name="PTFE",
                chemical_formula="(C2F4)n",
                structure_type="Semi-crystalline",
                composition_method="Suspension",
                property_name="melting_point",
                property_value=327,
                property_unit="°C",
                temperature=None,
                pressure=101325,
                data_source=DataSource.DATABASE,
                uncertainty=2,
                description="Teflon fluoropolymer",
            ),
        ]
        self.seed(new_records)
        regenerate_csv_for_dataset(dataset.id)
        create_version_snapshot(dataset.id, user1.id, "Added biodegradable and fluoropolymer materials")

        print("  ✓ Dataset versions created successfully!")

    def run(self):
        # Retrieve users
        user1 = User.query.filter_by(email="user1@example.com").first()
        user2 = User.query.filter_by(email="user2@example.com").first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        # Create DSMetrics instance
        ds_metrics = DSMetrics(number_of_models="5", number_of_features="50")
        seeded_ds_metrics = self.seed([ds_metrics])[0]

        # Create MaterialsDataset instances - 20 datasets
        materials_dataset_info = [
            (
                "Ceramic Oxides Properties Database",
                "Comprehensive thermophysical properties for ceramic oxides including alumina, zirconia, and titania",
                "ceramics, oxides, thermal, mechanical",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Advanced Carbides and Nitrides",
                "Mechanical and thermal properties of carbides and nitrides for high-temperature applications",
                "carbides, nitrides, high-temperature, mechanical",
                PublicationType.DATA_MANAGEMENT_PLAN,
            ),
            (
                "Metallic Alloys Thermal Properties",
                "Thermal conductivity and expansion data for engineering alloys",
                "metals, alloys, thermal, conductivity",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Semiconductor Materials Database",
                "Electronic and optical properties of semiconductor materials",
                "semiconductors, electronic, optical, bandgap",
                PublicationType.CONFERENCE_PAPER,
            ),
            (
                "2D Materials Properties",
                "Mechanical and electronic properties of graphene and other 2D materials",
                "2D materials, graphene, electronic, mechanical",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Polymer Materials Database",
                "Mechanical and thermal properties of engineering polymers",
                "polymers, mechanical, thermal, engineering",
                PublicationType.DATA_MANAGEMENT_PLAN,
            ),
            (
                "Composite Materials Properties",
                "Properties of fiber-reinforced and particulate composites",
                "composites, reinforced, mechanical, structural",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "High Entropy Alloys Database",
                "Mechanical properties of high entropy alloys at various temperatures",
                "HEA, alloys, mechanical, temperature",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Piezoelectric Materials",
                "Piezoelectric coefficients and properties for sensor applications",
                "piezoelectric, sensors, electronic, ceramic",
                PublicationType.CONFERENCE_PAPER,
            ),
            (
                "Thermoelectric Materials",
                "Thermoelectric properties for energy conversion applications",
                "thermoelectric, energy, conversion, ZT",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Battery Materials Database",
                "Electrochemical properties of cathode and anode materials",
                "battery, electrochemical, energy storage, cathode",
                PublicationType.DATA_MANAGEMENT_PLAN,
            ),
            (
                "Optical Materials Properties",
                "Refractive indices and optical properties of transparent materials",
                "optical, refractive index, transparent, glass",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Magnetic Materials Database",
                "Magnetic properties of ferromagnetic and ferrimagnetic materials",
                "magnetic, ferromagnetic, saturation, coercivity",
                PublicationType.CONFERENCE_PAPER,
            ),
            (
                "Biomaterials Properties",
                "Biocompatible materials for medical implants and devices",
                "biomaterials, biocompatible, medical, implants",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Superconductor Materials",
                "Critical temperature and properties of superconducting materials",
                "superconductor, critical temperature, magnetic, oxide",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Refractory Metals Database",
                "High-temperature properties of refractory metals and alloys",
                "refractory, metals, high-temperature, tungsten",
                PublicationType.DATA_MANAGEMENT_PLAN,
            ),
            (
                "Nanomaterials Properties",
                "Size-dependent properties of nanoparticles and nanostructures",
                "nanomaterials, nanoparticles, size-dependent, quantum",
                PublicationType.CONFERENCE_PAPER,
            ),
            (
                "Perovskite Materials Database",
                "Electronic and optical properties of perovskite materials",
                "perovskite, photovoltaic, electronic, optical",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Shape Memory Alloys",
                "Transformation temperatures and mechanical properties of SMAs",
                "SMA, shape memory, transformation, NiTi",
                PublicationType.JOURNAL_ARTICLE,
            ),
            (
                "Thermal Barrier Coatings",
                "Thermal and mechanical properties of TBC materials",
                "TBC, coatings, thermal barrier, YSZ",
                PublicationType.DATA_MANAGEMENT_PLAN,
            ),
        ]

        materials_ds_meta_data_list = [
            DSMetaData(
                deposition_id=100 + i,
                title=info[0],
                description=info[1],
                publication_type=info[3],
                publication_doi=f"10.1234/materials{i+1:02d}",
                dataset_doi=f"10.1234/materials-ds{i+1:02d}",
                tags=info[2],
                ds_metrics_id=seeded_ds_metrics.id,
            )
            for i, info in enumerate(materials_dataset_info)
        ]
        seeded_materials_meta_data = self.seed(materials_ds_meta_data_list)

        # Create Author instances for MaterialsDataset - 20 authors
        author_names = [
            ("Dr. Maria Garcia", "Materials Science Institute"),
            ("Prof. John Smith", "Advanced Materials Lab"),
            ("Dr. Li Wei", "Nanotech Research Center"),
            ("Prof. Sarah Johnson", "Institute of Ceramics"),
            ("Dr. Ahmed Hassan", "Semiconductor Research Lab"),
            ("Prof. Elena Volkov", "2D Materials Center"),
            ("Dr. Carlos Mendez", "Polymer Science Institute"),
            ("Prof. Yuki Tanaka", "Composite Materials Lab"),
            ("Dr. Priya Sharma", "High Entropy Alloys Group"),
            ("Prof. Hans Mueller", "Piezoelectric Materials Lab"),
            ("Dr. Grace Kim", "Thermoelectric Research Center"),
            ("Prof. Marco Rossi", "Energy Storage Materials Lab"),
            ("Dr. Anna Kowalski", "Optical Materials Institute"),
            ("Prof. David Chen", "Magnetic Materials Center"),
            ("Dr. Fatima Al-Rashid", "Biomaterials Research Group"),
            ("Prof. Björn Andersson", "Superconductor Lab"),
            ("Dr. Isabella Ferrari", "Refractory Materials Institute"),
            ("Prof. Raj Patel", "Nanomaterials Research Center"),
            ("Dr. Sophie Laurent", "Perovskite Materials Lab"),
            ("Prof. Michael O'Brien", "Smart Materials Institute"),
        ]

        materials_authors = [
            Author(
                name=author_names[i][0],
                affiliation=author_names[i][1],
                orcid=f"0000-000{(i+1)//10}-{(i+1) % 10:04d}-{6789+i:04d}",
                ds_meta_data_id=seeded_materials_meta_data[i].id,
            )
            for i in range(20)
        ]
        self.seed(materials_authors)

        # Create MaterialsDataset instances - 20 datasets alternating between user1 and user2
        # csv_file_path will be set after generating CSV files
        materials_datasets = [
            MaterialsDataset(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=seeded_materials_meta_data[i].id,
                csv_file_path=None,
                created_at=datetime.now(timezone.utc),
            )
            for i in range(20)
        ]
        seeded_materials_datasets = self.seed(materials_datasets)

        # Create MaterialRecord instances for all 20 MaterialsDatasets
        # Data structure: (material_name, chemical_formula, structure_type, composition_method,
        #                  property_name, property_value, property_unit, temperature, pressure,
        #                  data_source, uncertainty, description)

        materials_records_data = [
            # Dataset 0: Ceramic Oxides
            [
                (
                    "Alumina",
                    "Al2O3",
                    "Corundum",
                    "Sintering",
                    "density",
                    3.95,
                    "g/cm³",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.02,
                    "High-purity alumina ceramic",
                ),
                (
                    "Alumina",
                    "Al2O3",
                    "Corundum",
                    "Sintering",
                    "hardness",
                    9.0,
                    "Mohs",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    None,
                    "Mohs hardness scale",
                ),
                (
                    "Zirconia",
                    "ZrO2",
                    "Cubic",
                    "Sintering",
                    "fracture_toughness",
                    10.0,
                    "MPa·m^0.5",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.5,
                    "YSZ toughness",
                ),
                (
                    "Titanium Dioxide",
                    "TiO2",
                    "Rutile",
                    "Sol-gel",
                    "density",
                    4.23,
                    "g/cm³",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.03,
                    "Rutile phase",
                ),
            ],
            # Dataset 1: Carbides and Nitrides
            [
                (
                    "Silicon Carbide",
                    "SiC",
                    "Hexagonal",
                    "Hot Pressing",
                    "youngs_modulus",
                    410,
                    "GPa",
                    298,
                    101325,
                    DataSource.COMPUTATIONAL,
                    10,
                    "DFT calculation",
                ),
                (
                    "Silicon Carbide",
                    "SiC",
                    "Hexagonal",
                    "Hot Pressing",
                    "hardness",
                    28,
                    "GPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    2,
                    "Vickers hardness",
                ),
                (
                    "Boron Carbide",
                    "B4C",
                    "Rhombohedral",
                    "Reaction Bonding",
                    "hardness",
                    38,
                    "GPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    2,
                    "Very hard ceramic",
                ),
                (
                    "Aluminium Nitride",
                    "AlN",
                    "Wurtzite",
                    "Sintering",
                    "thermal_conductivity",
                    180,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    10,
                    "High thermal conductivity",
                ),
                (
                    "Titanium Nitride",
                    "TiN",
                    "Cubic",
                    "PVD",
                    "hardness",
                    21,
                    "GPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    1.5,
                    "Hard coating material",
                ),
            ],
            # Dataset 2: Metallic Alloys
            [
                (
                    "Steel 304",
                    "Fe-Cr-Ni",
                    "FCC",
                    "Casting",
                    "thermal_conductivity",
                    16.2,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.DATABASE,
                    None,
                    "Stainless steel",
                ),
                (
                    "Aluminum 6061",
                    "Al-Mg-Si",
                    "FCC",
                    "Extrusion",
                    "thermal_expansion",
                    23.6,
                    "10^-6/K",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.5,
                    "Engineering alloy",
                ),
                (
                    "Copper",
                    "Cu",
                    "FCC",
                    "Casting",
                    "thermal_conductivity",
                    401,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.DATABASE,
                    None,
                    "Pure copper",
                ),
                (
                    "Titanium Ti-6Al-4V",
                    "Ti-Al-V",
                    "HCP+BCC",
                    "Forging",
                    "density",
                    4.43,
                    "g/cm³",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.01,
                    "Aerospace alloy",
                ),
            ],
            # Dataset 3: Semiconductors
            [
                (
                    "Silicon",
                    "Si",
                    "Diamond Cubic",
                    "Czochralski",
                    "bandgap",
                    1.12,
                    "eV",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.01,
                    "Indirect bandgap",
                ),
                (
                    "Gallium Arsenide",
                    "GaAs",
                    "Zinc Blende",
                    "MBE",
                    "bandgap",
                    1.42,
                    "eV",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.02,
                    "Direct bandgap",
                ),
                (
                    "Silicon Carbide",
                    "SiC",
                    "Hexagonal",
                    "CVD",
                    "bandgap",
                    3.26,
                    "eV",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.05,
                    "Wide bandgap",
                ),
                (
                    "Gallium Nitride",
                    "GaN",
                    "Wurtzite",
                    "MOCVD",
                    "bandgap",
                    3.4,
                    "eV",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.03,
                    "Wide bandgap semiconductor",
                ),
            ],
            # Dataset 4: 2D Materials
            [
                (
                    "Graphene",
                    "C",
                    "2D Hexagonal",
                    "CVD",
                    "youngs_modulus",
                    1000,
                    "GPa",
                    298,
                    101325,
                    DataSource.COMPUTATIONAL,
                    50,
                    "Monolayer graphene",
                ),
                (
                    "Graphene",
                    "C",
                    "2D Hexagonal",
                    "CVD",
                    "thermal_conductivity",
                    5000,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.COMPUTATIONAL,
                    500,
                    "In-plane conductivity",
                ),
                (
                    "MoS2",
                    "MoS2",
                    "2D Hexagonal",
                    "Exfoliation",
                    "bandgap",
                    1.8,
                    "eV",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.1,
                    "Monolayer TMD",
                ),
                (
                    "h-BN",
                    "BN",
                    "2D Hexagonal",
                    "CVD",
                    "bandgap",
                    5.9,
                    "eV",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.2,
                    "Hexagonal boron nitride",
                ),
            ],
            # Dataset 5: Polymers
            [
                (
                    "Polyethylene",
                    "(C2H4)n",
                    "Semi-crystalline",
                    "Extrusion",
                    "density",
                    0.95,
                    "g/cm³",
                    298,
                    101325,
                    DataSource.DATABASE,
                    0.01,
                    "HDPE",
                ),
                (
                    "Polypropylene",
                    "(C3H6)n",
                    "Semi-crystalline",
                    "Injection Molding",
                    "melting_point",
                    160,
                    "°C",
                    None,
                    101325,
                    DataSource.LITERATURE,
                    5,
                    "PP thermoplastic",
                ),
                (
                    "PEEK",
                    "C19H12O3",
                    "Semi-crystalline",
                    "Extrusion",
                    "tensile_strength",
                    100,
                    "MPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    5,
                    "High performance polymer",
                ),
                (
                    "Nylon 6",
                    "(C6H11NO)n",
                    "Semi-crystalline",
                    "Casting",
                    "youngs_modulus",
                    2.85,
                    "GPa",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.2,
                    "Polyamide",
                ),
            ],
            # Dataset 6: Composites
            [
                (
                    "Carbon Fiber Composite",
                    "C-Epoxy",
                    "Laminate",
                    "Autoclave",
                    "tensile_strength",
                    600,
                    "MPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    30,
                    "CFRP unidirectional",
                ),
                (
                    "Glass Fiber Composite",
                    "SiO2-Epoxy",
                    "Laminate",
                    "Hand Layup",
                    "tensile_strength",
                    400,
                    "MPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    20,
                    "GFRP",
                ),
                (
                    "Ceramic Matrix Composite",
                    "SiC-SiC",
                    "Fiber Reinforced",
                    "CVI",
                    "fracture_toughness",
                    25,
                    "MPa·m^0.5",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    3,
                    "CMC high temperature",
                ),
            ],
            # Dataset 7: High Entropy Alloys
            [
                (
                    "CoCrFeNi",
                    "CoCrFeNi",
                    "FCC",
                    "Arc Melting",
                    "hardness",
                    2.5,
                    "GPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.2,
                    "Cantor alloy",
                ),
                (
                    "CoCrFeNi",
                    "CoCrFeNi",
                    "FCC",
                    "Arc Melting",
                    "youngs_modulus",
                    200,
                    "GPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    10,
                    "Room temperature",
                ),
                (
                    "AlCoCrFeNi",
                    "AlCoCrFeNi",
                    "BCC",
                    "Arc Melting",
                    "hardness",
                    5.2,
                    "GPa",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.3,
                    "High hardness HEA",
                ),
                (
                    "CoCrFeMnNi",
                    "CoCrFeMnNi",
                    "FCC",
                    "Arc Melting",
                    "fracture_toughness",
                    200,
                    "MPa·m^0.5",
                    77,
                    101325,
                    DataSource.EXPERIMENTAL,
                    15,
                    "Cryogenic properties",
                ),
            ],
            # Dataset 8: Piezoelectric Materials
            [
                (
                    "PZT",
                    "Pb(Zr,Ti)O3",
                    "Perovskite",
                    "Sintering",
                    "piezo_coefficient",
                    300,
                    "pC/N",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    15,
                    "d33 coefficient",
                ),
                (
                    "Quartz",
                    "SiO2",
                    "Trigonal",
                    "Natural",
                    "piezo_coefficient",
                    2.3,
                    "pC/N",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.1,
                    "d11 coefficient",
                ),
                (
                    "BaTiO3",
                    "BaTiO3",
                    "Perovskite",
                    "Sintering",
                    "dielectric_constant",
                    1700,
                    "dimensionless",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    100,
                    "Relative permittivity",
                ),
            ],
            # Dataset 9: Thermoelectric Materials
            [
                (
                    "Bismuth Telluride",
                    "Bi2Te3",
                    "Rhombohedral",
                    "Zone Melting",
                    "ZT",
                    1.0,
                    "dimensionless",
                    300,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.1,
                    "Figure of merit",
                ),
                (
                    "Lead Telluride",
                    "PbTe",
                    "Cubic",
                    "Melting",
                    "ZT",
                    1.5,
                    "dimensionless",
                    700,
                    101325,
                    DataSource.LITERATURE,
                    0.15,
                    "High temperature",
                ),
                (
                    "Silicon Germanium",
                    "SiGe",
                    "Diamond Cubic",
                    "Alloying",
                    "ZT",
                    0.8,
                    "dimensionless",
                    1000,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.1,
                    "Very high temperature",
                ),
            ],
            # Dataset 10: Battery Materials
            [
                (
                    "LiCoO2",
                    "LiCoO2",
                    "Layered",
                    "Sol-gel",
                    "specific_capacity",
                    140,
                    "mAh/g",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    5,
                    "Cathode material",
                ),
                (
                    "LiFePO4",
                    "LiFePO4",
                    "Olivine",
                    "Hydrothermal",
                    "specific_capacity",
                    160,
                    "mAh/g",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    8,
                    "Safer cathode",
                ),
                (
                    "Graphite",
                    "C",
                    "Layered",
                    "Natural",
                    "specific_capacity",
                    372,
                    "mAh/g",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    10,
                    "Anode material",
                ),
                (
                    "NMC",
                    "LiNi0.33Mn0.33Co0.33O2",
                    "Layered",
                    "Co-precipitation",
                    "specific_capacity",
                    165,
                    "mAh/g",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    7,
                    "High energy cathode",
                ),
            ],
            # Dataset 11: Optical Materials
            [
                (
                    "Fused Silica",
                    "SiO2",
                    "Amorphous",
                    "Melting",
                    "refractive_index",
                    1.46,
                    "dimensionless",
                    298,
                    101325,
                    DataSource.DATABASE,
                    0.001,
                    "At 589 nm",
                ),
                (
                    "Sapphire",
                    "Al2O3",
                    "Corundum",
                    "Czochralski",
                    "refractive_index",
                    1.77,
                    "dimensionless",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.01,
                    "Ordinary ray",
                ),
                (
                    "BK7 Glass",
                    "Borosilicate",
                    "Amorphous",
                    "Melting",
                    "refractive_index",
                    1.52,
                    "dimensionless",
                    298,
                    101325,
                    DataSource.DATABASE,
                    0.002,
                    "Standard optical glass",
                ),
            ],
            # Dataset 12: Magnetic Materials
            [
                (
                    "Iron",
                    "Fe",
                    "BCC",
                    "Melting",
                    "saturation_magnetization",
                    1707,
                    "emu/cm³",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    10,
                    "Ferromagnetic",
                ),
                (
                    "NdFeB",
                    "Nd2Fe14B",
                    "Tetragonal",
                    "Sintering",
                    "coercivity",
                    12000,
                    "Oe",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    500,
                    "Permanent magnet",
                ),
                (
                    "Ferrite",
                    "Fe3O4",
                    "Cubic",
                    "Ceramic",
                    "saturation_magnetization",
                    480,
                    "emu/cm³",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    20,
                    "Soft magnetic",
                ),
            ],
            # Dataset 13: Biomaterials
            [
                (
                    "Titanium",
                    "Ti",
                    "HCP",
                    "Machining",
                    "biocompatibility",
                    5,
                    "scale",
                    310,
                    101325,
                    DataSource.EXPERIMENTAL,
                    None,
                    "Excellent for implants",
                ),
                (
                    "Hydroxyapatite",
                    "Ca10(PO4)6(OH)2",
                    "Hexagonal",
                    "Precipitation",
                    "bioactivity",
                    8,
                    "scale",
                    310,
                    101325,
                    DataSource.EXPERIMENTAL,
                    None,
                    "Bone substitute",
                ),
                (
                    "PEEK",
                    "C19H12O3",
                    "Semi-crystalline",
                    "Extrusion",
                    "biocompatibility",
                    4,
                    "scale",
                    310,
                    101325,
                    DataSource.LITERATURE,
                    None,
                    "Polymer implant",
                ),
            ],
            # Dataset 14: Superconductors
            [
                (
                    "YBCO",
                    "YBa2Cu3O7",
                    "Orthorhombic",
                    "Solid State",
                    "critical_temperature",
                    92,
                    "K",
                    None,
                    101325,
                    DataSource.LITERATURE,
                    1,
                    "High-Tc superconductor",
                ),
                (
                    "NbTi",
                    "NbTi",
                    "BCC",
                    "Alloying",
                    "critical_temperature",
                    9.5,
                    "K",
                    None,
                    101325,
                    DataSource.DATABASE,
                    0.2,
                    "Type-II superconductor",
                ),
                (
                    "MgB2",
                    "MgB2",
                    "Hexagonal",
                    "Reaction",
                    "critical_temperature",
                    39,
                    "K",
                    None,
                    101325,
                    DataSource.LITERATURE,
                    1,
                    "Intermediate Tc",
                ),
            ],
            # Dataset 15: Refractory Metals
            [
                (
                    "Tungsten",
                    "W",
                    "BCC",
                    "Powder Metallurgy",
                    "melting_point",
                    3422,
                    "°C",
                    None,
                    101325,
                    DataSource.LITERATURE,
                    10,
                    "Highest melting point",
                ),
                (
                    "Molybdenum",
                    "Mo",
                    "BCC",
                    "Arc Melting",
                    "thermal_conductivity",
                    138,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.DATABASE,
                    5,
                    "High temperature",
                ),
                (
                    "Tantalum",
                    "Ta",
                    "BCC",
                    "Electron Beam Melting",
                    "melting_point",
                    3017,
                    "°C",
                    None,
                    101325,
                    DataSource.LITERATURE,
                    20,
                    "Corrosion resistant",
                ),
            ],
            # Dataset 16: Nanomaterials
            [
                (
                    "Gold Nanoparticles",
                    "Au",
                    "FCC",
                    "Chemical Reduction",
                    "particle_size",
                    20,
                    "nm",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    2,
                    "Spherical nanoparticles",
                ),
                (
                    "Carbon Nanotubes",
                    "C",
                    "Tubular",
                    "CVD",
                    "diameter",
                    1.5,
                    "nm",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.2,
                    "Single-walled CNT",
                ),
                (
                    "ZnO Nanowires",
                    "ZnO",
                    "Wurtzite",
                    "Hydrothermal",
                    "diameter",
                    50,
                    "nm",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    5,
                    "Nanowire array",
                ),
            ],
            # Dataset 17: Perovskite Materials
            [
                (
                    "MAPI",
                    "CH3NH3PbI3",
                    "Perovskite",
                    "Solution Processing",
                    "bandgap",
                    1.55,
                    "eV",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.02,
                    "Photovoltaic material",
                ),
                (
                    "CsPbBr3",
                    "CsPbBr3",
                    "Perovskite",
                    "Hot Injection",
                    "bandgap",
                    2.3,
                    "eV",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.05,
                    "LED material",
                ),
                (
                    "FAPbI3",
                    "HC(NH2)2PbI3",
                    "Perovskite",
                    "Solution Processing",
                    "bandgap",
                    1.48,
                    "eV",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.03,
                    "Stable perovskite",
                ),
            ],
            # Dataset 18: Shape Memory Alloys
            [
                (
                    "Nitinol",
                    "NiTi",
                    "B2/B19'",
                    "Arc Melting",
                    "transformation_temp",
                    50,
                    "°C",
                    None,
                    101325,
                    DataSource.EXPERIMENTAL,
                    3,
                    "Austenite finish",
                ),
                (
                    "Nitinol",
                    "NiTi",
                    "B2/B19'",
                    "Arc Melting",
                    "superelasticity",
                    8,
                    "%",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.5,
                    "Recoverable strain",
                ),
                (
                    "CuAlNi",
                    "Cu-Al-Ni",
                    "Beta Phase",
                    "Casting",
                    "transformation_temp",
                    80,
                    "°C",
                    None,
                    101325,
                    DataSource.LITERATURE,
                    5,
                    "Higher temperature SMA",
                ),
            ],
            # Dataset 19: Thermal Barrier Coatings
            [
                (
                    "YSZ",
                    "Y2O3-ZrO2",
                    "Tetragonal",
                    "APS",
                    "thermal_conductivity",
                    2.3,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    0.2,
                    "Standard TBC",
                ),
                (
                    "YSZ",
                    "Y2O3-ZrO2",
                    "Tetragonal",
                    "EB-PVD",
                    "porosity",
                    15,
                    "%",
                    298,
                    101325,
                    DataSource.EXPERIMENTAL,
                    2,
                    "Columnar structure",
                ),
                (
                    "Gadolinium Zirconate",
                    "Gd2Zr2O7",
                    "Pyrochlore",
                    "APS",
                    "thermal_conductivity",
                    1.6,
                    "W/(m·K)",
                    298,
                    101325,
                    DataSource.LITERATURE,
                    0.15,
                    "Low conductivity TBC",
                ),
            ],
        ]

        # Seed all material records
        all_records = []
        for i, dataset_records in enumerate(materials_records_data):
            for record_data in dataset_records:
                record = MaterialRecord(
                    materials_dataset_id=seeded_materials_datasets[i].id,
                    material_name=record_data[0],
                    chemical_formula=record_data[1],
                    structure_type=record_data[2],
                    composition_method=record_data[3],
                    property_name=record_data[4],
                    property_value=record_data[5],
                    property_unit=record_data[6],
                    temperature=record_data[7],
                    pressure=record_data[8],
                    data_source=record_data[9],
                    uncertainty=record_data[10],
                    description=record_data[11],
                )
                all_records.append(record)

        self.seed(all_records)

        # Generate CSV files for each MaterialsDataset
        csv_dir = "uploads/materials_csv"
        os.makedirs(csv_dir, exist_ok=True)

        for i, dataset in enumerate(seeded_materials_datasets):
            csv_filename = f"materials_dataset_{i+1}.csv"
            csv_path = os.path.join(csv_dir, csv_filename)

            # Get records for this dataset
            dataset_records = materials_records_data[i]

            # Write CSV file
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "material_name",
                    "chemical_formula",
                    "structure_type",
                    "composition_method",
                    "property_name",
                    "property_value",
                    "property_unit",
                    "temperature",
                    "pressure",
                    "data_source",
                    "uncertainty",
                    "description",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for record_data in dataset_records:
                    writer.writerow(
                        {
                            "material_name": record_data[0],
                            "chemical_formula": record_data[1],
                            "structure_type": record_data[2],
                            "composition_method": record_data[3],
                            "property_name": record_data[4],
                            "property_value": record_data[5],
                            "property_unit": record_data[6],
                            "temperature": record_data[7],
                            "pressure": record_data[8],
                            "data_source": record_data[9].value if record_data[9] else "",
                            "uncertainty": record_data[10] if record_data[10] is not None else "",
                            "description": record_data[11],
                        }
                    )

            # Update dataset csv_file_path
            dataset.csv_file_path = csv_path

        # Commit changes to database
        from app import db

        db.session.commit()

        # Generate random download and view records for each MaterialsDataset
        print("Generating random download and view records for MaterialsDatasets...")

        all_download_records = []
        all_view_records = []

        for dataset in seeded_materials_datasets:
            # Random number of downloads (between 5 and 50)
            num_downloads = random.randint(5, 50)

            # Generate downloads over the last 60 days
            for _ in range(num_downloads):
                days_ago = random.randint(0, 60)
                download_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

                download_record = DSDownloadRecord(
                    user_id=None if random.random() < 0.3 else random.choice([user1.id, user2.id]),
                    dataset_id=dataset.id,
                    download_date=download_date,
                    download_cookie=str(uuid.uuid4()),
                )
                all_download_records.append(download_record)

            # Random number of views (between 10 and 200)
            num_views = random.randint(10, 200)

            # Generate views over the last 60 days
            for _ in range(num_views):
                days_ago = random.randint(0, 60)
                view_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

                view_record = DSViewRecord(
                    user_id=None if random.random() < 0.3 else random.choice([user1.id, user2.id]),
                    dataset_id=dataset.id,
                    view_date=view_date,
                    view_cookie=str(uuid.uuid4()),
                )
                all_view_records.append(view_record)

        # Seed all download and view records
        self.seed(all_download_records)
        self.seed(all_view_records)

        print(
            f"Generated {len(all_download_records)} download records and "
            f"{len(all_view_records)} view records for MaterialsDatasets"
        )

        # Create versions for datasets with different types of changes
        print("Creating dataset versions with different changes...")
        self._create_dataset_versions(seeded_materials_datasets, user1, user2)
