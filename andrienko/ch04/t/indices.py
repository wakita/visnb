import json
from pathlib import Path

import pandas as pd

def spi_hierarchy():
    'Excel の最後のシートに記載されているSPI指標の定義から階層構造を構成する'

    def rec(defs, keys):
        indices = list(defs.keys())[:3]
        dimensions = dict()
        for _, row in defs.iterrows():
            if pd.notna(row).all():
                dimension, component, name = row['Dimension'], row['Component'], row['Indicator name']
                if not dimension in dimensions: dimensions[dimension] = dict()
                components = dimensions[dimension]
                if not component in components: components[component] = []
                components[component].append(name)
        return dimensions

    return rec(pd.read_excel(str(Path(__file__).parent.parent / 'data' / 'spi2019.xlsx'),
                             sheet_name='Definitions', skiprows=[0]),
               'Region Name, Sub-region Name, Intermediate Region Name, Country or Area'.split(', '))


######################################################################
# Bokeh section

from bokeh.models import RadioButtonGroup
from bokeh.layouts import column

class IndexMenus():
    '階層化メニューの階層の沿った階層化メニュー'
    tree = spi_hierarchy()  # SPI指標の階層を表す木構造

    def __init__(self, doc):
        '''
        Attributes
        ----------
        view: Column
            階層化メニューウィジェット
        path: list of str
            階層化メニューの値から選択された項目のリスト
        '''

        def set_callback(choice, level):
            '''
            level番目のメニューchoiceの要素が選択されたとき(active)の挙動(on_change)を設定

            Parameters
            ----------
            choice :
                メニュー
            level :
                メニュー階層のレベル (0-index)

            Notes
            -----
            set_callback に choice, level を与えることで、これらを含む関数閉包を構成していることに注意
            '''
            def on_change(attr, old, new):
                if new is None: return  # This is the case when the active field of a widget is updated within the "update" method
                self.path = self.path[:level] + [choice.labels[new]]
                self._update()
            choice.on_change('active', on_change)

        def button_group(level):
            choice = RadioButtonGroup(labels=['None'], visible=False, active=None)
            set_callback(choice, level)
            return choice

        self.view = column(name='index_menus',
                           children=[button_group(level) for level in range(3)],
                           css_classes=['spix', 'spix-spi-view'],
                           sizing_mode='scale_width')
        self.path = []
        self._update()
        doc.add_root(self.view)

    def _update(self):
        print(' > '.join(self.path))  # 選択状態を表示する

        menu = self.view.children
        for level, choice in enumerate(menu):
            choice.visible = level <= len(self.path)
        menu[len(self.path)].active = None

        # 階層的な選択に沿って階層化メニューのラベルを更新
        t = self.tree
        menu[0].labels = sorted(t.keys())
        for active, choice in zip(self.path, menu[1:]):
            t = t[active]  # 階層構造から選択 (path) に沿って探索
            if type(t) == dict:  # 地域群の場合
                choice.labels = sorted(t.keys())
            else:  # 国と地域の場合は、それらを列挙表示する
                choice.visible = False
                for index in t: print(f' - {index}')
