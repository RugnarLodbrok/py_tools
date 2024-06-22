from py_tools.class_property import classproperty


def test_classproperty():
    class A:
        @classmethod
        @classproperty
        def p(cls):
            return 'value'

    assert A.p == 'value'
