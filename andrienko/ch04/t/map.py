from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

pd.options.display.precision = 2

import json

from bokeh.plotting import figure, show, output_notebook
from bokeh.models import *
from bokeh.tile_providers import get_provider, Vendors

from bokeh.plotting import figure, output_notebook, show
from bokeh.models import *
from bokeh.transform import factor_cmap

from colormath.color_objects import ColorBase, sRGBColor as sRGB, LabColor as Lab
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# sRGB
sRGB.hex = lambda c: c.get_rgb_hex()
sRGB.clamp = lambda c: sRGB(*[c.clamped_rgb_r, c.clamped_rgb_g, c.clamped_rgb_b])
ColorBase.values = ColorBase.get_value_tuple

# 色変換
ColorBase.sRGB = lambda c: c if isinstance(c, sRGB) else convert_color(c, sRGB)
ColorBase.Lab  = lambda c: c if isinstance(c, Lab)  else convert_color(c, Lab)

# 色距離
ColorBase.delta = lambda c1, c2: delta_e_cie2000(c1.Lab(), c2.Lab())

labs = [np.array([60, 60 * np.cos(theta), 60 * np.sin(theta)])
        for theta in np.linspace(0, 2 * np.pi, num=4)[:-1]]
print(labs)
print([Lab(*lab).sRGB().hex() for lab in labs])

SPI = Needs, Wellbeing, Opportunity = ['Basic Human Needs', 'Foundations of Wellbeing', 'Opportunity']
spi2019 = pd.read_excel('../data/spi2019.xlsx', sheet_name='2019')[['Country', 'Code'] + SPI].fillna(0)
spi2019 = spi2019[spi2019['Country'] != 'World']

mean, std = spi2019.mean('rows'), np.sqrt(spi2019.std('rows'))
spi2019['N'], spi2019['W'], spi2019['O'] = [
    ((spi2019[i] - mean[i]) / std[i] * 7 + 50).clip(0, 100) / 100
    for i in SPI]
#print(spi2019[['Country', 'N', 'W', 'O']].head(50))

def color(c):
    lab = (labs[0] * c['N'] + labs[1] * c['W'] + labs[2] * c['O']) / 3
    return Lab(*lab).sRGB().hex()
spi2019['Color'] = spi2019.apply(color, axis='columns')
print(spi2019[spi2019['Country'].isin(['Japan', 'China'])])

world = gpd.read_file('data/world.geo.json/countries.geo.json').merge(spi2019, left_on='id', right_on='Code')

# range bounds supplied in web mercator coordinates
class Map():
    def __init__(self, doc):

        p = figure(width=900, height=600, sizing_mode='scale_both')
        glyphs = p.add_glyph(GeoJSONDataSource(geojson=world.to_json()),
                             Patches(xs='xs', ys='ys',
                                     fill_color='Color', line_color='#c0c0c0', line_width=.5))
        doc.add_root(Column(name='map', children=[p], sizing_mode='scale_both'))

        '''
        f = figure(x_range=(-3900000, 37000000), y_range=(-500000, 500000),
                   x_axis_type="mercator", y_axis_type="mercator", sizing_mode='scale_both')
        f.add_tile(tile_provider)
        doc.add_root(Column(name='map', children=[f], sizing_mode='scale_both'))
        '''
