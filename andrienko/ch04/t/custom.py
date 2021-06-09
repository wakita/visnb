from bokeh.core.properties import String, Instance
from bokeh.models import HTMLBox, Slider

class Custom(HTMLBox):

    __implementation__ = "custom.ts"

    text = String(default="Custom text")

    slider = Instance(Slider)
