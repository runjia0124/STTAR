#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright 2021 The NiPreps Developers <nipreps@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
import sys
sys.path.append('/Users/runjia/Code/STTAR')
"""STTAR dMRI preprocessing workflow."""
# from .. import config Edited
from sttar import config

def main():
    """Entry point."""
    import os
    import sys
    import gc
    from multiprocessing import Process, Manager
    # from .parser import parse_args Edited
    from sttar.cli.parser import parse_args
    # from ..utils.bids import write_derivative_description Edited
    from sttar.utils.bids import write_derivative_description

    parse_args()

    # IGNORE at this point
    popylar = None
    if not config.execution.notrack:
        import popylar
        from ..__about__ import __ga_id__

        config.loggers.cli.info(
            "Your usage of dmriprep is being recorded using popylar (https://popylar.github.io/). ",  # noqa
            "For details, see https://nipreps.github.io/dmriprep/usage.html. ",
            "To opt out, call dmriprep with a `--notrack` flag",
        )
        popylar.track_event(__ga_id__, "run", "cli_run")

    # CRITICAL Save the config to a file. This is necessary because the execution graph
    # is built as a separate process to keep the memory footprint low. The most
    # straightforward way to communicate with the child process is via the filesystem.
    config_file = config.execution.work_dir / ".dmriprep.toml"
    config.to_filename(config_file)

    # CRITICAL Call build_workflow(config_file, retval) in a subprocess.
    # Because Python on Linux does not ever free virtual memory (VM), running the
    # workflow construction jailed within a process preempts excessive VM buildup.
    with Manager() as mgr:
        # from .workflow import build_workflow Edited
        from sttar.cli.workflow import build_workflow

        retval = mgr.dict()
        p = Process(target=build_workflow, args=(str(config_file), retval))
        p.start()
        p.join()

        retcode = p.exitcode or retval.get("return_code", 0)
        dmriprep_wf = retval.get("workflow", None)

if __name__ == '__main__':
    main()