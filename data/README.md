## InParanoid Orthologs

The app attempts to map the features in a genome or a feature set to
orthologs in Arabidopsis thaliana using the results computed from
InParanoid by Phytozome, these are made available direct from
Phytozome:

https://data.jgi.doe.gov/refine-download/phytozome?expanded=Phytozome-167

You will want to download the file named:
`inparanoid_Athaliana_167_TAIR10.tar.gz`

At this time, that file was dated 23 Sept 2020 and hasn't since been
updated, so it won't include all the genomes in Phytozome until it's
next updated. The genomes that were included as part of this current
iteration are listed in:
[`Phytozome_Genomes_080421.txt`](Phytozome_Genomes_080421.txt)

The archive contains a list of files, one for each Phytozome genome,
so I wrote a short script
([`Consolidate_Orthologs.py`](Consolidate_Orthologs.py)) to process
these into a single JSON file to use as reference data, which is
loaded from:

https://web.cels.anl.gov/~seaver/KBase_App_Files/Phytozome_Ortholog_Mapping.tar.gz

as part of [`scripts/entrypoint.sh`](../scripts/entrypoint.sh)
