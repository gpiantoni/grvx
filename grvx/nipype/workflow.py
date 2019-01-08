from shutil import rmtree
from nipype import Workflow, config, logging, JoinNode

from boavus.workflow.corr_ieeg_fmri import workflow_corr_ieeg_fmri
from boavus.corr import function_corr_summary

from .bids import bids, SUBJECTS
from ..core.constants import NIPYPE_PATH, FREESURFER_PATH, PARAMETERS

LOG_PATH = NIPYPE_PATH / 'log'


config.update_config({
    'logging': {
        'log_directory': LOG_PATH,
        'log_to_file': True,
        },
    'execution': {
        'crashdump_dir': LOG_PATH,
        'keep_inputs': 'false',
        'remove_unnecessary_outputs': 'false',
        },
    })


def create_grvx_workflow(upsample=None, graymatter=None):

    w_subj = workflow_corr_ieeg_fmri(PARAMETERS, FREESURFER_PATH)

    bids.iterables = ('subject', SUBJECTS)

    summary = JoinNode(
        function_corr_summary,
        name='corr_fmri_ecog_summary',
        joinsource='bids',
        joinfield=('in_files', 'ecog_files', 'fmri_files'),
        )

    w = Workflow('grvx')
    w.base_dir = str(NIPYPE_PATH)

    w.connect(bids, 'subject', w_subj, 'input.subject')
    w.connect(bids, 'anat', w_subj, 'input.T1w')
    w.connect(bids, 'func', w_subj, 'input.bold')
    w.connect(bids, 'ieeg', w_subj, 'input.ieeg')
    w.connect(bids, 'elec', w_subj, 'input.electrodes')

    w.connect(w_subj, 'output.out_file', summary, 'in_files')
    w.connect(w_subj, 'output.ecog_file', summary, 'ecog_files')
    w.connect(w_subj, 'output.fmri_file', summary, 'fmri_files')

    w.write_graph(graph2use='flat')

    rmtree(LOG_PATH, ignore_errors=True)
    LOG_PATH.mkdir()
    logging.update_logging(config)

    return w
