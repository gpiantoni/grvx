from boavus.main import boavus
from .core.constants import (DATA_PATH,
                             Parameters_Json,
                             PARAMETERS,
                             OUTPUT_PATH,
                             ANALYSIS_PATH,
                             )


from .core.log import with_log


@with_log
def Corr_fMRI_to_Elec(lg, img_dir):

    PARAMETERS_JSON = Parameters_Json(PARAMETERS['corrfmri'])
    boavus([
        'ieeg',
        'corrfmri',
        '--output_dir',
        str(OUTPUT_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--bids_dir',
        str(DATA_PATH),
        '--parameters',
        PARAMETERS_JSON.name,
        '--log',
        'debug',
        ])
    PARAMETERS_JSON.delete()
