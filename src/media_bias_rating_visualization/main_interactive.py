from os.path import dirname, join

import json
import pandas as pd

from bokeh.io import curdoc
from bokeh.models.widgets import Select
from bokeh.layouts import layout, column
from bokeh.models import Div, HoverTool, ColumnDataSource

from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, BasicTicker, PrintfTickFormatter, ColorBar

# Color Palettets
from bokeh.palettes import Blues9
from bokeh.palettes import Magma10
from bokeh.palettes import Viridis10


parameter_map = {
    "Click-bait": "clickbait",
    "Controversial News": "controversy",
    "Readability": "readability",
    "Spamminess": "spamminess",
    "Vagueness": "vagueness",
}


def get_data(scores_json, parameter, order):
    input_parameter = parameter_map[parameter]
    data = pd.DataFrame.from_dict(scores_json[input_parameter])

    data.rename(index=str, columns={"scores": "SCORE"}, inplace=True)
    data = data.set_index('sources')
    data.columns.name = 'SCORES'
    df = pd.DataFrame(data.stack(), columns=['score']).reset_index()

    if order == "Best to Worst":
        df.sort_values(by='score', ascending=False, inplace=True)
    else:
        df.sort_values(by='score', ascending=True, inplace=True)

    return df


def get_color_palette(color_map):
    colors = list(reversed(color_map))
    mapper = LinearColorMapper(palette=colors, low=df.score.min(), high=df.score.max())
    return mapper, colors


with open("D:/UnFound/git_repositories/interactive_visualizations/interactive_visualization/app/mediarank/media_scores.json", "r") as file:
    media_scores = json.load(file)

desc = Div(text=open(
    "D:/UnFound/git_repositories/interactive_visualizations/interactive_visualization/app/parliament/description.html").read(),
           width=800)
"""
desc = Div(text=open(join(dirname(__file__), 'description.html')).read(),
           width=800)"""

# Input Controls
parameters = ["Click-bait", "Controversial News", "Readability", "Spamminess", "Vagueness"]
parameter = Select(title="Rating Parameter", options=parameters, value="Readability")

order_list = ["Best to Worst", "Worst to Best"]
order = Select(title="Rank", options=order_list, value="Best to Worst")

df = get_data(media_scores, parameter.value, order.value)
mapper, colors = get_color_palette(Blues9)

media = list(df.sources)
column_name = [parameter.value]
print(df.head())
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

p = figure(title="Media Credibility Rank",
           x_range=column_name, y_range=list(reversed(media)),
           x_axis_location="above", plot_width=400, plot_height=500,
           tools=TOOLS, toolbar_location='below')

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0

# create rectangle for heatmap
p.rect(x=["SCORE"], y="sources", width=1, height=1,
       source=df,
       fill_color={'field': 'score', 'transform': mapper},
       line_color=None)

# create colorbar for label
color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="10pt",
                     ticker=BasicTicker(desired_num_ticks=len(colors)),
                     formatter=PrintfTickFormatter(format="%d%%"),
                     label_standoff=6, border_line_color=None, location=(0, 0))
p.add_layout(color_bar, 'right')

# Add on-hover functionality
hover = HoverTool()
hover.tooltips = [("Media", "@sources"),
                  ("Score", "@score")]
p.tools.append(hover)


# most important
def update():
    parameter_name = parameter.value
    sorting_order = order.value

    # media = list(df.sources)
    # column_name = [parameter_name]
    # p.x_range = column_name
    # p.y_range = list(reversed(media))
    df = get_data(media_scores, parameter_name, sorting_order)
    p.title.text = "%s Ratings of Indian News Sources sorted from %s" % (parameter_name, sorting_order)
    p.title.align = 'center'


controls = [parameter, order]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = column(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p]], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Indian Media Sources"
