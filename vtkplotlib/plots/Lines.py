# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 20:32:50 2019
#
# @author: Brénainn Woodsend
#
#
# Lines.py plots 3D lines through some points.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================

from builtins import super

import vtk
import numpy as np
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import ConstructedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib import _numpy_vtk, nuts_and_bolts
from vtkplotlib.plots.polydata import join_line_ends



class Lines(ConstructedPlot):
    """Plots a line passing through an array of points.

    :param vertices: The points to plot through.
    :type vertices: np.ndarray of shape (n, 3)

    :param color: The color(s) of the plot, defaults to white.
    :type color: str, 3-tuple, 4-tuple, np.ndarray optional

    :param opacity: The translucency of the plot, 0 is invisible, 1 is solid, defaults to solid.
    :type opacity: float, optional

    :param line_width: The thickness of the lines, defaults to 1.0.
    :type line_width: float, optional

    :param join_ends: If true, join the 1st and last points to form a closed loop, defaults to False.
    :type join_ends: bool, optional

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure, optional


    :return: A lines object.
    :rtype: vtkplotlib.plots.Lines.Lines

    If `vertices` is 3D then multiple seperate lines are plotted. Currently it
    can only do one color for the whole thing. This can be used to plot meshes
    as wireframes.


    .. code-block:: python

        import vtkplotlib as vpl
        from stl.mesh import Mesh

        mesh = Mesh.from_file(vpl.data.get_rabbit_stl())
        vertices = mesh.vectors

        vpl.plot(vertices, join_ends=True, color="dark red")
        vpl.show()

    If `color` is an `np.ndarray` then a color per vertex is implied. The shape
    of `color` relative to the shape of `vertices` determines whether the
    colors should be interpreted as scalars, texture coordinates or RGB values.
    If `color` is either a list, tuple, or str then it is one color for the
    whole plot.


    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create an octogon, using `t` as scalar values.

        t = np.arange(0, 1, .125) * 2 * np.pi
        vertices = vpl.zip_axes(np.cos(t),
                                np.sin(t),
                                0)

        vpl.plot(vertices,
                 line_width=6,
                 join_ends=True,
                 color=t)

        vpl.show()

    """

    def __init__(self, vertices, color=None, opacity=None, line_width=1.0, join_ends=False, fig="gcf"):
        super().__init__(fig)


        self.shape = ()
        self.join_ends = join_ends

        self.vertices = vertices

#        assert np.array_equal(points[args], vertices)


        self.add_to_plot()

        self.opacity = opacity
        self.color = color
        self.line_width = line_width


    @property
    def line_width(self):
        return self.property.GetLineWidth()

    @line_width.setter
    def line_width(self, width):
        self.property.SetLineWidth(width)

    @property
    def vertices(self):
        return self.polydata.points.reshape(self.shape)

    @vertices.setter
    def vertices(self, vertices):
        vertices = np.asarray(vertices)
        self.polydata.points = vertices.reshape((-1, 3))

        if vertices.shape == self.shape:
            return

        self.shape = vertices.shape
        args = np.arange(np.prod(self.shape[:-1])).reshape((-1, self.shape[-2]))

        if self.join_ends:
            self.polydata.lines = join_line_ends(args)
        else:
            self.polydata.lines = args

    @property
    def color(self):
        colors = self.polydata.point_colors
        if colors is not None:
            return colors.reshape(self.shape[:-1] + (-1,))

        return super().color

    @color.setter
    def color(self, c):
        if isinstance(c, np.ndarray):
            if c.shape == self.shape[:-1]:
                c = c[..., np.newaxis]
            assert self.shape[:-1] == c.shape[:-1]
            self.polydata.point_colors = c.reshape((-1, c.shape[-1]))
            self.set_scalar_range(c)
            self.mapper.SetScalarModeToUsePointData()
        else:
            ConstructedPlot.color.fset(self, c)
            self.polydata.point_colors = None





def test():
    import vtkplotlib as vpl

    t = np.arange(0, 1, .001) * 2 * np.pi
    vertices = np.array([np.cos(2 * t),
                         np.sin(3 * t),
                         np.cos(5 * t) * np.sin(7 *t)]).T
    vertices = np.array([vertices, vertices + 2])

    t = np.arange(0, 1, .125) * 2 * np.pi
    vertices = vpl.zip_axes(np.cos(t),
                            np.sin(t),
                            0)

#    vertices = np.random.uniform(-30, 30, (3, 3))
#    color = np.broadcast_to(t, vertices.shape[:-1])

    self = vpl.plot(vertices, line_width=6, join_ends=True,
                    color=t)
#    self.polydata.point_scalars = vpl.geometry.distance(vertices)
#    self.polydata.point_colors = t
    fig = vpl.gcf()
    fig.background_color = "grey"
    self.add_to_plot()
    vpl.show()

    return self


if __name__ == "__main__":
    self = test()
