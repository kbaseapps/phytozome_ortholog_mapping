/*
A KBase module: phytozome_ortholog_mapping
*/

module phytozome_ortholog_mapping {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    typedef structure {
	float threshold;
	string input_ws;
	string input_features;
	string ortholog_feature_set;
    } MapPhytozomeOrthologsParams;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef map_phytozome_orthologs(MapPhytozomeOrthologsParams params) returns (ReportResults output) authentication required;

};
