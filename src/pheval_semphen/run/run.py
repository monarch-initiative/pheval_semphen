import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from packaging import version
from pheval.utils.file_utils import all_files

from pheval_semphen.prepare.tool_specific_configuration_options import SemphenConfigurations


def run_semphen_local(input_dir: Path,
                      output_dir: Path,
                      config: SemphenConfigurations) -> None:
    """
    Run Semphen locally
    """
    print("...running semphen")

    # Combine arguments into subprocess friendly command format
    subp_command = ["python",
                    config.path_to_semphen,
                    "rank-associations",
                    "-i", input_dir,
                    "-o", output_dir,
                    "-p", config.path_to_phenio]
    
    # Run semphen through subprocss
    subprocess.run(subp_command, shell=False)
