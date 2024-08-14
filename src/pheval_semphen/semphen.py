# General imports
import os
import click
from pathlib import Path
from typing import List, Set
from collections import Counter
import pandas as pd
import numpy as np

# Pheval phenopacket utils
from pheval.utils.phenopacket_utils import phenopacket_reader
from pheval.utils.phenopacket_utils import PhenopacketUtil

# Semsimian
from semsimian import Semsimian


@click.group()
def main():
    """
    Main entry point for the CLI tool.
    """
    pass


def gather_input_output_info(input_path, output_path, results_suffix="_results.tsv"):
    """
    Input is allowed to be a directory containing .json phenopacket files
    Or input is allowed to be a filepath specifying a .json phenopacket
    """
    
    if os.path.isdir(input_path):
        process_data = [os.path.join(input_path, fname) for fname in os.listdir(input_path) if fname.endswith(".json")]
        
    elif os.path.isfile(input_path) and input_path.endswith(".json"):
        process_data = [input_path]
    
    else:
        return None, None
    
    # Format output file names
    out_data = [os.path.join(output_path, pname.split('/')[-1].replace(".json", results_suffix)) for pname in process_data]
    
    return process_data, out_data


@click.command()
@click.option("--input-path",
              "-i",
              required=True,
              type=str,
              help="Input path to directory of .json phenopacket files OR a path to a single .json phenopacket file",
)
@click.option("--output-path",
              "-o",
              required=True,
              type=str,
              help="Output file path to a directory "
)
@click.option("--phenio-path",
              "-p",
              required=True,
              type=str,
              help="Path phenio database .db file")
def get_phenotype_associations(input_path, output_path, phenio_path):
    """
    This algorithm leverages Semsimian + Monarchs phenio ontology to find the disease(s) 
    that are most associated with a patients phenotypes. A single .json phenopacket file can be passed in or
    a directory containing multiple .json phenopacket files. The patients observed phenotype terms are pulled
    from the data and are used as input to semsimian. Disease information is returned with the top associated
    ids appearing first in the list. 
    
    Subject prefixes within the phenio db begginning with "MONDO:" are compared
    """

    
    # Preformat our input and output paths
    infiles, outfiles = gather_input_output_info(input_path, output_path, results_suffix="_results.tsv")
    print("- Found {} file(s) to process...".format(format(len(infiles), ',')))
    
    # Initiate semsimian object
    semsim = Semsimian(predicates=["rdfs:subClassOf"], spo=None, resource_path=phenio_path)
    print("- Semsimian object loaded with data from {}".format(phenio_path))
    
    # Loop through data perform semsimians associations_search method on phenopacket hp terms
    processed = 0
    for fname, outname in zip(infiles, outfiles):
        
        # Open phenopacket file and pull relevant information (we want observed phenotypes)
        phenopacket = phenopacket_reader(str(fname))
        phenopacket_util = PhenopacketUtil(phenopacket)
        observed_phenotypes = phenopacket_util.observed_phenotypic_features()
        phenotype_ids = [observed_phenotype.type.id for observed_phenotype in observed_phenotypes]
        
        # Perform search (results are sorted in order of best ranking to worst ranking)
        results =  semsim.associations_search(object_closure_predicate_terms={"biolink:has_phenotype"},
                                              object_terms=set(phenotype_ids),
                                              include_similarity_object=False,
                                              subject_terms=None,
                                              subject_prefixes=["MONDO:"],
                                              search_type="full",
                                              score_metric="ancestor_information_content",
                                              limit=10000,
                                              direction="object_to_subject")
        ###results = [[0,0,"A"], [1,1,"B"], [2,2,"C"]] Testing purposes
        
        # Results are originally in form of [[score, details, mondo_id], ...]
        results = np.asarray(results).T
        
        # Convert to dataframe and write data. 
        # TO DO: potentially need to map disease_identifier to something else, and bring in disease_name through sssom file...
        pd.DataFrame({"rank":np.arange(1, len(results[0])+1),
                      "score":np.round(results[0].astype(float), decimals=4),
                      "disease_name":".",
                      "disease_identifier":results[2]} 
                     ).to_csv(outname, sep='\t', header=True, index=False)
        
        processed += 1
        ##if processed >= 10:
        ##    break
    

main.add_command(get_phenotype_associations, name="rank-associations")


if __name__ == '__main__':
    main()
