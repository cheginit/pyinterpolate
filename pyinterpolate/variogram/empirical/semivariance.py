def temp_calc_point_to_point_distance(points_a, points_b):
    "temporary function for pt to pt distance estimation"
    from scipy.spatial.distance import cdist
    if points_b is None:
        distances = cdist(points_a, points_a, 'euclidean')
    else:
        distances = cdist(points_a, points_b, 'euclidean')
    return distances

def calculate_semivariance(points, step_size, max_range, is_weighted=False, direction=0, tolerance=0.1):
    """
    Function calculates semivariance from given points. In a default mode it calculates non-weighted and omnidirectional
        semivariance. User may provide weights to additionally weight points by a specific factor. User can calculate
        directional semivariogram with a specified tolerance.

    :param points: (numpy array) coordinates and their values and optionally weighs:
            [pt x, pt y, value, weight]
    :param step_size: (float) distance between lags within each points are included in the calculations,
    :param max_range: (float) maximum range of analysis,
    :param is_weighted: (bool) if True then parameter points must provide weights in the last column of an array,
    :param direction: (float) direction of semivariogram, values from 0 to 360 degrees:
        0 or 180: is NS direction,
        90 or 270 is EW direction,
        30 or 210 is NE-SW direction,
        120 or 300 is NW-SE direction,
    :param tolerance: (float) value in range (0-1) normalized to [0 : 0.5] to select tolerance of semivariogram.
        If tolerance is 0 then points must be placed at a single line with beginning in the origin of coordinate system
        and angle given by y axis and direction parameter. If tolerance is greater than 0 then semivariance is estimated
        from elliptical area with major axis with the same direction as the line for 0 tolerance and minor axis
        of a size:
        (tolerance * step_size)
        and major axis (pointed in NS direction):
        ((1 - tolerance) * step_size)
        and baseline point at a center of ellipse. Tolerance == 1 (normalized to 0.5) creates omnidirectional
        semivariogram.

    ## Semivariance

    It is a measure of dissimilarity between points over distance. In geography, we assume that the close observations
        tends to be similar. Distant observations are less and less similar up to the distance where influence of one
        point value into the other is negligible.

    We calculate the empirical semivariance as:

        (1)    g(h) = 0.5 * n(h)^(-1) * (SUM|i=1, n(h)|: [z(x_i + h) - z(x_i)]^2)

        where:
        h: lag,
        g(h): empirical semivariance for lag h,
        n(h): number of point pairs within a specific lag,
        z(x_i): point a (value of observation at point a),
        z(x_i + h): point b in distance h from point a (value of observation at point b).


    As an output we get array of lags h, semivariances g and number of points within each lag n.

    ## Weighted Semivariance

    For some cases we need to weight each point by specific factor. It is especially important for the semivariogram
        deconvolution and Poisson Kriging. We can weight observations by specific factors, for example the time effort
        for observations at specific locations (ecology) or population size at specific block (public health).
        Implementation of algorithm follows publications:

        1. A. Monestiez P, Dubroca L, Bonnin E, Durbec JP, Guinet C: Comparison of model based geostatistical methods
        in ecology: application to fin whale spatial distribution in northwestern Mediterranean Sea.
        In Geostatistics Banff 2004 Volume 2. Edited by: Leuangthong O, Deutsch CV. Dordrecht, The Netherlands,
        Kluwer Academic Publishers; 2005:777-786.
        2. B. Monestiez P, Dubroca L, Bonnin E, Durbec JP, Guinet C: Geostatistical modelling of spatial distribution
        of Balenoptera physalus in the northwestern Mediterranean Sea from sparse count data and heterogeneous
        observation efforts. Ecological Modelling 2006 in press.

    We calculate the weighted empirical semivariance as:

        (2)    g_w(h) = 0.5 * (SUM|i=1, n(h)|: w(h))^(-1) * ...
                            * (SUM|i=1, n(h)|: w(h) * z_w(h))

        (3)    w(h) = [n(x_i) * n(x_i + h)] / [n(u_i) + n(u_i + h)]

        (4)    z_w(h) = (z(x_i) - z(x_i + h))^2 - m'

        where:
        h: lag,
        g_w(h): weighted empirical semivariance for lag h,
        n(h): number of point pairs within a specific lag,
        z(x_i): point a (rate of specific process at point a),
        z(x_i + h): point b in distance h from point a (rate of specific process at point b),
        n(x_i): denominator value size at point a (time, population ...),
        n(x_i + h): denominator value size at point b in distance h from point a,
        m': weighted mean of rates.

    The output of weighted algorithm is the same as for non-weighted data: array of lags h, semivariances g and number
        of points within each lag n.

    ## Directional Semivariogram

    Assumption that our observations change in the same way in every direction is rarely true. Let's consider
        temperature. It changes from equator to poles, so in the N-S and S-N axes. The good idea is to test if
        our observations are correlated in a few different directions. The main difference between an omnidirectional
        semivariogram and a directional semivariogram is that we take into account a different subset of neighbors.
        The selection depends on the angle (direction) of analysis. You may imagine it like that:

        - Omnidirectional semivariogram: we test neighbors in a circle,
        - Directional semivariogram: we test neighbors within an ellipse.

        or graphically:

        - omnidirectional:

               ooooo
              oooxooo
               ooooo

        - directional (W-E):

              oooxooo

        - directional with some tolerance (N-S):

                 o
                 o
                oxo
                 o
                 o

    ## Examples:

    # TODO


    """

    # Data validity tests

    if is_weighted:


    pass
