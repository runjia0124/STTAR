"""STTAR base processing workflows."""
import sys
import os
from copy import deepcopy

from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu

from niworkflows.engine.workflows import LiterateWorkflow as Workflow
from niworkflows.interfaces.bids import BIDSInfo, BIDSFreeSurferDir
from niworkflows.utils.misc import fix_multi_T1w_source_name
from niworkflows.utils.spaces import Reference

from sttar import config

def init_sttar_wf():
    """
    Create the base workflow.

    This workflow organizes the execution of *STTAR*, with a sub-workflow for
    each subject. If FreeSurfer's recon-all is to be run, a FreeSurfer derivatives folder is
    created and populated with any needed template subjects.

    Workflow Graph
        .. workflow::
            :graph2use: orig
            :simple_form: yes

            from dmriprep.config.testing import mock_config
            from dmriprep.workflows.base import init_dmriprep_wf
            with mock_config():
                wf = init_dmriprep_wf()

    """
    sttar_wf = Workflow(name="sttar_wf")
    sttar_wf.base_dir = config.execution.work_dir

    freesurfer = config.workflow.run_reconall
    if freesurfer:
        fsdir = pe.Node(
            BIDSFreeSurferDir(
                derivatives=config.execution.output_dir,
                freesurfer_home=os.getenv("FREESURFER_HOME"),
                spaces=config.workflow.spaces.get_fs_spaces(),
            ),
            name=f"fsdir_run_{config.execution.run_uuid.replace('-', '_')}",
            run_without_submitting=True,
        )
        if config.execution.fs_subjects_dir is not None:
            fsdir.inputs.subjects_dir = str(config.execution.fs_subjects_dir.absolute())


if __name__ == '__main__':
    init_sttar_wf()