# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 13:01:28 2019

@author: Brénainn Woodsend


colors.py
Shamelessly steals matplotlib's color library. Functions for handling different
color types.
Copyright (C) 2019  Brénainn Woodsend

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import numpy as np
from matplotlib import colors


mpl_colors = {}
mpl_colors.update(colors.BASE_COLORS)
for dic in (colors.CSS4_COLORS, colors.TABLEAU_COLORS, colors.XKCD_COLORS):
    for (key, val) in dic.items():
        mpl_colors[key.split(":")[-1]] = colors.hex2color(val)


def process_color(color=None, opacity=None):
    """This is designed to handle all the different ways a color and/or 
    opacity can be given.
    
    'color' accepts either:
        A string color name. e.g "r" or "red". This uses matplotlib's 
        named color libraries. See there or vtkplotlib.BasePlot.mpl_colors for
        a full list of names.
        
        Or an html hex string in the form "#RRGGBB". (An alpha here is silently ignored.)
        
        Or any iterable of length 3 or 4 representing
            (r, g, b) or (r, g, b, alpha)
        r, g, b, alpha can be from 0 to 1 or from 0 to 255 (inclusive).
        Conventionally if they are from 0 to 1 they should be floats and if they
        are from 0 to 255 they should be ints. But this is so often not the 
        case that this rule is useless. This function divides by 255 if it sees
        anything greater than 1. Hence from 0 to 1 is the preferred format.
        
    'opacity':
        An scalar like the numbers for 'color'.'opacity' overides alpha
        if alpha provided in 'color'.
                
"""
    
    color_out = None
    opacity_out = None
    
    if color is not None:
        if isinstance(color, str):
            if color[0] == "#":
                color = colors.hex2color(color)
            else:
                color = mpl_colors[color]

        color = np.asarray(color)
        if color.dtype == int and color.max() > 1:
            color = color / 255.
            if opacity is not None:
                opacity /= 255

        if len(color) == 4:
            opacity_out = color[3]
            color = np.array(color[:3])
            
        color_out = color

    if opacity is not None:
        opacity_out = opacity
        

    return color_out, opacity_out







if __name__ == "__main__":
    pass