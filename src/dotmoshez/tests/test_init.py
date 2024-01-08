import unittest
from hamcrest import assert_that, contains_string

from .. import __version__
from .. import clean_ipynb
from .. import init_py
from .. import git_extras
from .. import ssh


class TestInit(unittest.TestCase):
    def test_version(self):
        assert_that(__version__, contains_string("."))

    def test_clean_ipynb(self):
        assert_that(clean_ipynb.__doc__ or "", contains_string(""))

    def test_init_py(self):
        assert_that(init_py.__doc__ or "", contains_string(""))

    def test_ssh(self):
        assert_that(ssh.__doc__ or "", contains_string(""))

    def test_git_extras(self):
        assert_that(git_extras.__doc__ or "", contains_string(""))
