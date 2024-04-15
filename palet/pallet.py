from __future__ import annotations

import random
from typing import List, Dict

from palet.color import Color, color_average
from palet.metric import euclidean_distance


class Pallet:
    """
    Pallet (Set of Colors)
    """

    def __init__(self, *colors: Color):
        self._colors = set()

        for color in colors:
            self.add(color)

    @property
    def color_set(self):
        """
        Colors as Set of RGBA Tuple

        :return: set
        """
        return {x.rgba for x in self._colors}

    @property
    def colors(self):
        """
        Colors as Set of Color Object

        :return:
        """
        return self._colors

    def add(self, color: Color | tuple):
        """
        Add Color to Pallet Set

        :param color: Color Object or Tuple (R,G,B,*A)
        :return:
        """
        if isinstance(color, Color):
            self.colors.add(color)
            return

        if isinstance(color, tuple):
            self.colors.add(Color(*color))
            return

        raise ValueError(f"Unable to add color to Pallet of type `{type(color)}`")

    def remove(self, color: Color | tuple):
        """
        Remove Color from Pallet Set

        :param color: Color Object or Tuple (R,G,B,*A)
        :return:
        """
        if isinstance(color, Color):
            self.colors.remove(color)
            return

        if isinstance(color, tuple):
            cn = Color(*color)
            self.colors.remove(cn)
            return

        raise ValueError(f"Unable to remove color to Pallet by type `{type(color)}`")

    def clear(self):
        """
        Clear the Pallet Set

        :return:
        """
        self._colors = set()

    def __iter__(self):
        return iter(self.colors)

    def __len__(self):
        return len(self.colors)

    def __eq__(self, other):
        if isinstance(other, Pallet):
            return self.colors == other.colors

        if isinstance(other, set):
            return self.colors == other

        # TODO: Implement New Instances : (Tuple, List) as List of RGB/A

        return False

    def __or__(self, other):
        if isinstance(other, Pallet):
            return Pallet(*self.colors | other.colors)

        # TODO: Implement New Instances : (Colors, Tuple, List, None) as RGB/A

        raise TypeError(f'Unsupported operation with class "{type(other)}". Must be instance of {self.__class__}')

    def __add__(self, other):
        return self.__or__(other)

    def __and__(self, other):
        if isinstance(other, Pallet):
            return Pallet(*(self.colors & other.colors))

        # TODO: Implement New Instances : (Tuple, List, None) as List of Colors or RGB/A

        raise TypeError(f'Unsupported operation with class "{type(other)}". Must be instance of {self.__class__}')

    def __sub__(self, other):
        if isinstance(other, Pallet):
            return Pallet(*self.colors.difference(other.colors))

        # TODO: Implement New Instances : (Tuple, List, None) as List of Colors or RGB/A

        raise TypeError(f'Unsupported operation with class "{type(other)}". Must be instance of {self.__class__}')

    def __contains__(self, item):
        if isinstance(item, tuple) or isinstance(item, list):
            return item in self.color_set

        return item in self.colors

    def union(self, other: Pallet):
        """
        Union with Other Pallet Set

        :param other: Pallet Object
        :return: Pallet Object
        """
        return self.__add__(other)

    def difference(self, other: Pallet):
        """
        Difference between Other Pallet Set

        :param other: Pallet Object
        :return: Pallet Object
        """
        return self.__sub__(other)

    def intersection(self, other: Pallet):
        """
        Intersection between Other Pallet Set

        :param other: Pallet Object
        :return: Pallet Object
        """
        return self.__and__(other)

    def to_list(self) -> List[Color]:
        """
        Returns a List Object of Set

        :return: list
        """
        return list(self.colors)

    def to_dict(self) -> Dict[str, tuple]:
        """
        Returns a Dict Object of Set {Hex : (R, G, B, A)}

        :return: dict
        """
        return {x.hex: x.rgba for x in self.colors}


class ConversionPallet:

    def __init__(self, cmap: dict[tuple, tuple] = None):
        self.cmap = cmap

    @classmethod
    def map(cls, pa: Pallet, pb: Pallet, algo=euclidean_distance, sim=min):
        cmap = {}

        pal = pa.to_list()
        pbl = pb.to_list()
        for ca in pal:
            dist = []
            for cb in pbl:
                dist.append(algo(ca.rgba, cb.rgba))
            min_dist = sim(dist)
            min_pos = dist.index(min_dist)
            cmap[ca] = pbl[min_pos]

        return cls(cmap=cmap)

    @classmethod
    def random(cls, pa: Pallet, pb: Pallet, seed=None):
        cmap = {}

        if seed:
            random.seed(seed)

        pal = pa.to_list()
        pbl = pb.to_list()
        for ca in pal:
            cmap[ca] = random.choice(pbl)

        return cls(cmap=cmap)

    def __getitem__(self, item):
        return self.cmap[item]

    def __contains__(self, item):
        return item in self.cmap.keys()

    def to_dict(self):
        return {
            k.rgba: v.rgba for k, v in self.cmap.items()
        }


def maximize_by_average(pallet: Pallet | list) -> Pallet:
    """
    Maximize Pallet by Average between Colors (in Pallet List Order)

    :param pallet: Pallet or List of Colors
    :return: Pallet
    """

    p_list = pallet
    if isinstance(pallet, Pallet):
        p_list = pallet.to_list()

    np_list = []

    for idx in range(len(p_list)):
        if idx == 0:
            np_list.append(p_list[idx])
            continue

        ca = color_average(np_list[-1], p_list[idx])
        np_list.append(ca)
        np_list.append(p_list[idx])

    return Pallet(*np_list)


def minimize_by_average(pallet: Pallet | list) -> Pallet:
    """
    Maximize Pallet by Average between Colors (in Pallet List Order)

    :param pallet: Pallet or List of Colors
    :return: Pallet
    """

    p_list = pallet
    if isinstance(pallet, Pallet):
        p_list = pallet.to_list()

    np_list = []

    for idx in range(len(p_list)):
        if idx == 0:
            continue

        ca = color_average(p_list[-1], p_list[idx])
        np_list.append(ca)

    return Pallet(*np_list)
