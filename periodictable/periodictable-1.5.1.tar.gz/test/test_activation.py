import numpy as np

from periodictable.activation import Sample, ActivationEnvironment

def test():
    # This is not a very complete test of the activation calculator.
    # Mostly just a smoke test to see that things run and produce the
    # same answers as before.  The target values have been checked
    # against the NCNR internal activation calculator spreadsheet.  The
    # values herein differ slightly from the spreadsheet since we are using
    # different tables for materials and different precision on our
    # constants.

    ## Print a table of flux vs. activity so we can debug the
    ## precision_correction value in the activity() function.
    ## Note that you also need to uncomment the print statement
    ## at the end of activity() that shows the column values.
    #sample = Sample('Au', mass=1)
    #for fluence in np.logspace(3,20,20-3+1):
    #    env = ActivationEnvironment(fluence=fluence)
    #    sample.calculate_activation(env, rest_times=[0])
    #raise Hell

    def _get_Au_activity(fluence=1e5):
        sample = Sample('Au', mass=1)
        env = ActivationEnvironment(fluence=fluence)
        sample.calculate_activation(env, rest_times=[0])
        for product, activity in sample.activity.items():
            if str(product.daughter) ==  'Au-198':
                return activity[0]
        else:
            raise RuntimeError("missing activity from Au-198")


    act1 = _get_Au_activity(fluence=1e5)
    act2 = _get_Au_activity(fluence=1e8)
    assert act2 > act1


    # spreadsheet results
    # Co-60m+  5186.888  98.878   2.751e-38
    # Co-61    2.689e-8  1.767e-8 1.127e-12
    # Co-60    1.550322  1.550299 1.549764
    # Co-61    5.695e-8  3.741e-8 2.386e-12
    sample = Sample('Co', mass=10)
    env = ActivationEnvironment(fluence=1e8)
    sample.calculate_activation(env, rest_times=[0, 1, 24])
    for product, activity in sample.activity.items():
        if str(product.daughter) == 'Co-60m+':
            assert np

