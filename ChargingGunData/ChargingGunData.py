import time
from datetime import datetime
from functools import partial

import pandas as pd
import requests
import schedule
from pandas import json_normalize

# 接口 URL
list_url = "https://gw.am.xiaojukeji.com/equip-app/web/connector/list"
detail_url = "https://gw.am.xiaojukeji.com/equip-app/equipment/detail"

# 订单管理
order_url = "https://gw.am.xiaojukeji.com/epower-atreus/api/arcfox/order/web/queryList"


# 读取 config.txt 中的 cookie 和 csrf_token
def read_config(file_path='config.txt'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        cookie_line = lines[0].strip()  # 获取 cookie 的那一行
        csrf_token_line = lines[1].strip()  # 获取 csrf_token 的那一行

        # 提取 ticket 后的值
        cookie = cookie_line.split('ticket=')[1]  # 只截取 ticket 后面的内容
        csrf_token = csrf_token_line.split('csrf_token=')[1]  # 提取 csrf_token 的值
        return cookie, csrf_token


def fetch_and_write_order_data(cookie, csrf_token):
    # 请求头（根据从文件读取的 cookie 和 csrf_token）
    headers = {
        "Cookie": f"ticket={cookie}",  # 从 config.txt 获取的 Cookie
        "env": "pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    # 请求参数的公共部分
    params = {
        "loginMerchantId": 1013119,  # 登录商户 ID
        "csrfToken": csrf_token  # 从 config.txt 获取的 csrfToken
    }
    today = datetime.today()
    # 格式化为 YYYY-MM-DD 形式
    start_time = today.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
    end_time = today.replace(hour=23, minute=59, second=59, microsecond=999999).strftime('%Y-%m-%d %H:%M:%S')

    body = {
        # "page":1,
        "size": 10,
        "startTime": start_time,
        "endTime": end_time,
        "merchantId": 1013119
    }
    order_list = []

    total_pages = 100
    for item in range(1, total_pages + 1):
        body["page"] = item  # 动态修改 pageIndex 参数
        response = requests.post(order_url, json=body, headers=headers, params=params)
        if response.status_code == 200:
            # 如果请求成功，获取页面数据
            data = response.json()
            page_object = data['data'].get('pageObject', [])
            print(f'订单的数据是{page_object}')
            if page_object:
                for item in page_object:
                    detail_df = json_normalize(item)
                    order_list.append(detail_df)
            else:
                print(f"第 {item} 页 请求失败！状态码: {response.status_code}")
                break

    final_df1 = pd.concat(order_list, ignore_index=True)

    # 获取当前时间并格式化为文件名
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name1 = f"订单管理{current_time}.xlsx"

    # 写入 Excel 文件
    with pd.ExcelWriter(file_name1, engine='openpyxl') as writer:
        final_df1.to_excel(writer, index=False, sheet_name='订单列表')
    print(f"Excel 文件已生成：{file_name1}")


def fetch_and_write_chargingStation_data(cookie, csrf_token):
    # 请求头（根据从文件读取的 cookie 和 csrf_token）
    headers = {
        "Cookie": f"ticket={cookie}",  # 从 config.txt 获取的 Cookie
        "env": "pc",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    # 请求参数的公共部分
    params = {
        "current": 1,  # 当前页，一般在请求时是固定的，或者根据实际情况修改
        "pageSize": 10,
        "merchantId": 1013119,
        "loginMerchantId": 1013119,  # 登录商户 ID
        "csrfToken": csrf_token  # 从 config.txt 获取的 csrfToken
    }

    # 存储设备信息的列表
    equipment_list = []
    equipment_detail_list = []

    # 获取总页数 (假设从响应中获取)
    total_pages = 5  # 可以根据响应数据动态获取 totalPage 值

    # 遍历所有分页并请求数据
    for pageIndex in range(0, total_pages + 1):  # 从 1 到 total_pages
        params["pageIndex"] = pageIndex  # 动态修改 pageIndex 参数

        # 发送 GET 请求，传递参数和请求头
        response = requests.get(list_url, headers=headers, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            # 如果请求成功，获取页面数据
            data = response.json()
            page_object = data['data'].get('pageObject', [])

            if page_object:
                print(f"第 {pageIndex} 页 数据：")
                # 将充电枪的数据写入到excel中

                for item in page_object:
                    # 提取 equipmentId 和 fullEquipmentId
                    equipment_id = item['equipmentId']
                    full_equipment_id = item['fullEquipmentId']
                    print(f"调用设备详情接口：设备ID {equipment_id}, 完整设备ID {full_equipment_id}")

                    detail_df2 = json_normalize(item)
                    equipment_list.append(detail_df2)

                    # 调用设备详情接口
                    detail_params = {
                        "equipmentId": equipment_id,
                        "fullEquipmentId": full_equipment_id,
                        "loginMerchantId": 1013119,
                        "csrfToken": csrf_token  # 可以复用之前的 csrfToken
                    }
                    detail_response = requests.get(detail_url, headers=headers, params=detail_params)

                    # 检查设备详情请求响应
                    if detail_response.status_code == 200:
                        # 如果请求成功，获取设备详情数据
                        detail_data = detail_response.json()

                        # 打印设备详情数据
                        print("设备详情：", detail_data)

                        # 将 detail_data 转换为 DataFrame
                        # 使用 json_normalize 将嵌套的 JSON 扁平化
                        detail_df = json_normalize(detail_data['data'])

                        # 添加设备ID和完整设备ID作为额外列
                        detail_df['equipmentId'] = equipment_id
                        detail_df['fullEquipmentId'] = full_equipment_id

                        # 将设备信息保存到设备详情列表
                        equipment_detail_list.append(detail_df)
                    else:
                        print(f"设备详情请求失败！设备ID: {equipment_id}，状态码: {detail_response.status_code}")
            else:
                print(f"第 {pageIndex} 页 没有数据")
        else:
            print(f"第 {pageIndex} 页 请求失败！状态码: {response.status_code}")

    # 将所有设备详情合并为一个 DataFrame
    final_df1 = pd.concat(equipment_list, ignore_index=True)
    final_df2 = pd.concat(equipment_detail_list, ignore_index=True)

    # 获取当前时间并格式化为文件名
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name1 = f"充电枪列表数据_{current_time}.xlsx"
    file_name2 = f"充电枪详情数据_{current_time}.xlsx"

    # 写入 Excel 文件
    with pd.ExcelWriter(file_name1, engine='openpyxl') as writer:
        final_df1.to_excel(writer, index=False, sheet_name='设备列表')
    with pd.ExcelWriter(file_name2, engine='openpyxl') as writer:
        final_df2.to_excel(writer, index=False, sheet_name='设备详情')

    print(f"Excel 文件已生成：{file_name1}")
    print(f"Excel 文件已生成：{file_name2}")


if __name__ == '__main__':
    # 读取 cookie 和 csrf_token
    cookie, csrf_token = read_config()
    # 订单管理数据(当天)
    fetch_and_write_order_data(cookie, csrf_token)
    # 充电枪列表和详情数据
    fetch_and_write_chargingStation_data(cookie, csrf_token)

# 每半小时执行一次
# 读取配置中的 cookie 和 csrf_token
# cookie, csrf_token = read_config()
#
# # 定时任务，每 15 分钟执行
# schedule.every(5).minutes.do(partial(fetch_and_write_order_data, cookie, csrf_token))
# schedule.every(5).minutes.do(partial(fetch_and_write_chargingStation_data, cookie, csrf_token))
#
# # 保持程序持续运行
# while True:
#     schedule.run_pending()
#     time.sleep(1)
