import requests
from openpyxl import Workbook
import os
from datetime import datetime

# 获取当前日期
today = datetime.today()
start_time = today.strftime("%Y-%m-%d 00:00:00")
end_time = today.strftime("%Y-%m-%d 23:59:59")

# 发送请求
# url = "http://26.47.30.153:8089/jzzgfgcxt/jzzgfgc/getYcgfclqx"
url = "http://192.168.0.66:10032/articles/getJson"
params = {
    "cityCode": "321200",
    "areaCode": "",
    "startTime": start_time,
    "endTime": end_time
}

response = requests.get(url, params=params)

data = response.json()

# 检查请求是否成功
if data['code'] == 200 and data['success']:
    # 提取需要的数据
    result_data = data['result']['data']

    # 创建一个字典来存储按日期分组的数据
    grouped_data = {}

    for row in result_data:
        if len(row) < 2 or row[0] is None or row[1] is None:
            continue  # 跳过数据不完整的行
        try:
            date_time_obj = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"日期格式错误：{row[0]}")
            continue
        date_str = date_time_obj.strftime("%Y-%m-%d")  # 提取日期部分
        if date_str not in grouped_data:
            grouped_data[date_str] = []
        grouped_data[date_str].append((date_time_obj, row[1]))

    # 找出每一天的最大值
    max_values = []
    for date, values in grouped_data.items():
        max_value = max(values, key=lambda x: x[1])
        max_values.append((max_value[0].strftime("%Y-%m-%d %H:%M:%S"), max_value[1]))

    # 转换数据格式，分别存储日期和最大值
    dates = [date for date, value in max_values]
    values = [value for date, value in max_values]

    # 创建 Workbook 对象
    outwb = Workbook()
    outws = outwb.active

    # 写入数据到 Excel 以列的形式
    outws.append(dates)
    outws.append(values)

    # 保存 Excel 文件到桌面
    date_str = today.strftime("%Y-%m-%d")
    file_name = f"{date_str}.xlsx"

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, file_name)
    outwb.save(file_path)

    print(f"数据已成功导出到 {file_path}")
else:
    print("请求失败，无法获取数据")
