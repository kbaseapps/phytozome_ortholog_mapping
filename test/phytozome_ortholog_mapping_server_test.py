# -*- coding: utf-8 -*-
import os
import time
import unittest
import shutil
from configparser import ConfigParser

from phytozome_ortholog_mapping.phytozome_ortholog_mappingImpl import phytozome_ortholog_mapping
from phytozome_ortholog_mapping.phytozome_ortholog_mappingServer import MethodContext
from phytozome_ortholog_mapping.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.GenomeFileUtilClient import GenomeFileUtil

class phytozome_ortholog_mappingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('phytozome_ortholog_mapping'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'phytozome_ortholog_mapping',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = phytozome_ortholog_mapping(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_phytozome_ortholog_mapping_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa
        cls.gfu = GenomeFileUtil(cls.callback_url)
        cls.genome = "Test_Genome"
        cls.prepare_data()

    @classmethod
    def prepare_data(cls):
        cls.gff_filename = 'Test_v1.0.gene.gff3.gz'
        cls.gff_path = os.path.join(cls.scratch, cls.gff_filename)
        shutil.copy(os.path.join("/kb", "module", "data", cls.gff_filename), cls.gff_path)

        cls.fa_filename = 'Test_v1.0.fa.gz'
        cls.fa_path = os.path.join(cls.scratch, cls.fa_filename)
        shutil.copy(os.path.join("/kb", "module", "data", cls.fa_filename), cls.fa_path)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def loadFakeGenome(cls):
        
        input_params = {
            'fasta_file': {'path': cls.fa_path},
            'gff_file': {'path': cls.gff_path},
            'genome_name': cls.genome,
            'workspace_name': cls.wsName,
            'source': 'Phytozome',
            'type': 'Reference',
            'scientific_name': 'Populus trichocarpa'
        }

        result = cls.gfu.fasta_gff_to_genome(input_params)

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})

        self.loadFakeGenome()

        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        ret = self.serviceImpl.map_phytozome_orthologs(self.ctx, {'input_ws': self.wsName,
                                                                  'input_genome': self.genome,
                                                                  'ortholog_feature_set': 'orthologous_features'})
