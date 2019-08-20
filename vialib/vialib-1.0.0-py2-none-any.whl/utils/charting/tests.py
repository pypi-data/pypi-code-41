
import bar_chart2
import pie_chart
import pop_pyramid
import chart_colors

def maya_test():

    # bar charts
    bar_chart2.test1("TEST enrollment dist.png")
    bar_chart2.test2("TEST edu attainment.png")
    bar_chart2.test3("TEST housing dist.png")
    bar_chart2.test4("TEST right partial population.png")
    bar_chart2.test5("TEST left partial population.png")
    bar_chart2.test6("TEST lining up.png")

    # population pyramid
    pop_pyramid.test1("TEST population pyramid.png")

    # pie chart
    pie_chart.test1('TEST maya piechart.png')

    return

if __name__ == '__main__':
    maya_test()
