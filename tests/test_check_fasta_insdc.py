import os
from unittest import TestCase
from unittest.mock import patch

import requests as requests

from bin.check_fasta_insdc import assess_fasta, get_analyses_and_reference_genome_from_metadata


class TestFastaChecker(TestCase):
    resource_dir = os.path.join(os.path.dirname(__file__), 'resources')

    def test_assess_fasta_is_insdc(self):
        input_fasta = os.path.join(self.resource_dir, 'fasta_files', 'Saccharomyces_cerevisiae_I.fa')
        results = assess_fasta(input_fasta, ['analysis'], None)
        assert results == {
            'all_insdc': True,
            'sequences': [{'sequence_name': 'I', 'sequence_md5': '6681ac2f62509cfc220d78751b8dc524', 'insdc': True}],
            'possible_assemblies': {'GCA_000146045.2'}
        }
        input_fasta = os.path.join(self.resource_dir, 'fasta_files', 'input_passed.fa')
        results = assess_fasta(input_fasta, ['analysis'], None)
        assert results == {
            'all_insdc': False,
            'sequences': [{'sequence_name': 'chr1', 'sequence_md5': 'd2b3f22704d944f92a6bc45b6603ea2d', 'insdc': False}]
        }

    def test_assess_fasta_matches_metadata(self):
        input_fasta = os.path.join(self.resource_dir, 'fasta_files', 'Saccharomyces_cerevisiae_I.fa')
        results = assess_fasta(input_fasta, ['analysis'], 'GCA_000146045.2')
        assert results == {
            'all_insdc': True,
            'sequences': [
                {'sequence_name': 'I', 'sequence_md5': '6681ac2f62509cfc220d78751b8dc524', 'insdc': True}],
            'possible_assemblies': {'GCA_000146045.2'},
            'metadata_assembly_compatible': True,
            'associated_analyses': ['analysis'],
            'assembly_in_metadata': 'GCA_000146045.2'
        }
        results = assess_fasta(input_fasta, ['analysis'], 'GCA_002915635.1')
        assert results == {
            'all_insdc': True,
            'sequences': [
                {'sequence_name': 'I', 'sequence_md5': '6681ac2f62509cfc220d78751b8dc524', 'insdc': True}],
            'possible_assemblies': {'GCA_000146045.2'},
            'metadata_assembly_compatible': False,
            'associated_analyses': ['analysis'],
            'assembly_in_metadata': 'GCA_002915635.1'
        }

    def test_get_analysis_and_reference_genome_from_metadata(self):
        metadata_json = os.path.join(self.resource_dir, 'sample_checker', 'metadata.json')
        vcf_file = os.path.join(self.resource_dir, 'sample_checker', 'example1.vcf.gz')
        analyses, reference = get_analyses_and_reference_genome_from_metadata([vcf_file], metadata_json)
        assert analyses == {'VD1'}
        assert reference == 'GCA_000001405.27'

    def test_assess_fasta_http_error(self):
        input_fasta = os.path.join(self.resource_dir, 'fasta_files', 'Saccharomyces_cerevisiae_I.fa')
        with patch('bin.check_fasta_insdc._get_containing_assemblies_paged', autospec=True) as m_get_assemblies:
            m_get_assemblies.side_effect = requests.HTTPError('500 Internal Server Error')
            results = assess_fasta(input_fasta, ['analysis'], None)
            assert results == {
                'sequences': [{'sequence_name': 'I', 'sequence_md5': '6681ac2f62509cfc220d78751b8dc524', 'insdc': True}],
                'error': '500 Internal Server Error'
            }
