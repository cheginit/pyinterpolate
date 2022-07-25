import unittest

import numpy as np

from pyinterpolate.kriging.models.block.centroid_based_poisson_kriging import centroid_poisson_kriging
from pyinterpolate.processing.preprocessing.blocks import Blocks, PointSupport
from pyinterpolate.variogram import TheoreticalVariogram

DATASET = '../samples/regularization/cancer_data.gpkg'
VARIOGRAM_MODEL_FILE = '../samples/regularization/regularized_variogram.json'
POLYGON_LAYER = 'areas'
POPULATION_LAYER = 'points'
POP10 = 'POP10'
GEOMETRY_COL = 'geometry'
POLYGON_ID = 'FIPS'
POLYGON_VALUE = 'rate'
MAX_RANGE = 400000
NN = 32


def select_unknown_blocks_and_ps(areal_input, point_support, block_id):

    ar_x = areal_input.cx
    ar_y = areal_input.cy
    ar_val = areal_input.value_column_name
    ps_val = point_support.value_column
    ps_x = point_support.x_col
    ps_y = point_support.y_col
    idx_col = areal_input.index_column_name

    areal_input = areal_input.data.copy()
    point_support = point_support.point_support.copy()

    sample_key = np.random.choice(list(point_support[block_id].keys()))

    unkn_ps = point_support[point_support[block_id] == sample_key]
    known_poses = point_support[point_support[block_id] != sample_key]
    known_poses.rename(columns={
        ps_x: 'x', ps_y: 'y', ps_val: 'ds', idx_col: 'index'
    }, inplace=True)

    unkn_area = areal_input[areal_input[block_id] == sample_key][[ar_x, ar_y, ar_val]].values
    known_areas = areal_input[areal_input[block_id] != sample_key]
    known_areas.rename(columns={
        ar_x: 'x', ar_y: 'y', ar_val: 'ds', idx_col: 'index'
    }, inplace=True)

    return known_areas, known_poses, unkn_area, unkn_ps


AREAL_INPUT = Blocks()
AREAL_INPUT.from_file(DATASET, value_col=POLYGON_VALUE, index_col=POLYGON_ID, layer_name=POLYGON_LAYER)
POINT_SUPPORT_INPUT = PointSupport()
POINT_SUPPORT_INPUT.from_files(point_support_data_file=DATASET,
                               blocks_file=DATASET,
                               point_support_geometry_col=GEOMETRY_COL,
                               point_support_val_col=POP10,
                               blocks_geometry_col=GEOMETRY_COL,
                               blocks_index_col=POLYGON_ID,
                               use_point_support_crs=True,
                               point_support_layer_name=POPULATION_LAYER,
                               blocks_layer_name=POLYGON_LAYER)

AREAL_INP, PS_INP, UNKN_AREA, UNKN_PS = select_unknown_blocks_and_ps(AREAL_INPUT, POINT_SUPPORT_INPUT, POLYGON_ID)

THEORETICAL_VARIOGRAM = TheoreticalVariogram()
THEORETICAL_VARIOGRAM.from_json(VARIOGRAM_MODEL_FILE)


class TestCentroidPK(unittest.TestCase):

    def test_flow_1(self):
        pk_model = centroid_poisson_kriging(semivariogram_model=THEORETICAL_VARIOGRAM,
                                            blocks=AREAL_INP,
                                            point_support=PS_INP,
                                            unknown_block=UNKN_AREA,
                                            unknown_block_point_support=UNKN_PS,
                                            number_of_neighbors=NN,
                                            max_neighbors_radius=MAX_RANGE)
        self.assertTrue(pk_model)

    def test_flow_2(self):
        known_blocks = {
            'geometry': None,
            'data': np.array([
                [1.0, 1, 1, 100],
                [2.0, 0, 1, 100],
                [3.0, 1, 0, 200],
                [4.0, 5, 1, 500],
                [5.0, 4, 2, 800]
            ]),
            'info': None
        }

        ps = {
            'data': {
                1.0: np.array([
                    [0.9, 1.1, 1000],
                    [1.1, 0.9, 2000],
                    [0.8, 1.2, 1000]
                ]),
                2.0: np.array([
                    [-0.1, 1.1, 300],
                    [0.1, 1, 400]
                ]),
                3.0: np.array([
                    [0.9, -0.2, 100],
                    [1.1, -0.2, 200],
                    [1.1, 0.2, 400],
                    [0.9, 0.2, 200]
                ]),
                4.0: np.array([
                    [4.9, 0.9, 200],
                    [4.9, 1.1, 1000],
                    [5.1, 0.9, 8000]
                ]),
                5.0: np.array([
                    [3.8, 2.3, 600],
                    [4.2, 1.7, 1000]
                ])
            },
            'info': None
        }

        ublock = np.array([6.0, 3, 1])
        u_ps = np.array([
            [2.8, 0.9, 200],
            [3.2, 1.1, 400]
        ])

        pk_model = centroid_poisson_kriging(semivariogram_model=THEORETICAL_VARIOGRAM,
                                            blocks=known_blocks,
                                            point_support=ps,
                                            unknown_block=ublock,
                                            unknown_block_point_support=u_ps,
                                            number_of_neighbors=3,
                                            max_neighbors_radius=3)
        self.assertTrue(np.array_equal([int(x) for x in pk_model], [6, 399, 0]))
