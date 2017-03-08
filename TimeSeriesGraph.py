'''
tested only on Python 2.7.x
'''

from kivy.garden.graph import Graph, identity, exp10, log10
from kivy.graphics.transformation import Matrix
from math import radians

class TimeSeriesGraph(Graph):

    def __init__(self, x_date_labels, date_label_format = '%b', _with_stencilbuffer = False, **kwargs):
        self.x_date_labels = x_date_labels
        self._date_label_format = date_label_format
        self._with_stencilbuffer = _with_stencilbuffer
        kwargs["xmin"] = 0
        kwargs["xmax"] = len(self.x_date_labels) - 1
        super(TimeSeriesGraph, self).__init__(**kwargs)

    def _get_ticks(self, major, minor, log, s_min, s_max):
        if major == 'month':
            points_major = []
            m = self.x_date_labels[0].month
            for i in range(len(self.x_date_labels)):
                if self.x_date_labels[i].month != m:
                    m = self.x_date_labels[i].month
                    points_major.append(float(i))

            points_minor = []
        else:
            points_major, points_minor = super(TimeSeriesGraph, self)._get_ticks(major, minor, log, s_min, s_max)

        return points_major, points_minor

    def _update_labels(self):
        xlabel = self._xlabel
        ylabel = self._ylabel
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        padding = self.padding
        x_next = padding + x
        y_next = padding + y
        xextent = width + x
        yextent = height + y
        ymin = self.ymin
        ymax = self.ymax
        xmin = self.xmin
        precision = self.precision
        x_overlap = False
        y_overlap = False
        # set up x and y axis labels
        if xlabel:
            xlabel.text = self.xlabel
            xlabel.texture_update()
            xlabel.size = xlabel.texture_size
            xlabel.pos = int(x + width / 2. - xlabel.width / 2.), int(padding + y)
            y_next += padding + xlabel.height
        if ylabel:
            ylabel.text = self.ylabel
            ylabel.texture_update()
            ylabel.size = ylabel.texture_size
            ylabel.x = padding + x - (ylabel.width / 2. - ylabel.height / 2.)
            x_next += padding + ylabel.height
        xpoints = self._ticks_majorx
        xlabels = self._x_grid_label
        xlabel_grid = self.x_grid_label
        ylabel_grid = self.y_grid_label
        ypoints = self._ticks_majory
        ylabels = self._y_grid_label
        # now x and y tick mark labels
        if len(ylabels) and ylabel_grid:
            # horizontal size of the largest tick label, to have enough room
            funcexp = exp10 if self.ylog else identity
            funclog = log10 if self.ylog else identity
            ylabels[0].text = precision % funcexp(ypoints[0])
            ylabels[0].texture_update()
            y1 = ylabels[0].texture_size
            y_start = y_next + (padding + y1[1] if len(xlabels) and xlabel_grid
                                else 0) + \
                               (padding + y1[1] if not y_next else 0)
            yextent = y + height - padding - y1[1] / 2.

            ymin = funclog(ymin)
            ratio = (yextent - y_start) / float(funclog(ymax) - ymin)
            y_start -= y1[1] / 2.
            y1 = y1[0]
            for k in range(len(ylabels)):
                ylabels[k].text = precision % funcexp(ypoints[k])
                ylabels[k].texture_update()
                ylabels[k].size = ylabels[k].texture_size
                y1 = max(y1, ylabels[k].texture_size[0])
                ylabels[k].pos = tuple(map(int, (x_next, y_start +
                                                 (ypoints[k] - ymin) * ratio)))
            if len(ylabels) > 1 and ylabels[0].top > ylabels[1].y:
                y_overlap = True
            else:
                x_next += y1 + padding
        if len(xlabels) and xlabel_grid:
            funcexp = exp10 if self.xlog else identity
            funclog = log10 if self.xlog else identity
            # find the distance from the end that'll fit the last tick label
            xlabels[0].text = precision % funcexp(xpoints[-1])
            xlabels[0].texture_update()
            xextent = x + width - xlabels[0].texture_size[0] / 2. - padding
            # find the distance from the start that'll fit the first tick label
            if not x_next:
                xlabels[0].text = precision % funcexp(xpoints[0])
                xlabels[0].texture_update()
                x_next = padding + xlabels[0].texture_size[0] / 2.
            xmin = funclog(xmin)
            ratio = (xextent - x_next) / float(funclog(self.xmax) - xmin)
            right = -1
            for k in range(len(xlabels)):
                xlabels[k].text = self.x_date_labels[int(xpoints[k])].strftime(self._date_label_format)
                # update the size so we can center the labels on ticks
                xlabels[k].texture_update()
                xlabels[k].size = xlabels[k].texture_size
                xlabels[k].pos = tuple(map(int, (x_next + (xpoints[k] - xmin)
                    * ratio - xlabels[k].texture_size[0] / 2., y_next)))
                if xlabels[k].x < right:
                    x_overlap = True
                    break
                right = xlabels[k].right
            if not x_overlap:
                y_next += padding + xlabels[0].texture_size[1]
        # now re-center the x and y axis labels
        if xlabel:
            xlabel.x = int(x_next + (xextent - x_next) / 2. - xlabel.width / 2.)
        if ylabel:
            ylabel.y = int(y_next + (yextent - y_next) / 2. - ylabel.height / 2.)
            t = Matrix().translate(ylabel.center[0], ylabel.center[1], 0)
            t = t.multiply(Matrix().rotate(-radians(270), 0, 0, 1))
            ylabel.transform = t.multiply(
                Matrix().translate(
                    -int(ylabel.center_x),
                    -int(ylabel.center_y),
                    0))
        if x_overlap:
            for k in range(len(xlabels)):
                xlabels[k].text = ''
        if y_overlap:
            for k in range(len(ylabels)):
                ylabels[k].text = ''
        return x_next - x, y_next - y, xextent - x, yextent - y

