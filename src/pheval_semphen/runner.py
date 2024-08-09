"""Custom Pheval Runner."""
from dataclasses import dataclass
from pathlib import Path
from pheval.runners.runner import PhEvalRunner

# Copied from EXOMISER
#from pheval_exomiser.post_process.post_process import post_process_result_format
from pheval_semphen.prepare.tool_specific_configuration_options import SemphenConfigurations
from pheval_semphen.run.run import run_semphen_local


@dataclass
class SemphenPhevalRunner(PhEvalRunner):
    """CustomPhevalRunner Class."""

    input_dir: Path
    testdata_dir: Path
    tmp_dir: Path
    output_dir: Path
    config_file: Path
    version: str

    def prepare(self):
        """prepare method."""
        print("preparing")

    def run(self):
        """run"""

        print("running semphen...")
        #print(self.input_dir)
        #print(self.testdata_dir)
        #print(self.output_dir)
        #print(self.config_file)
        #print(self.version)
        #print(self.input_dir_config)
        
        config = SemphenConfigurations.model_validate(self.input_dir_config.tool_specific_configuration_options)
        print("config made...")
        run_semphen_local(input_dir=self.testdata_dir,
                          output_dir=self.output_dir,
                          config=config)
        print("semphen ran")

    def post_process(self):
        """post_process method."""
        print("post processing")
