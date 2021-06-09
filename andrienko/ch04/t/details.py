from bokeh.core.properties import String
from bokeh.models import *

class Details(HTMLBox):
    __implementation__ = 'details.ts'

    #button = Button(label='Click Me')

    description = String(default='If you love something, set it free.')

    '''
    descriptions = [Paragraph(text='If it comes back to you, it is yours.'),
                    Paragraph(text='If it comes not, it was never meant to be.')]
    '''

    def __init__(self, doc, **args):
        super().__init__(**args)
        doc.add_root(self, Column(self, name='Details'))
