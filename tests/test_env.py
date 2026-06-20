"""Smoke test: verify the analytics core is installed and importable."""

import polars as pl
import pydantic
import scipy
import sklearn
import statsmodels


def test_core_imports() -> None:
    assert pl.__version__
    assert pydantic.VERSION
    assert scipy.__version__
    assert sklearn.__version__
    assert statsmodels.__version__
