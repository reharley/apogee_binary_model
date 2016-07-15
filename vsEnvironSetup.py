import os

def setVariables():
    # These are the environment variables that are required for apogee to run
    # Contains the path to the top-level directory that will be used to (selectively) mirror the SDSS SAS
    mirrorEnv = 'SDSS_LOCAL_SAS_MIRROR'
    mirrorPath = '/Users/harleyr/Documents/test_directory/data_mirror'
    # Contains the APOGEE reduction version (e.g., v304 for DR10, v402 for DR11, v603 for DR12, l30e.2 for DR13)
    resultsEnv = 'RESULTS_VERS'
    resultsVers = 'v603'
    # APOKASC catalog version
    apogeeEnv = 'APOGEE_APOKASC_REDUX'
    apogeeVers = 'v6.2a'
    # Custom path for VS code to run properly.
    pathEnv = 'PATH'
    pathVal = '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin:/Library/TeX/texbin'

    # Directly assigns these environment variables.
    # TODO: Actually make these permanent...
    os.environ[mirrorEnv] = mirrorPath
    os.environ[resultsEnv] = resultsVers
    os.environ[apogeeEnv] = apogeeVers
    os.environ[pathEnv] = pathVal
    print('Environment vairables set')