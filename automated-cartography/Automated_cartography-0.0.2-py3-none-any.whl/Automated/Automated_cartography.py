# -*- coding:utf-8 -*-
def get_best_sell_index(PSINrank, sellsnum):
    bestsellindex = float(1 / int(PSINrank)) * 1000
    sellsnumber = sellsnum * 47
    commemts = sellsnum
    return bestsellindex, sellsnumber, commemts


def drow_chart(data, filename):
    import xlsxwriter

    workbook = xlsxwriter.Workbook(filename)

    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    headings = ['日期', '评价量', '销售量', '评分', '商品链接', '价格', '爆款指数']

    worksheet.write_row('A1', headings, bold)

    worksheet.write_column('A2', data[0])
    worksheet.write_column('B2', data[1])
    worksheet.write_column('C2', data[2])
    worksheet.write_column('D2', data[3])
    worksheet.write_column('E2', data[4])
    worksheet.write_column('F2', data[5])
    worksheet.write_column('G2', data[6])

    chart_col = workbook.add_chart({'type': 'line'})
    chart_col2 = workbook.add_chart({'type': 'line'})
    chart_col3 = workbook.add_chart({'type': 'line'})
    chart_col4 = workbook.add_chart({'type': 'line'})
    chart_col5 = workbook.add_chart({'type': 'line'})

    chart_col.add_series({
        'name': ['Sheet1', 0, 1],
        'categories': ['Sheet1', 1, 0, len(data[0]), 0],
        'values': ['Sheet1', 1, 1, len(data[0]), 1],
        'line': {'color': 'red'},
    })

    chart_col.set_title({'name': '评价量趋势图'})
    chart_col.set_x_axis({'name': '日期'})
    chart_col.set_y_axis({'name': '评价量数值'})

    chart_col.set_style(1)

    worksheet.insert_chart('H20', chart_col, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2.5, 'y_scale': 1.3})

    # -------------------------------------------------------------------------------------------------------
    chart_col2.add_series({
        'name': ['Sheet1', 0, 6],
        'categories': ['Sheet1', 1, 0, len(data[0]), 0],
        'values': ['Sheet1', 1, 6, len(data[0]), 6],
        'line': {'color': 'red'},
    })
    chart_col2.set_title({'name': '爆款指数趋势图'})
    chart_col2.set_x_axis({'name': '日期'})
    chart_col2.set_y_axis({'name': '相对爆款指数值'})

    chart_col2.set_style(1)

    worksheet.insert_chart('H1', chart_col2, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2.5, 'y_scale': 1.3})
    # -----------------------------------------------------------------------------------------------------
    chart_col3.add_series({
        'name': ['Sheet1', 0, 3],
        'categories': ['Sheet1', 1, 0, len(data[0]), 0],
        'values': ['Sheet1', 1, 3, len(data[0]), 3],
        'line': {'color': 'green'},
    })
    chart_col3.set_title({'name': '评分趋势图'})
    chart_col3.set_x_axis({'name': '日期'})
    chart_col3.set_y_axis({'name': '综合评分数值'})

    chart_col3.set_style(1)

    worksheet.insert_chart('H80', chart_col3, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2.5, 'y_scale': 1.3})
    # -----------------------------------------------------------------------------------------------------
    chart_col4.add_series({
        'name': ['Sheet1', 0, 5],
        'categories': ['Sheet1', 1, 0, len(data[0]), 0],
        'values': ['Sheet1', 1, 5, len(data[0]), 5],
        'line': {'color': 'yellow'},
    })
    chart_col4.set_title({'name': '价格趋势图'})
    chart_col4.set_x_axis({'name': '日期'})
    chart_col4.set_y_axis({'name': '价格'})

    chart_col4.set_style(1)

    worksheet.insert_chart('H40', chart_col4, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2.5, 'y_scale': 1.3})
    # -----------------------------------------------------------------------------------------------------
    chart_col5.add_series({
        'name': ['Sheet1', 0, 2],
        'categories': ['Sheet1', 1, 0, len(data[0]), 0],
        'values': ['Sheet1', 1, 2, len(data[0]), 2],
        'line': {'color': 'blue'},
    })
    chart_col5.set_title({'name': '销售量趋势图'})
    chart_col5.set_x_axis({'name': '日期'})
    chart_col5.set_y_axis({'name': '销售量根据2.1%留评率估算'})

    chart_col5.set_style(1)

    worksheet.insert_chart('H60', chart_col5, {'x_offset': 10, 'y_offset': 10, 'x_scale': 2.5, 'y_scale': 1.3})

    workbook.close()
