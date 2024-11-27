"""Custom Pheval Runner."""
# General imports
import os
import subprocess
import pandas as pd
from pathlib import Path
from packaging import version
from dataclasses import dataclass
from typing import Optional
from pydantic import (BaseModel, 
                      Field)

# Pheval imports
from pheval.runners.runner import PhEvalRunner
from pheval.utils.file_utils import (all_files,
                                     files_with_suffix)
from pheval.post_processing.post_processing import (PhEvalDiseaseResult,
                                                    generate_pheval_result)


class SemphenConfigurations(BaseModel):
    """
    Class for defining the semphen configurations in tool_specific_configurations field,
    within the input_dir config.yaml
    Args:
        environment (str): Environment to run semphen, i.e., local/docker (only local supported)
        path_to_semphen (str): File path to semphen.py 
        path_to_phenio (str): File path to phenio.db file
    """

    environment: str = Field(...)
    path_to_phenio: str = Field(...)
    path_to_semphen: Optional[str] = None


@dataclass
class SemphenPhevalRunner(PhEvalRunner):
    """
    CustomPhevalRunner Class
    """

    input_dir: Path
    testdata_dir: Path
    tmp_dir: Path
    output_dir: Path
    config_file: Path
    version: str


    def prepare(self):
        """
        prepare method (Currently un-used for this runner)
        """
        dummy_variable = 0
    

    def run(self):
        """
        Generates semphen command line call and writes to file, then runs the command through subprocess
        """

        # Gather tool config options and create output path to write command to 
        config = SemphenConfigurations.model_validate(self.input_dir_config.tool_specific_configuration_options)
        tool_command_outpath = str(self.tool_input_commands_dir.joinpath("semphen_commands.txt"))

        # outputd_dir is the top level directory for the results for this run.
        # So we pass in self.raw_results_dir instead so that the tool will output there instead to work with pheval
        self.run_semphen_local(input_dir=self.testdata_dir,
                               output_dir=self.raw_results_dir,
                               tool_input_commands_path=tool_command_outpath,
                               config=config)


    def post_process(self):
        """
        post_process method
        """
        
        # Disease results
        if self.input_dir_config.disease_analysis == True:
            for fname in files_with_suffix(self.raw_results_dir, suffix='.tsv'):
                self.convert_to_pheval_disease_results(str(fname), self.output_dir)
        
        # TO DO: Potentially
        ##if gene_analysis == True:
        ##if variant_analysis == True:

    
    # Run (main function )
    def run_semphen_local(self,input_dir: Path,
                          output_dir: Path,
                          tool_input_commands_path: str,
                          config: SemphenConfigurations) -> None:
        """
        Run Semphen locally
        """

        # Combine arguments into subprocess friendly command format
        if config.path_to_semphen != None:
            subp_command = ["python", config.path_to_semphen]
        else:
            subp_command = ["pheval-semphen"]
        
        # Add the rest of our command options
        subp_command += ["rank-associations",
                         "-i", input_dir,
                         "-o", output_dir,
                         "-p", config.path_to_phenio]
        
        # Write command to file
        with open(tool_input_commands_path, 'w') as outfile:
            outfile.write(' '.join([str(v) for v in subp_command])) # Must convert Path objects to strings
        
        # Run semphen through subprocss
        subprocess.run(subp_command, shell=False)


    # Post Process (sub function)
    def convert_to_pheval_disease_results(self, res_path: str, output_dir: str):
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