if __name__ == "__main__":
    from kivy.garden.graph import SmoothLinePlot
    from kivy.uix.screenmanager import Screen, ScreenManager
    from datetime import date, timedelta
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.utils import get_color_from_hex as rgb
    from random import random

    class TestApp(App):

        def build(self):
            layout = BoxLayout(orientation='vertical')

            graph_theme = {
                'label_options': {
                    'color': rgb('444444'),  # color of tick labels and titles
                    'bold': True},
                'background_color': rgb('f8f8f2'),  # back ground color of canvas
                'tick_color': rgb('808080'),  # ticks and grid
                'border_color': rgb('808080')}  # border drawn around each graph

            x_values = list(range(100))
            y_values = [123.0 + random() for x in x_values]
            end_date = date(2017, 2, 1)
            one_day = timedelta(1)
            date_values = [end_date - one_day * i for i in x_values]
            date_values.reverse()
            time_series = zip(x_values, y_values)

            graph1 = TimeSeriesGraph(
                date_values,
                date_label_format='%b',
                xlabel='example 1',
                ylabel='some y labels',
                #x_ticks_minor=5,
                x_ticks_major='month',
                y_ticks_major=0.1,
                y_grid_label=True,
                x_grid_label=True,
                padding=5,
                xlog=False,
                ylog=False,
                x_grid=True,
                y_grid=True,
                #xmin=-50,
                #xmax=50,
                ymin=123,
                ymax=124,
                font_size = '12sp',
                **graph_theme)

            plot1 = SmoothLinePlot(color=rgb('7dac9f'))
            plot1.points = time_series
            graph1.add_plot(plot1)

            plot3 = SmoothLinePlot(color=rgb('dc7062'))
            y_values = [123.0 + random() for x in x_values]
            time_series = zip(x_values, y_values)
            plot3.points = time_series
            graph1.add_plot(plot3)

            layout.add_widget(graph1)

            y_values = [123.0 + random() for x in x_values]

            graph2 = TimeSeriesGraph(
                date_values,
                date_label_format='%b-%d',
                xlabel='example 2',
                ylabel='some y labels',
                x_ticks_minor=5,
                x_ticks_major=30,
                y_ticks_major=0.1,
                y_grid_label=True,
                x_grid_label=True,
                padding=5,
                xlog=False,
                ylog=False,
                x_grid=True,
                y_grid=True,
                #xmin=-50,
                #xmax=50,
                ymin=123,
                ymax=124,
                font_size = '12sp',
                **graph_theme)

            plot2 = SmoothLinePlot(color=rgb('7dac9f'))
            plot2.points = zip(x_values, y_values)
            graph2.add_plot(plot2)

            layout.add_widget(graph2)

            s = Screen(name="test1")
            s.add_widget(layout)

            sm = ScreenManager()
            sm.add_widget(s)

            return sm

    TestApp().run()
