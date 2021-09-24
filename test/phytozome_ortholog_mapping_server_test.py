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
from installed_clients.DataFileUtilClient import DataFileUtil

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
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.genome = "Test_Genome"
        cls.feature_set = "Test_Feature_Set"
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

    def loadFakeFeatureSet(cls):
        
        feature_list = ["Bradi1g19650.1","Bradi4g08567.1","Bradi5g26017.1",
                        "Bradi1g08917.1","Bradi1g48264.1","Bradi3g43345.2",
                        "Bradi3g33740.1","Bradi3g27912.3","Bradi3g34450.1","Bradi2g28007.1"]

        feature_set_dict = {'elements':{}}
        for feature in feature_list:
            feature_set_dict['elements'][feature]=["Phytozome_Genomes/Bdistachyon_v3.1"]

        wsid = cls.dfu.ws_name_to_id(cls.wsName)
        save_result = cls.dfu.save_objects({'id':wsid,'objects':[{'name':cls.feature_set,
                                                                  'data':feature_set_dict,
                                                                  'type':'KBaseCollections.FeatureSet'}]})[0]

        ws="seaver:narrative_1628187323546"
        wsid = cls.dfu.ws_name_to_id(ws)
        save_result = cls.dfu.save_objects({'id':wsid,'objects':[{'name':cls.feature_set,
                                                                  'data':feature_set_dict,
                                                                  'type':'KBaseCollections.FeatureSet'}]})[0]

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_map_phytozome_orthologs_from_genome(self):
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
                                                                  'ortholog_feature_set': 'orthologous_from_genome'})

    def test_map_phytozome_orthologs_from_feature_set(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})

        self.loadFakeFeatureSet()

        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        ret = self.serviceImpl.map_phytozome_orthologs(self.ctx, {'input_ws': self.wsName,
                                                                  'input_feature_set': self.feature_set,
                                                                  'ortholog_feature_set': 'orthologous_from_feature_set'})

