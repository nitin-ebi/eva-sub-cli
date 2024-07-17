import json
import os
from unittest import TestCase

import jsonschema
import yaml

from eva_sub_cli import ETC_DIR
from eva_sub_cli.executables.xlsx2json import XlsxParser, create_xls_template_from_yaml


class TestXlsReader(TestCase):
    resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
    conf_filename = os.path.join(ETC_DIR, 'spreadsheet2json_conf.yaml')
    eva_schema = os.path.abspath(os.path.join(__file__, "../../eva_sub_cli/etc/eva_schema.json", ))
    biosample_schema = os.path.abspath(os.path.join(__file__, "../../eva_sub_cli/etc/eva-biosamples.json", ))

    def tearDown(self):
        files_from_tests = [
            os.path.join(self.resource_dir, 'EVA_Submission_test_output.json'),
            os.path.join(self.resource_dir, 'metadata_not_existing.xlsx'),
            os.path.join(self.resource_dir, 'EVA_Submission_test_errors.yml')
        ]
        for f in files_from_tests:
            if os.path.exists(f):
                os.remove(f)

    def test_conversion_2_json(self) -> None:
        xls_filename = os.path.join(self.resource_dir, 'EVA_Submission_test.xlsx')
        self.parser = XlsxParser(xls_filename, self.conf_filename)
        output_json = os.path.join(self.resource_dir, 'EVA_Submission_test_output.json')
        errors_yaml = os.path.join(self.resource_dir, 'EVA_Submission_test_errors.yml')
        self.parser.json(output_json)
        self.parser.save_errors(errors_yaml)

        # confirm no errors
        with open(errors_yaml) as open_file:
            errors_data = yaml.safe_load(open_file)
            assert errors_data == []

        with open(output_json) as open_file:
            json_data = json.load(open_file)
            # assert json file is created with expected data
            assert sorted(json_data.keys()) == ['analysis', 'files', 'project', 'sample', 'submitterDetails']
            self.assertEqual(self.get_expected_json(), json_data)

        # assert json schema
        with open(self.eva_schema) as eva_schema_file:
            eva_json_schema = json.load(eva_schema_file)
        with open(self.biosample_schema) as biosample_schema_file:
            biosample_json_schema = json.load(biosample_schema_file)

        # assert created json file sample field conforms to eva-biosamples schema
        jsonschema.validate(json_data['sample'][3]['bioSampleObject'], biosample_json_schema)

        # assert created json file conform to eva_schema
        resolver = jsonschema.RefResolver.from_schema(eva_json_schema)
        resolver.store['eva-biosamples.json'] = biosample_json_schema
        jsonschema.validate(json_data, eva_json_schema, resolver=resolver)

    def test_create_xls_template(self):
        metadata_file = os.path.join(self.resource_dir, 'metadata_not_existing.xlsx')
        create_xls_template_from_yaml(metadata_file, self.conf_filename)
        assert os.path.exists(metadata_file)

    def test_json_conversion_fails(self):
        xls_filename = os.path.join(self.resource_dir, 'EVA_Submission_test_fails.xlsx')
        self.parser = XlsxParser(xls_filename, self.conf_filename)
        output_json = os.path.join(self.resource_dir, 'EVA_Submission_test_output.json')
        errors_yaml = os.path.join(self.resource_dir, 'EVA_Submission_test_errors.yml')
        self.parser.json(output_json)
        self.parser.save_errors(errors_yaml)

        assert not os.path.exists(output_json)
        with open(errors_yaml) as open_file:
            errors_data = yaml.safe_load(open_file)
            assert errors_data == [{
                'sheet': 'Project',
                'row': '',
                'column': 'Tax ID',
                'description': 'Worksheet Project is missing required header Tax ID'
            }]

    def get_expected_json(self):
        return {
            "submitterDetails": [
                {
                    "lastName": "Smith",
                    "firstName": "John",
                    "email": "john.smith@example.com",
                    "laboratory": "Genomics Lab",
                    "centre": "University of Example",
                    "address": "1 street address"
                },
                {
                    "lastName": "Doe",
                    "firstName": "Jane",
                    "email": "jane.doe@example.com",
                    "laboratory": "Bioinformatics Lab",
                    "centre": "University of Example",
                    "address": "1 street address"
                }
            ],
            "project": {
                "title": "Example Project",
                "description": "An example project for demonstration purposes",
                "centre": "University of Example",
                "taxId": 9606,
                "holdDate": "2023-12-31T00:00:00"
            },
            "analysis": [
                {
                    "analysisTitle": "Variant Detection 1",
                    "analysisAlias": "VD1",
                    "description": "An example analysis for demonstration purposes",
                    "experimentType": "Whole genome sequencing",
                    "referenceGenome": "GCA_000001405.27",
                    "referenceFasta": "GCA_000001405.27_fasta.fa",
                    "platform": "BGISEQ-500"
                },
                {
                    "analysisTitle": "Variant Detection 2",
                    "analysisAlias": "VD2",
                    "description": "An example analysis for demonstration purposes",
                    "experimentType": "Whole genome sequencing",
                    "referenceGenome": "GCA_000001405.27",
                    "referenceFasta": "GCA_000001405.27_fasta.fa",
                    "platform": "BGISEQ-500"
                },
                {
                    "analysisTitle": "Variant Detection 3",
                    "analysisAlias": "VD3",
                    "description": "An example analysis for demonstration purposes",
                    "experimentType": "Whole genome sequencing",
                    "referenceGenome": "GCA_000001405.27",
                    "referenceFasta": "GCA_000001405.27_fasta.fa",
                    "platform": "BGISEQ-500"
                }
            ],
            "sample": [
                {
                    "analysisAlias": ["VD1", "VD2", "VD3"],
                    "sampleInVCF": "sample1",
                    "bioSampleAccession": "SAME00001"
                },
                {
                    "analysisAlias": ["VD1", "VD2", "VD3"],
                    "sampleInVCF": "sample2",
                    "bioSampleAccession": "SAME00002"
                },
                {
                    "analysisAlias": ["VD3"],
                    "sampleInVCF": "sample3",
                    "bioSampleAccession": "SAME00003"
                },
                {
                    "analysisAlias": ["VD4", "VD5"],
                    "sampleInVCF": "sample4",
                    "bioSampleObject": {
                        "name": "Lm_17_S8",
                        "characteristics": {
                            "title": [
                                {"text": "Bastet normal sample"}
                            ],
                            "description": [
                                {"text": "Test Description"}
                            ],
                            "taxId": [
                                {"text": "9447"}
                            ],
                            "scientificName": [
                                {"text": "Lemur catta"}
                            ],
                            "sex": [
                                {"text": "Female"}
                            ],
                            "tissueType": [
                                {"text": "skin"}
                            ],
                            "species": [
                                {"text": "Lemur catta"}
                            ]
                        }
                    }
                }
            ],
            "files": [
                {
                    "analysisAlias": "VD1",
                    "fileName": "example1.vcf.gz",
                },
                {
                    "analysisAlias": "VD2",
                    "fileName": "example2.vcf",
                },
                {
                    "analysisAlias": "VD3",
                    "fileName": "example3.vcf",
                }
            ]
        }
