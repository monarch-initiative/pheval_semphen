import os
import pandas as pd
from pathlib import Path
from pheval.post_processing.post_processing import PhEvalDiseaseResult
from pheval.post_processing.post_processing import generate_pheval_result
##from pheval.post_processing.post_processing import PhEvalGeneResult
##from pheval.post_processing.post_processing import PhEvalVariantResult
from pheval.utils.file_utils import files_with_suffix


def convert_to_pheval_disease_results(res_path: str, output_dir: str):
    """
    Opens raw results file as dataframe, converts to lists, and uses phevals built in results formatting to
    convert and write disease results to relevant pheval_disease_results directory
    """

    # Open and convert to lists
    analysis_df = pd.read_csv(res_path, sep='\t', header=0)
    ranks = list(analysis_df["rank"])
    scores = list(analysis_df["score"]) 
    names = list(analysis_df["disease_name"]) 
    ids = list(analysis_df["disease_identifier"])

    # Convert data to pheval results
    results = [PhEvalDiseaseResult(disease_name=d[2],
                                   disease_identifier=d[3],
                                   score=float(d[1])) for d in zip(ranks, scores, names, ids)]
        
    # Now leverage pheval to write disease results to disease results directory with accompanying filename suffixs
    # Note, that we need to format samplename_results.tsv --> samplename.tsv so that the pheval post_processing .stem
    # function will pull in the appropriate sample name
    tool_res_path = Path(res_path.replace("_results", ''))
    pheval_res = generate_pheval_result(pheval_result=results,
                                        sort_order_str='descending', # We want highest score first
                                        output_dir=output_dir,
                                        tool_result_path=tool_res_path)
        

def raw_results_to_pheval(raw_results_dir: str, 
                          output_dir: str, 
                          disease_analysis: bool=True, 
                          gene_analysis: bool=False, 
                          variant_analysis: bool=False):

    # Disease results
    if disease_analysis == True:
        for fname in files_with_suffix(raw_results_dir, suffix='.tsv'):
            convert_to_pheval_disease_results(str(fname), output_dir)
    
    # TO DO: Potentially 
    ##if gene_analysis == True:
    ##if variant_analysis == True: