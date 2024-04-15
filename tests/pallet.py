import pytest

from palet.color import Color, color_average
from palet.pallet import Pallet, ConversionPallet, maximize_by_average, minimize_by_average


@pytest.fixture
def pallet_object():
    return Pallet(
        Color.from_hex("#531380"),
        Color.from_hex("#d7820e"),
        Color.from_hex("#60d048"),
        Color.from_hex("#f8c630"),
    )


def test_const_pallet():
    assert Pallet() == Pallet()
    assert Pallet(Color.from_hex("fff")) == Pallet(Color.from_hex("fff"))
    assert Pallet(Color.from_hex("fff"), Color.from_hex("000")) == Pallet(Color.from_hex("000"), Color.from_hex("fff"))

    with pytest.raises(ValueError):
        Pallet(0)
        Pallet(0x1)
        Pallet((0, 1, 2, 3, 4, 5, 6, 7, 8))
        Pallet(0, 1, 2, 3, 45)
        Pallet(Pallet(Color.from_hex("fff")))

    assert Pallet() == Pallet()


def test_pallet_color_set(pallet_object):
    assert len(pallet_object.color_set) == len(pallet_object.colors)
    assert type(pallet_object.color_set) == set

    assert (83, 19, 128, 255) in pallet_object.color_set
    assert (215, 130, 14, 255) in pallet_object.color_set
    assert (96, 208, 72, 255) in pallet_object.color_set
    assert (248, 198, 48, 255) in pallet_object.color_set


def test_pallet_colors(pallet_object):
    assert len(pallet_object.color_set) == len(pallet_object.color_set)
    assert type(pallet_object.color_set) == set


def test_pallet_add(pallet_object):
    nc = Color.from_hex("fff")
    pallet_object.add(nc)
    assert nc in pallet_object
    assert nc in pallet_object.colors
    assert nc.rgba in pallet_object.color_set

    nc = (0, 0, 0, 255)
    pallet_object.add(nc)
    assert nc in pallet_object
    assert nc in pallet_object.color_set

    nc = 1
    with pytest.raises(ValueError):
        pallet_object.add(nc)


def test_pallet_remove(pallet_object):
    nc = Color.from_hex("531380")
    pallet_object.remove(nc)
    assert nc not in pallet_object
    assert nc not in pallet_object.colors
    assert nc.rgba not in pallet_object.color_set

    with pytest.raises(KeyError):
        nc = (83, 19, 128, 255)
        pallet_object.remove(nc)
        assert nc not in pallet_object
        assert nc not in pallet_object.color_set

    nc = (215, 130, 14, 255)
    pallet_object.remove(nc)
    assert nc not in pallet_object
    assert nc not in pallet_object.color_set

    nc = 1
    with pytest.raises(ValueError):
        pallet_object.add(nc)


def test_pallet_clear(pallet_object):
    pallet_object.clear()

    assert len(pallet_object) == 0
    assert len(pallet_object.colors) == 0
    assert len(pallet_object.color_set) == 0


def test_pallet_iter(pallet_object):
    for idx, pallet in enumerate(pallet_object):
        assert isinstance(pallet, Color)

    assert idx == len(pallet_object) - 1


def test_pallet_dlen(pallet_object):
    assert len(pallet_object) == len(pallet_object.colors)
    assert len(pallet_object) == len(pallet_object.color_set)


def test_pallet_deq(pallet_object):
    assert pallet_object == pallet_object
    assert pallet_object != Pallet()
    assert pallet_object == pallet_object.colors
    assert 0 != pallet_object
    assert 0x1212 != pallet_object
    assert [(255, 255, 255, 0), ] != pallet_object
    assert ((255, 255, 255, 0),) != pallet_object


def test_pallet_dor(pallet_object):
    assert pallet_object | pallet_object == pallet_object
    assert pallet_object | Pallet(Color.from_hex("fff")) != pallet_object

    with pytest.raises(TypeError):
        assert pallet_object | None
        assert pallet_object | 121
        assert pallet_object | 0x131


def test_pallet_dadd(pallet_object):
    assert pallet_object + pallet_object == pallet_object
    assert pallet_object + Pallet(Color.from_hex("fff")) != pallet_object

    pallet_object += Pallet(Color.from_hex("000"))
    assert pallet_object + Pallet(Color.from_hex("000")) == pallet_object

    with pytest.raises(TypeError):
        assert pallet_object + None
        assert pallet_object + 100
        assert pallet_object + 0x24


def test_pallet_dand(pallet_object):
    np = Pallet(Color.from_hex("FFF"))
    op = Pallet()

    assert pallet_object & pallet_object == pallet_object
    assert pallet_object.colors & pallet_object.colors == pallet_object.colors
    assert pallet_object & np == np & pallet_object
    assert pallet_object.colors & op.colors == op.colors  # Intersect with Empty Set

    with pytest.raises(TypeError):
        assert pallet_object & None
        assert pallet_object & set()
        assert pallet_object & Color()


def test_pallet_dsub(pallet_object):
    mp = Pallet(Color.from_hex("531380"))
    np = Pallet(Color.from_hex("FFF"))
    op = Pallet()

    assert pallet_object - pallet_object == op
    assert pallet_object.colors - pallet_object.colors == op.colors
    assert pallet_object - mp == Pallet(
        Color.from_hex("#d7820e"),
        Color.from_hex("#60d048"),
        Color.from_hex("#f8c630"),
    )
    assert pallet_object - np == pallet_object  # No Intersection
    assert pallet_object - np != np - pallet_object  # Not Commutative (ofc)
    assert pallet_object.colors - op.colors == pallet_object.colors  # Difference with Empty Set

    with pytest.raises(TypeError):
        assert pallet_object - None
        assert pallet_object - Color


def test_pallet_dcontains(pallet_object):
    assert Color.from_hex("f8c630") in pallet_object
    assert Color.from_hex("fff") not in pallet_object

    assert (96, 208, 72, 255) in pallet_object
    assert (96, 208, 72, 0) not in pallet_object

    assert 0 not in pallet_object
    assert None not in pallet_object
    assert 0x1 not in pallet_object
    assert 10000000000 not in pallet_object

    with pytest.raises(TypeError):
        assert pallet_object not in pallet_object


def test_pallet_union(pallet_object):
    mp = Pallet(Color.from_hex("531380"))
    np = Pallet(Color.from_hex("FFF"))

    assert pallet_object.union(pallet_object) == pallet_object
    assert pallet_object.union(Pallet()) == pallet_object
    assert pallet_object.union(mp) == pallet_object
    assert pallet_object.union(np) == np.union(pallet_object)


def test_pallet_difference(pallet_object):
    mp = Pallet(Color.from_hex("531380"))
    np = Pallet(Color.from_hex("FFF"))

    assert pallet_object.difference(pallet_object) == Pallet()
    assert pallet_object.difference(Pallet()) == pallet_object
    assert pallet_object.difference(mp) == Pallet(
        Color.from_hex("#d7820e"),
        Color.from_hex("#60d048"),
        Color.from_hex("#f8c630"),
    )
    assert pallet_object.difference(np) == pallet_object
    assert pallet_object.difference(np) != np.difference(pallet_object)


def test_pallet_intersection(pallet_object):
    mp = Pallet(Color.from_hex("531380"))
    np = Pallet(Color.from_hex("FFF"))

    assert pallet_object.intersection(pallet_object) == pallet_object
    assert pallet_object.intersection(Pallet()) == Pallet()
    assert pallet_object.intersection(mp) == mp.intersection(pallet_object)
    assert pallet_object.intersection(np) == Pallet()


def test_pallet_to_list(pallet_object):
    ptl = {Color.from_hex("#531380"),
           Color.from_hex("#d7820e"),
           Color.from_hex("#60d048"),
           Color.from_hex("#f8c630")}

    assert pallet_object.to_list() == list(ptl)
    assert len(pallet_object.to_list()) > 0


def test_pallet_to_dict(pallet_object):
    ptl = {Color.from_hex("#531380"),
           Color.from_hex("#d7820e"),
           Color.from_hex("#60d048"),
           Color.from_hex("#f8c630")}

    assert pallet_object.to_dict() == {x.hex: x.rgba for x in ptl}
    assert "#d7820e" in pallet_object.to_dict().keys()
