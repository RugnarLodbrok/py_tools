import pytest


# @pytest.mark.skip('abstract')
class TestPoly:
    __test__ = False

    def test_go(self, poly_value):
        assert poly_value == 1


class TestChild(TestPoly):
    __test__ = True

    @pytest.fixture()
    def poly_value(self):
        return 1
