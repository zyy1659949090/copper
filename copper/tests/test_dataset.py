from __future__ import division
import os
import tempfile
import numpy as np
import pandas as pd
from copper.tests.utils import eq_
import copper


def test_create_empty():
    ds = copper.Dataset()
    eq_(ds.role, pd.Series())
    eq_(ds.type, pd.Series())
    eq_(ds.metadata.empty, True)
    eq_(ds.frame.empty, True)


def test_create_noempty():
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    eq_(ds.frame, df)
    eq_(len(ds.role), 10)
    eq_(len(ds.type), 10)
    eq_(len(ds.metadata), 10)
    eq_(ds.metadata['Role'], ds.role)
    eq_(ds.metadata['Type'], ds.type)


def test_set_metadata():
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    meta = ds.metadata

    meta['Role'][5] = ds.TARGET
    ds.metadata = meta
    eq_(ds.role[5], ds.TARGET)

    meta['Role'][5] = ds.INPUT
    ds.metadata = meta
    eq_(ds.role[5], ds.INPUT)

    meta['Type'][3] = ds.CATEGORY
    ds.metadata = meta
    eq_(ds.type[3], ds.CATEGORY)

    meta['Type'][3] = ds.NUMBER
    ds.metadata = meta
    eq_(ds.type[3], ds.NUMBER)


def test_save_load_metadata():
    tempdir = tempfile.gettempdir()
    # Save
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    ds.role[2] = ds.TARGET
    ds.role[7] = ds.IGNORE
    ds.type[1] = ds.CATEGORY
    ds.type[5] = ds.CATEGORY
    ds.metadata.to_csv(os.path.join(tempdir, 'metadata.csv'))

    # Load
    ds2 = copper.Dataset(df)
    loaded_meta = pd.read_csv(os.path.join(tempdir, 'metadata.csv'))
    loaded_meta = loaded_meta.set_index('Columns')
    ds2.metadata = loaded_meta
    eq_(ds2.role[2], ds.TARGET)
    eq_(ds2.role[7], ds.IGNORE)
    eq_(ds2.type[1], ds.CATEGORY)
    eq_(ds2.type[5], ds.CATEGORY)


def test_get_column():
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    eq_(ds[0], df[0])
    eq_(ds[5], df[5])
    eq_(ds[9], df[9])


def test_set_column():
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    new_col = np.random.rand(10, 1)
    eq_(ds[3].values, df[3].values)
    ds[3] = new_col
    eq_(ds[[3]].values, new_col)


def test_transform_to_number_ints():
    sol = np.arange(100)
    strings = np.array(['a(%f)' % d for d in sol])
    df = pd.DataFrame(strings)
    ds = copper.Dataset(df)
    ds.type[0] = ds.NUMBER
    ds.update()
    eq_(sol, ds[0].values)


def test_transform_to_number_float():
    sol = np.arange(100) / 100
    strings = np.array(['a(%f)' % d for d in sol])
    df = pd.DataFrame(strings)
    ds = copper.Dataset(df)
    ds.type[0] = ds.NUMBER
    ds.update()
    eq_(sol, ds[0].values)


def test_filter_role():
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    ds.role[[0, 2, 4, 5, 9]] = ds.IGNORE
    eq_(ds.filter(role=ds.INPUT), ds[[1, 3, 6, 7, 8]])

    ds.role[:] = ds.IGNORE
    ds.role[[1, 3, 4, 6, 8]] = ds.INPUT
    eq_(ds.filter(role=ds.INPUT), ds[[1, 3, 4, 6, 8]])

    ds.role[[2, 9]] = ds.TARGET
    eq_(ds.filter(role=ds.TARGET), ds[[2, 9]])

    eq_(ds.filter(role=[ds.INPUT, ds.TARGET]), ds[[1, 2, 3, 4, 6, 8, 9]])

    eq_(ds.filter(), df)


def test_filter_type():
    df = pd.DataFrame(np.random.rand(10, 10))
    ds = copper.Dataset(df)
    ds.type[[0, 2, 4, 5, 9]] = ds.CATEGORY
    eq_(ds.filter(type=ds.CATEGORY), ds[[0, 2, 4, 5, 9]])

    ds.type[:] = ds.CATEGORY
    ds.type[[1, 3, 6, 7, 9]] = ds.NUMBER
    eq_(ds.filter(type=ds.NUMBER), ds[[1, 3, 6, 7, 9]])

    eq_(ds.filter(type=[ds.NUMBER, ds.CATEGORY]), df)

    eq_(ds.filter(), df)


def test_filter_both():
    df = pd.DataFrame(np.random.rand(5, 5))
    ds = copper.Dataset(df)
    ds.role[:] = ds.IGNORE

    ds.role[2] = ds.INPUT
    ds.type[2] = ds.CATEGORY
    eq_(ds.filter(role=ds.INPUT, type=ds.CATEGORY), df[[2]])

    ds.role[4] = ds.INPUT
    ds.type[4] = ds.CATEGORY
    eq_(ds.filter(role=ds.INPUT, type=ds.CATEGORY), df[[2, 4]])

    eq_(ds.filter(role=ds.IGNORE, type=ds.NUMBER), df[[0, 1, 3]])

    ds.role[4] = ds.IGNORE
    eq_(ds.filter(role=ds.INPUT, type=ds.CATEGORY), df[[2]])

    eq_(ds.filter(), df)

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__, '-vs', '--nologcapture'], exit=False)
