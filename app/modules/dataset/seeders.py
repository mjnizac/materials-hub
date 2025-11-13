import os
import shutil
from datetime import datetime, timezone

from dotenv import load_dotenv

from app.modules.auth.models import User
from app.modules.dataset.models import (
    Author, DataSet, DSMetaData, DSMetrics, PublicationType,
    MaterialsDataset, MaterialRecord, DataSource
)
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from core.seeders.BaseSeeder import BaseSeeder


class DataSetSeeder(BaseSeeder):

    priority = 2  # Lower priority

    def run(self):
        # Retrieve users
        user1 = User.query.filter_by(email="user1@example.com").first()
        user2 = User.query.filter_by(email="user2@example.com").first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        # Create DSMetrics instance
        ds_metrics = DSMetrics(number_of_models="5", number_of_features="50")
        seeded_ds_metrics = self.seed([ds_metrics])[0]

        # Create DSMetaData instances
        ds_meta_data_list = [
            DSMetaData(
                deposition_id=1 + i,
                title=f"Sample dataset {i+1}",
                description=f"Description for dataset {i+1}",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
                publication_doi=f"10.1234/dataset{i+1}",
                dataset_doi=f"10.1234/dataset{i+1}",
                tags="tag1, tag2",
                ds_metrics_id=seeded_ds_metrics.id,
            )
            for i in range(4)
        ]
        seeded_ds_meta_data = self.seed(ds_meta_data_list)

        # Create Author instances and associate with DSMetaData
        authors = [
            Author(
                name=f"Author {i+1}",
                affiliation=f"Affiliation {i+1}",
                orcid=f"0000-0000-0000-000{i}",
                ds_meta_data_id=seeded_ds_meta_data[i % 4].id,
            )
            for i in range(4)
        ]
        self.seed(authors)

        # Create DataSet instances
        datasets = [
            DataSet(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=seeded_ds_meta_data[i].id,
                created_at=datetime.now(timezone.utc),
            )
            for i in range(4)
        ]
        seeded_datasets = self.seed(datasets)

        # Assume there are 12 UVL files, create corresponding FMMetaData and FeatureModel
        fm_meta_data_list = [
            FMMetaData(
                uvl_filename=f"file{i+1}.uvl",
                title=f"Feature Model {i+1}",
                description=f"Description for feature model {i+1}",
                publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
                publication_doi=f"10.1234/fm{i+1}",
                tags="tag1, tag2",
                uvl_version="1.0",
            )
            for i in range(12)
        ]
        seeded_fm_meta_data = self.seed(fm_meta_data_list)

        # Create Author instances and associate with FMMetaData
        fm_authors = [
            Author(
                name=f"Author {i+5}",
                affiliation=f"Affiliation {i+5}",
                orcid=f"0000-0000-0000-000{i+5}",
                fm_meta_data_id=seeded_fm_meta_data[i].id,
            )
            for i in range(12)
        ]
        self.seed(fm_authors)

        feature_models = [
            FeatureModel(data_set_id=seeded_datasets[i // 3].id, fm_meta_data_id=seeded_fm_meta_data[i].id)
            for i in range(12)
        ]
        seeded_feature_models = self.seed(feature_models)

        # Create files, associate them with FeatureModels and copy files
        load_dotenv()
        working_dir = os.getenv("WORKING_DIR", "")
        src_folder = os.path.join(working_dir, "app", "modules", "dataset", "uvl_examples")
        for i in range(12):
            file_name = f"file{i+1}.uvl"
            feature_model = seeded_feature_models[i]
            dataset = next(ds for ds in seeded_datasets if ds.id == feature_model.data_set_id)
            user_id = dataset.user_id

            dest_folder = os.path.join(working_dir, "uploads", f"user_{user_id}", f"dataset_{dataset.id}")
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy(os.path.join(src_folder, file_name), dest_folder)

            file_path = os.path.join(dest_folder, file_name)

            uvl_file = Hubfile(
                name=file_name,
                checksum=f"checksum{i+1}",
                size=os.path.getsize(file_path),
                feature_model_id=feature_model.id,
            )
            self.seed([uvl_file])

        # Create MaterialsDataset instances - 20 datasets
        materials_dataset_info = [
            ("Ceramic Oxides Properties Database", "Comprehensive thermophysical properties for ceramic oxides including alumina, zirconia, and titania", "ceramics, oxides, thermal, mechanical", PublicationType.JOURNAL_ARTICLE),
            ("Advanced Carbides and Nitrides", "Mechanical and thermal properties of carbides and nitrides for high-temperature applications", "carbides, nitrides, high-temperature, mechanical", PublicationType.DATA_MANAGEMENT_PLAN),
            ("Metallic Alloys Thermal Properties", "Thermal conductivity and expansion data for engineering alloys", "metals, alloys, thermal, conductivity", PublicationType.JOURNAL_ARTICLE),
            ("Semiconductor Materials Database", "Electronic and optical properties of semiconductor materials", "semiconductors, electronic, optical, bandgap", PublicationType.CONFERENCE_PAPER),
            ("2D Materials Properties", "Mechanical and electronic properties of graphene and other 2D materials", "2D materials, graphene, electronic, mechanical", PublicationType.JOURNAL_ARTICLE),
            ("Polymer Materials Database", "Mechanical and thermal properties of engineering polymers", "polymers, mechanical, thermal, engineering", PublicationType.DATA_MANAGEMENT_PLAN),
            ("Composite Materials Properties", "Properties of fiber-reinforced and particulate composites", "composites, reinforced, mechanical, structural", PublicationType.JOURNAL_ARTICLE),
            ("High Entropy Alloys Database", "Mechanical properties of high entropy alloys at various temperatures", "HEA, alloys, mechanical, temperature", PublicationType.JOURNAL_ARTICLE),
            ("Piezoelectric Materials", "Piezoelectric coefficients and properties for sensor applications", "piezoelectric, sensors, electronic, ceramic", PublicationType.CONFERENCE_PAPER),
            ("Thermoelectric Materials", "Thermoelectric properties for energy conversion applications", "thermoelectric, energy, conversion, ZT", PublicationType.JOURNAL_ARTICLE),
            ("Battery Materials Database", "Electrochemical properties of cathode and anode materials", "battery, electrochemical, energy storage, cathode", PublicationType.DATA_MANAGEMENT_PLAN),
            ("Optical Materials Properties", "Refractive indices and optical properties of transparent materials", "optical, refractive index, transparent, glass", PublicationType.JOURNAL_ARTICLE),
            ("Magnetic Materials Database", "Magnetic properties of ferromagnetic and ferrimagnetic materials", "magnetic, ferromagnetic, saturation, coercivity", PublicationType.CONFERENCE_PAPER),
            ("Biomaterials Properties", "Biocompatible materials for medical implants and devices", "biomaterials, biocompatible, medical, implants", PublicationType.JOURNAL_ARTICLE),
            ("Superconductor Materials", "Critical temperature and properties of superconducting materials", "superconductor, critical temperature, magnetic, oxide", PublicationType.JOURNAL_ARTICLE),
            ("Refractory Metals Database", "High-temperature properties of refractory metals and alloys", "refractory, metals, high-temperature, tungsten", PublicationType.DATA_MANAGEMENT_PLAN),
            ("Nanomaterials Properties", "Size-dependent properties of nanoparticles and nanostructures", "nanomaterials, nanoparticles, size-dependent, quantum", PublicationType.CONFERENCE_PAPER),
            ("Perovskite Materials Database", "Electronic and optical properties of perovskite materials", "perovskite, photovoltaic, electronic, optical", PublicationType.JOURNAL_ARTICLE),
            ("Shape Memory Alloys", "Transformation temperatures and mechanical properties of SMAs", "SMA, shape memory, transformation, NiTi", PublicationType.JOURNAL_ARTICLE),
            ("Thermal Barrier Coatings", "Thermal and mechanical properties of TBC materials", "TBC, coatings, thermal barrier, YSZ", PublicationType.DATA_MANAGEMENT_PLAN),
        ]

        materials_ds_meta_data_list = [
            DSMetaData(
                deposition_id=100 + i,
                title=f"Materials Dataset {i+1}: {info[0]}",
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
                orcid=f"0000-000{(i+1)//10}-{(i+1)%10:04d}-{6789+i:04d}",
                ds_meta_data_id=seeded_materials_meta_data[i].id,
            )
            for i in range(20)
        ]
        self.seed(materials_authors)

        # Create MaterialsDataset instances - 20 datasets alternating between user1 and user2
        materials_datasets = [
            MaterialsDataset(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=seeded_materials_meta_data[i].id,
                csv_file_path=f"/uploads/materials_dataset_{i+1}.csv",
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
                ("Alumina", "Al2O3", "Corundum", "Sintering", "density", 3.95, "g/cm³", 298, 101325, DataSource.EXPERIMENTAL, 0.02, "High-purity alumina ceramic"),
                ("Alumina", "Al2O3", "Corundum", "Sintering", "hardness", 9.0, "Mohs", 298, 101325, DataSource.LITERATURE, None, "Mohs hardness scale"),
                ("Zirconia", "ZrO2", "Cubic", "Sintering", "fracture_toughness", 10.0, "MPa·m^0.5", 298, 101325, DataSource.EXPERIMENTAL, 0.5, "YSZ toughness"),
                ("Titanium Dioxide", "TiO2", "Rutile", "Sol-gel", "density", 4.23, "g/cm³", 298, 101325, DataSource.EXPERIMENTAL, 0.03, "Rutile phase"),
            ],
            # Dataset 1: Carbides and Nitrides
            [
                ("Silicon Carbide", "SiC", "Hexagonal", "Hot Pressing", "youngs_modulus", 410, "GPa", 298, 101325, DataSource.COMPUTATIONAL, 10, "DFT calculation"),
                ("Silicon Carbide", "SiC", "Hexagonal", "Hot Pressing", "hardness", 28, "GPa", 298, 101325, DataSource.EXPERIMENTAL, 2, "Vickers hardness"),
                ("Boron Carbide", "B4C", "Rhombohedral", "Reaction Bonding", "hardness", 38, "GPa", 298, 101325, DataSource.EXPERIMENTAL, 2, "Very hard ceramic"),
                ("Aluminium Nitride", "AlN", "Wurtzite", "Sintering", "thermal_conductivity", 180, "W/(m·K)", 298, 101325, DataSource.LITERATURE, 10, "High thermal conductivity"),
                ("Titanium Nitride", "TiN", "Cubic", "PVD", "hardness", 21, "GPa", 298, 101325, DataSource.EXPERIMENTAL, 1.5, "Hard coating material"),
            ],
            # Dataset 2: Metallic Alloys
            [
                ("Steel 304", "Fe-Cr-Ni", "FCC", "Casting", "thermal_conductivity", 16.2, "W/(m·K)", 298, 101325, DataSource.DATABASE, None, "Stainless steel"),
                ("Aluminum 6061", "Al-Mg-Si", "FCC", "Extrusion", "thermal_expansion", 23.6, "10^-6/K", 298, 101325, DataSource.LITERATURE, 0.5, "Engineering alloy"),
                ("Copper", "Cu", "FCC", "Casting", "thermal_conductivity", 401, "W/(m·K)", 298, 101325, DataSource.DATABASE, None, "Pure copper"),
                ("Titanium Ti-6Al-4V", "Ti-Al-V", "HCP+BCC", "Forging", "density", 4.43, "g/cm³", 298, 101325, DataSource.LITERATURE, 0.01, "Aerospace alloy"),
            ],
            # Dataset 3: Semiconductors
            [
                ("Silicon", "Si", "Diamond Cubic", "Czochralski", "bandgap", 1.12, "eV", 298, 101325, DataSource.LITERATURE, 0.01, "Indirect bandgap"),
                ("Gallium Arsenide", "GaAs", "Zinc Blende", "MBE", "bandgap", 1.42, "eV", 298, 101325, DataSource.LITERATURE, 0.02, "Direct bandgap"),
                ("Silicon Carbide", "SiC", "Hexagonal", "CVD", "bandgap", 3.26, "eV", 298, 101325, DataSource.LITERATURE, 0.05, "Wide bandgap"),
                ("Gallium Nitride", "GaN", "Wurtzite", "MOCVD", "bandgap", 3.4, "eV", 298, 101325, DataSource.EXPERIMENTAL, 0.03, "Wide bandgap semiconductor"),
            ],
            # Dataset 4: 2D Materials
            [
                ("Graphene", "C", "2D Hexagonal", "CVD", "youngs_modulus", 1000, "GPa", 298, 101325, DataSource.COMPUTATIONAL, 50, "Monolayer graphene"),
                ("Graphene", "C", "2D Hexagonal", "CVD", "thermal_conductivity", 5000, "W/(m·K)", 298, 101325, DataSource.COMPUTATIONAL, 500, "In-plane conductivity"),
                ("MoS2", "MoS2", "2D Hexagonal", "Exfoliation", "bandgap", 1.8, "eV", 298, 101325, DataSource.EXPERIMENTAL, 0.1, "Monolayer TMD"),
                ("h-BN", "BN", "2D Hexagonal", "CVD", "bandgap", 5.9, "eV", 298, 101325, DataSource.LITERATURE, 0.2, "Hexagonal boron nitride"),
            ],
            # Dataset 5: Polymers
            [
                ("Polyethylene", "(C2H4)n", "Semi-crystalline", "Extrusion", "density", 0.95, "g/cm³", 298, 101325, DataSource.DATABASE, 0.01, "HDPE"),
                ("Polypropylene", "(C3H6)n", "Semi-crystalline", "Injection Molding", "melting_point", 160, "°C", None, 101325, DataSource.LITERATURE, 5, "PP thermoplastic"),
                ("PEEK", "C19H12O3", "Semi-crystalline", "Extrusion", "tensile_strength", 100, "MPa", 298, 101325, DataSource.EXPERIMENTAL, 5, "High performance polymer"),
                ("Nylon 6", "(C6H11NO)n", "Semi-crystalline", "Casting", "youngs_modulus", 2.85, "GPa", 298, 101325, DataSource.LITERATURE, 0.2, "Polyamide"),
            ],
            # Dataset 6: Composites
            [
                ("Carbon Fiber Composite", "C-Epoxy", "Laminate", "Autoclave", "tensile_strength", 600, "MPa", 298, 101325, DataSource.EXPERIMENTAL, 30, "CFRP unidirectional"),
                ("Glass Fiber Composite", "SiO2-Epoxy", "Laminate", "Hand Layup", "tensile_strength", 400, "MPa", 298, 101325, DataSource.EXPERIMENTAL, 20, "GFRP"),
                ("Ceramic Matrix Composite", "SiC-SiC", "Fiber Reinforced", "CVI", "fracture_toughness", 25, "MPa·m^0.5", 298, 101325, DataSource.LITERATURE, 3, "CMC high temperature"),
            ],
            # Dataset 7: High Entropy Alloys
            [
                ("CoCrFeNi", "CoCrFeNi", "FCC", "Arc Melting", "hardness", 2.5, "GPa", 298, 101325, DataSource.EXPERIMENTAL, 0.2, "Cantor alloy"),
                ("CoCrFeNi", "CoCrFeNi", "FCC", "Arc Melting", "youngs_modulus", 200, "GPa", 298, 101325, DataSource.EXPERIMENTAL, 10, "Room temperature"),
                ("AlCoCrFeNi", "AlCoCrFeNi", "BCC", "Arc Melting", "hardness", 5.2, "GPa", 298, 101325, DataSource.EXPERIMENTAL, 0.3, "High hardness HEA"),
                ("CoCrFeMnNi", "CoCrFeMnNi", "FCC", "Arc Melting", "fracture_toughness", 200, "MPa·m^0.5", 77, 101325, DataSource.EXPERIMENTAL, 15, "Cryogenic properties"),
            ],
            # Dataset 8: Piezoelectric Materials
            [
                ("PZT", "Pb(Zr,Ti)O3", "Perovskite", "Sintering", "piezo_coefficient", 300, "pC/N", 298, 101325, DataSource.EXPERIMENTAL, 15, "d33 coefficient"),
                ("Quartz", "SiO2", "Trigonal", "Natural", "piezo_coefficient", 2.3, "pC/N", 298, 101325, DataSource.LITERATURE, 0.1, "d11 coefficient"),
                ("BaTiO3", "BaTiO3", "Perovskite", "Sintering", "dielectric_constant", 1700, "dimensionless", 298, 101325, DataSource.EXPERIMENTAL, 100, "Relative permittivity"),
            ],
            # Dataset 9: Thermoelectric Materials
            [
                ("Bismuth Telluride", "Bi2Te3", "Rhombohedral", "Zone Melting", "ZT", 1.0, "dimensionless", 300, 101325, DataSource.EXPERIMENTAL, 0.1, "Figure of merit"),
                ("Lead Telluride", "PbTe", "Cubic", "Melting", "ZT", 1.5, "dimensionless", 700, 101325, DataSource.LITERATURE, 0.15, "High temperature"),
                ("Silicon Germanium", "SiGe", "Diamond Cubic", "Alloying", "ZT", 0.8, "dimensionless", 1000, 101325, DataSource.EXPERIMENTAL, 0.1, "Very high temperature"),
            ],
            # Dataset 10: Battery Materials
            [
                ("LiCoO2", "LiCoO2", "Layered", "Sol-gel", "specific_capacity", 140, "mAh/g", 298, 101325, DataSource.EXPERIMENTAL, 5, "Cathode material"),
                ("LiFePO4", "LiFePO4", "Olivine", "Hydrothermal", "specific_capacity", 160, "mAh/g", 298, 101325, DataSource.EXPERIMENTAL, 8, "Safer cathode"),
                ("Graphite", "C", "Layered", "Natural", "specific_capacity", 372, "mAh/g", 298, 101325, DataSource.LITERATURE, 10, "Anode material"),
                ("NMC", "LiNi0.33Mn0.33Co0.33O2", "Layered", "Co-precipitation", "specific_capacity", 165, "mAh/g", 298, 101325, DataSource.EXPERIMENTAL, 7, "High energy cathode"),
            ],
            # Dataset 11: Optical Materials
            [
                ("Fused Silica", "SiO2", "Amorphous", "Melting", "refractive_index", 1.46, "dimensionless", 298, 101325, DataSource.DATABASE, 0.001, "At 589 nm"),
                ("Sapphire", "Al2O3", "Corundum", "Czochralski", "refractive_index", 1.77, "dimensionless", 298, 101325, DataSource.LITERATURE, 0.01, "Ordinary ray"),
                ("BK7 Glass", "Borosilicate", "Amorphous", "Melting", "refractive_index", 1.52, "dimensionless", 298, 101325, DataSource.DATABASE, 0.002, "Standard optical glass"),
            ],
            # Dataset 12: Magnetic Materials
            [
                ("Iron", "Fe", "BCC", "Melting", "saturation_magnetization", 1707, "emu/cm³", 298, 101325, DataSource.LITERATURE, 10, "Ferromagnetic"),
                ("NdFeB", "Nd2Fe14B", "Tetragonal", "Sintering", "coercivity", 12000, "Oe", 298, 101325, DataSource.EXPERIMENTAL, 500, "Permanent magnet"),
                ("Ferrite", "Fe3O4", "Cubic", "Ceramic", "saturation_magnetization", 480, "emu/cm³", 298, 101325, DataSource.EXPERIMENTAL, 20, "Soft magnetic"),
            ],
            # Dataset 13: Biomaterials
            [
                ("Titanium", "Ti", "HCP", "Machining", "biocompatibility", 5, "scale", 310, 101325, DataSource.EXPERIMENTAL, None, "Excellent for implants"),
                ("Hydroxyapatite", "Ca10(PO4)6(OH)2", "Hexagonal", "Precipitation", "bioactivity", 8, "scale", 310, 101325, DataSource.EXPERIMENTAL, None, "Bone substitute"),
                ("PEEK", "C19H12O3", "Semi-crystalline", "Extrusion", "biocompatibility", 4, "scale", 310, 101325, DataSource.LITERATURE, None, "Polymer implant"),
            ],
            # Dataset 14: Superconductors
            [
                ("YBCO", "YBa2Cu3O7", "Orthorhombic", "Solid State", "critical_temperature", 92, "K", None, 101325, DataSource.LITERATURE, 1, "High-Tc superconductor"),
                ("NbTi", "NbTi", "BCC", "Alloying", "critical_temperature", 9.5, "K", None, 101325, DataSource.DATABASE, 0.2, "Type-II superconductor"),
                ("MgB2", "MgB2", "Hexagonal", "Reaction", "critical_temperature", 39, "K", None, 101325, DataSource.LITERATURE, 1, "Intermediate Tc"),
            ],
            # Dataset 15: Refractory Metals
            [
                ("Tungsten", "W", "BCC", "Powder Metallurgy", "melting_point", 3422, "°C", None, 101325, DataSource.LITERATURE, 10, "Highest melting point"),
                ("Molybdenum", "Mo", "BCC", "Arc Melting", "thermal_conductivity", 138, "W/(m·K)", 298, 101325, DataSource.DATABASE, 5, "High temperature"),
                ("Tantalum", "Ta", "BCC", "Electron Beam Melting", "melting_point", 3017, "°C", None, 101325, DataSource.LITERATURE, 20, "Corrosion resistant"),
            ],
            # Dataset 16: Nanomaterials
            [
                ("Gold Nanoparticles", "Au", "FCC", "Chemical Reduction", "particle_size", 20, "nm", 298, 101325, DataSource.EXPERIMENTAL, 2, "Spherical nanoparticles"),
                ("Carbon Nanotubes", "C", "Tubular", "CVD", "diameter", 1.5, "nm", 298, 101325, DataSource.EXPERIMENTAL, 0.2, "Single-walled CNT"),
                ("ZnO Nanowires", "ZnO", "Wurtzite", "Hydrothermal", "diameter", 50, "nm", 298, 101325, DataSource.EXPERIMENTAL, 5, "Nanowire array"),
            ],
            # Dataset 17: Perovskite Materials
            [
                ("MAPI", "CH3NH3PbI3", "Perovskite", "Solution Processing", "bandgap", 1.55, "eV", 298, 101325, DataSource.EXPERIMENTAL, 0.02, "Photovoltaic material"),
                ("CsPbBr3", "CsPbBr3", "Perovskite", "Hot Injection", "bandgap", 2.3, "eV", 298, 101325, DataSource.EXPERIMENTAL, 0.05, "LED material"),
                ("FAPbI3", "HC(NH2)2PbI3", "Perovskite", "Solution Processing", "bandgap", 1.48, "eV", 298, 101325, DataSource.LITERATURE, 0.03, "Stable perovskite"),
            ],
            # Dataset 18: Shape Memory Alloys
            [
                ("Nitinol", "NiTi", "B2/B19'", "Arc Melting", "transformation_temp", 50, "°C", None, 101325, DataSource.EXPERIMENTAL, 3, "Austenite finish"),
                ("Nitinol", "NiTi", "B2/B19'", "Arc Melting", "superelasticity", 8, "%", 298, 101325, DataSource.EXPERIMENTAL, 0.5, "Recoverable strain"),
                ("CuAlNi", "Cu-Al-Ni", "Beta Phase", "Casting", "transformation_temp", 80, "°C", None, 101325, DataSource.LITERATURE, 5, "Higher temperature SMA"),
            ],
            # Dataset 19: Thermal Barrier Coatings
            [
                ("YSZ", "Y2O3-ZrO2", "Tetragonal", "APS", "thermal_conductivity", 2.3, "W/(m·K)", 298, 101325, DataSource.EXPERIMENTAL, 0.2, "Standard TBC"),
                ("YSZ", "Y2O3-ZrO2", "Tetragonal", "EB-PVD", "porosity", 15, "%", 298, 101325, DataSource.EXPERIMENTAL, 2, "Columnar structure"),
                ("Gadolinium Zirconate", "Gd2Zr2O7", "Pyrochlore", "APS", "thermal_conductivity", 1.6, "W/(m·K)", 298, 101325, DataSource.LITERATURE, 0.15, "Low conductivity TBC"),
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
                    description=record_data[11]
                )
                all_records.append(record)

        self.seed(all_records)
