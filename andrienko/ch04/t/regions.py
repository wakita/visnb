######################################################################
# Load the United Nation countries and regions dataset
# The data was obtained from: https://unstats.un.org/unsd/methodology/m49/

from pathlib import Path
import pandas as pd

def UN_regions():
    def rec(db, keys):
        key = keys[0]
        keys = keys[1:]
        regions = set(db[key].dropna())
        if len(regions) == 0: return rec(db, keys)
        if len(keys) == 0: return regions
        d = dict(_type=key)
        for region in regions:
            d[region] = rec(db[db[key] == region], keys)
        return d

    return rec(pd.read_excel(str(Path(__file__).parent.parent / 'data' / 'UNSD-M49.xlsx')),
               'Region Name, Sub-region Name, Intermediate Region Name, Country or Area'.split(', '))


######################################################################
# Bokeh section

from bokeh.models import RadioButtonGroup, Panel
from bokeh.layouts import Column

class RegionMenus():
    '国と地域の階層に沿った階層化メニュー'
    tree = UN_regions()  # 国と地域の階層を表す木構造

    def __init__(self, doc):
        '''
        Attributes
        ----------
        view :
            階層化メニューシステム
        menus : Column
            階層化メニューを表すウィジェット
        path : list of str
            階層化メニューから選択された項目のリスト
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
                if new is None: return # 無効化されたメニューについては無視する
                self.path = self.path[:level] + [choice.labels[new]]
                self._update()
            choice.on_change('active', on_change)

        def button_group(level):
            choice = RadioButtonGroup(labels=['None'], visible=False, active=None)
            set_callback(choice, level)
            return choice

        self.menus = Column(name='region_menus',
                            children=[button_group(level) for level in range(4)],
                            css_classes=['spix', 'spix-region-view'],
                            sizing_mode='scale_width')
        self.path = []
        self._update()
        doc.add_root(self.menus)

    def _update(self):
        print(' > '.join(self.path))  # 選択状態を表示する

        menu = self.menus.children
        for level, choice in enumerate(menu):  # path に指定されたレベルのメニューのみを表示
            choice.visible = level <= len(self.path)
        menu[len(self.path)].active = None  # 表示されたメニューのうち最下段は未選択状態とする

        # 階層的な選択に沿って階層化メニューのラベルを更新
        t = self.tree
        menu[0].labels = sorted(t.keys())[:-1]
        for active, choice in zip(self.path, menu[1:]):
            t = t[active]  # 階層構造から選択 (path) に沿って探索
            if isinstance(t, dict):  # 地域群の場合
                choice.labels = sorted(t.keys())[:-1]
            else:  # 国と地域の場合は、それらを列挙表示する
                choice.visible = False
                for index in t: print(f' - {index}')
