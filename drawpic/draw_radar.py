import json

import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = 'radar'
        RESOLUTION = 1
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def get_data(fix: str):
    language_list = ['cpp', 'java', 'python']
    project_list = [['bitcoin', 'calculator', 'leveldb', 'git', 'electron'],
                    ['halo', 'fastjson', 'mockito', 'MPAndroidChart', 'RxJava'],
                    ['boto3', 'glances', 'mypy', 'numpy', 'keras']]
    # project_list = [['bitcoin'],
    #                 ['halo'],
    #                 ['boto3']]
    data_list = {}
    tool_list = ['Sourcetrail', 'ENRE', 'Depends', 'Sourcetrail', 'Understand', 'Depends', 'ENRE', 'Understand']
    for index in range(0, len(language_list)):
        data_list[language_list[index]] = []
        projects = project_list[index]
        count = get_tool_number(projects, fix)
        language = language_list[index]
        data_list[language].append([count[tool_name.lower()] for tool_name in tool_list])
        for index in range(0, len(tool_list)):
            tool = tool_list[index]
            temp_list = [0, 0, 0, 0, 0, 0, 0, 0]
            temp_list[index] = count[tool.lower()]
            data_list[language].append(temp_list)
        for i in range(0, 6):
            data_list[language].append([0, 0, 0, 0, 0, 0, 0, 0])

        for project_name in projects:
            with open(f"../count_file/{project_name}_{fix}.csv", 'r') as file:
                # 'Sourcetrail', 'ENRE', 'Depends', 'Sourcetrail', 'Understand', 'Depends', 'ENRE', 'Understand'
                reader = csv.reader(file)
                for index, rows in enumerate(reader):
                    # enre & understand
                    if index == 2:
                        l_equal_data = int(rows[len(rows) - 1])
                    if index == 4:
                        r_equal_data = int(rows[len(rows) - 1])
                        temp_list = [0, 0, 0, 0, 0, 0, l_equal_data, r_equal_data]
                        data_list[language][9] = [(temp_list[i] + data_list[language][9][i]) for i in range(0, 8)]
                    # enre & depends
                    if index == 13:
                        l_equal_data = int(rows[len(rows) - 1])
                    if index == 15:
                        r_equal_data = int(rows[len(rows) - 1])
                        temp_list = [0, l_equal_data, r_equal_data, 0, 0, 0, 0, 0]
                        data_list[language][10] = [(temp_list[i] + data_list[language][10][i]) for i in range(0, 8)]
                    # enre & sourcetrail
                    if index == 24:
                        l_equal_data = int(rows[len(rows) - 1])
                    if index == 26:
                        r_equal_data = int(rows[len(rows) - 1])
                        temp_list = [r_equal_data, l_equal_data, 0, 0, 0, 0, 0, 0]
                        data_list[language][11] = [(temp_list[i] + data_list[language][11][i]) for i in range(0, 8)]
                    # understand & depends
                    if index == 35:
                        l_equal_data = int(rows[len(rows) - 1])
                    if index == 37:
                        r_equal_data = int(rows[len(rows) - 1])
                        temp_list = [0, 0, 0, 0, l_equal_data, r_equal_data, 0, 0]
                        data_list[language][12] = [(temp_list[i] + data_list[language][12][i]) for i in range(0, 8)]
                    # Understand & sourcetrail
                    if index == 46:
                        l_equal_data = int(rows[len(rows) - 1])
                    if index == 48:
                        r_equal_data = int(rows[len(rows) - 1])
                        temp_list = [r_equal_data, 0, 0, 0, 0, 0, 0, l_equal_data]
                        data_list[language][13] = [(temp_list[i] + data_list[language][13][i]) for i in range(0, 8)]
                    # depends & sourcetrail
                    if index == 57:
                        l_equal_data = int(rows[len(rows) - 1])
                    if index == 59:
                        r_equal_data = int(rows[len(rows) - 1])
                        temp_list = [0, 0, l_equal_data, r_equal_data, 0, 0, 0, 0]
                        data_list[language][14] = [(temp_list[i] + data_list[language][14][i]) for i in range(0, 8)]
    Jaccard = dict()
    for key in data_list.keys():
        temp = data_list[key]
        Jaccard[key] = list()
        m_list = [9, 10, 11, 12, 13, 14]
        n_list = [6, 1, 0, 4, 0, 2]
        j_list = [7, 2, 1, 5, 7, 3]
        for m, n, j in zip(m_list, n_list, j_list):
            Jaccard[key].append(((temp[m][j] +temp[m][n])/2)/(temp[0][n] + temp[0][j] + temp[m][n]/2 + temp[m][j]/2))
    print(Jaccard)

    data = [
        ['Sourcetrail', 'ENRE', 'Depends', 'Sourcetrail', 'Understand', 'Depends', 'ENRE', 'Understand'],
        ('C++', data_list['cpp']),
        ('Java', data_list['java']),
        ('Python', data_list['python'])
    ]
    return data


def get_tool_number(project:list, fix):
    tool_list = ['enre', 'understand', 'sourcetrail', 'depends']
    count = dict()
    for tool_name in tool_list:
        count[tool_name] = 0
    for project_name in project:
        for tool_name in tool_list:
            path = f"../input_dir/{project_name}/{tool_name}_{project_name}_{fix}.json"
            with open(path, 'r') as file:
                data = json.load(file)
                count[tool_name] = count[tool_name] + len(data[fix])
    return count


if __name__ == '__main__':
    isentity = "dependency"
    N = 8
    theta = radar_factory(N, frame='polygon')
    data = get_data(isentity)
    spoke_labels = data.pop(0)

    fig, axs = plt.subplots(figsize=(9, 9), nrows=1, ncols=3,
                            subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    color1 = "#772540"
    color2 = "#D3658A"
    color3 = "#FCE4EC"
    colors = ['#769BFF', color2, color2, color2, color2, color2, color2, color2, color2,
              color1, color1, color1, color1, color1, color1]
    color_backgroud = ['#C4D4FF', color2, color2, color2, color2, color2, color2, color2, color2,
                       color3, color3, color3, color3, color3, color3]
    for ax, (title, case_data) in zip(axs.flat, data):
        ax.set_rgrids([0.2, 0.4, 0.6, 0.8])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        for d, color, color_back in zip(case_data, colors, color_backgroud):
            ax.plot(theta, d, color=color)
            ax.fill(theta, d, facecolor=color_back, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    fig.text(0.5, 0.965, '4-Tool result on specific project Across Three Languages',
             horizontalalignment='center', color='black', weight='bold',
             size='large')

    plt.show()