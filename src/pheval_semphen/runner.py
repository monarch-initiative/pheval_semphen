"""Custom Pheval Runner."""
from dataclasses import dataclass
from pathlib import Path
from pheval.runners.runner import PhEvalRunner

from pheval_semphen.prepare.tool_specific_configuration_options import SemphenConfigurations
from pheval_semphen.run.run import run_semphen_local
from pheval_semphen.post_process.post_process import raw_results_to_pheval


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
        prepare method
        """
        print("preparing")

    def run(self):
        """
        Generates semphen command line call and writes to file, then runs the command through subprocess
        """

        # Gather tool config options and create output path to write command to 
        config = SemphenConfigurations.model_validate(self.input_dir_config.tool_specific_configuration_options)
        tool_command_outpath = str(self.tool_input_commands_dir.joinpath("semphen_commands.txt"))

        # outputd_dir is the top level directory for the results for this run.
        # So we pass in self.raw_results_dir instead so that the tool will output there instead to work with pheval
        run_semphen_local(input_dir=self.testdata_dir,
                          output_dir=self.raw_results_dir,
                          tool_input_commands_path=tool_command_outpath,
                          config=config)

    def post_process(self):
        """
        post_process method
        """

        raw_results_to_pheval(raw_results_dir=self.raw_results_dir,
                              output_dir=self.output_dir,
                              disease_analysis=self.input_dir_config.disease_analysis,
                              gene_analysis=self.input_dir_config.gene_analysis,
                              variant_analysis=self.input_dir_config.variant_analysis)
