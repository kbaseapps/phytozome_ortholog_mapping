# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import json
import time
import uuid

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
#END_HEADER


class phytozome_ortholog_mapping:
    '''
    Module Name:
    phytozome_ortholog_mapping

    Module Description:
    A KBase module: phytozome_ortholog_mapping
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "git@github.com:kbaseapps/phytozome_ortholog_mapping.git"
    GIT_COMMIT_HASH = "6c0541a681990d19754c9eaec70777afcf0ac348"

    #BEGIN_CLASS_HEADER

    def log(self,message, prefix_newline=False):
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        print(('\n' if prefix_newline else '') + time_str + ': ' + message)

    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.token = os.environ['KB_AUTH_TOKEN']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        self.dfu = DataFileUtil(self.callback_url)
        #END_CONSTRUCTOR
        pass


    def map_phytozome_orthologs(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "MapPhytozomeOrthologsParams" ->
           structure: parameter "threshold" of Double, parameter "input_ws"
           of String, parameter "input_features" of String, parameter
           "ortholog_feature_set" of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN map_phytozome_orthologs

        with open("/data/Phytozome_Ortholog_Mapping.json") as data_file:
            species_ortholog_map = json.load(data_file)

        print("Species: ",str(len(species_ortholog_map.keys())))

        ortholog_map = dict()
        for spp in species_ortholog_map.keys():
            for feature in species_ortholog_map[spp].keys():
                if(feature not in ortholog_map):
                    ortholog_map[feature] = dict()
                for ortholog in species_ortholog_map[spp][feature].keys():
                    if(ortholog not in ortholog_map[feature]):
                        ortholog_map[feature][ortholog]=species_ortholog_map[spp][feature][ortholog]

        # Input can be either genome or feature set
        self.log("Fetching Features: "+params['input_ws']+'/'+params['input_features'])
        feature_object = self.dfu.get_objects({'object_refs': [params['input_ws']+'/'+params['input_features']]})['data'][0]
        object_type = feature_object['info'][2]

        found_orthologs = list()
        if("KBaseGenomes.Genome" in object_type):
            print("Query Features in "+object_type+": ",str(len(feature_object['data']['mrnas'])))

            for mrna in feature_object['data']['mrnas']:
                if(mrna['id'] in ortholog_map):
                    for ortholog in ortholog_map[mrna['id']].keys():
                        if(ortholog not in found_orthologs):
                            found_orthologs.append(ortholog)

        elif("KBaseCollections.FeatureSet" in object_type):
            print("Query Features in "+object_type+": ",str(len(feature_object['data']['elements'])))

            genome_obj_dict = dict()
            for query_ftr in feature_object['data']['elements']:
                if(query_ftr in ortholog_map):
                    for ortholog in ortholog_map[query_ftr].keys():
                        if(ortholog not in found_orthologs):
                            found_orthologs.append(ortholog)
                else:
                    # each element in a FeatureSet should hold the workspace reference for its source genome
                    genome_ref = feature_object['data']['elements'][query_ftr][0]
                    genome_obj = dict()
                    if(genome_ref not in genome_obj_dict):
                        genome_obj = self.dfu.get_objects({'object_refs': [ genome_ref ]})['data'][0]
                        genome_obj_dict[genome_ref]=genome_obj
                    else:
                        genome_obj = genome_obj_dict[genome_ref]

                    # iterate through features until you get a hit
                    # then find the mapping through the child mrna
                    for genome_ftr in genome_obj['data']['features']:
                        if(genome_ftr['id'] == query_ftr):
                            for genome_mrna in genome_ftr['mrnas']:
                                if(genome_mrna in ortholog_map):
                                    for ortholog in ortholog_map[genome_mrna].keys():
                                        if(ortholog not in found_orthologs):
                                            found_orthologs.append(ortholog)

        ortholog_set = {'elements' : {}}

        for ortholog in found_orthologs:
            ortholog_set['elements'][ortholog]=["Phytozome_Genomes/Athaliana_TAIR10"]

        print("Found: ",len(found_orthologs))

        wsid = self.dfu.ws_name_to_id(params['input_ws'])
        save_result = self.dfu.save_objects({'id':wsid,'objects':[{'name':params['ortholog_feature_set'],
                                                                   'data':ortholog_set,
                                                                   'type':'KBaseCollections.FeatureSet'}]})[0]
        
        # reference of saved featureset
        saved_featureset = "{}/{}/{}".format(save_result[6],save_result[0],save_result[4])
        
        html_string="<html><head><title>KBase Phytozome Ortholog Mapping Report</title></head><body>"
        html_string+="<p>The app has finished running and it found "
        html_string+=str(len(found_orthologs))+" Arabidopsis orthologs</p></body></html>"

        uuid_string = str(uuid.uuid4())
        report_params = { 'objects_created' : [{"ref":saved_featureset,"description":"bollocks"}],
#                          'file_links' : output_files,
#                          'html_links' : [html_folder],
#                          'direct_html_link_index' : 0, #Use to refer to index of 'html_links'
                          'direct_html' : html_string, # Can't embed images
                          'workspace_name' : params['input_ws'],
                          'report_object_name' : 'phytozome_ortholog_mapping_' + uuid_string }
        kbase_report_client = KBaseReport(self.callback_url, token=self.token)
        report_client_output = kbase_report_client.create_extended_report(report_params)

        output = dict()
        output['report_name']=report_client_output['name']
        output['report_ref']=report_client_output['ref']

        #END map_phytozome_orthologs

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method map_phytozome_orthologs return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
