from ..api import *
from ..models import *
from datetime import datetime
import cv2

if __name__ == "__main__":
    conf = Configuration()
    # 这里的地址可能会变
    conf.host = "http://localhost:9090/api"
    client = ApiClient(conf)

    category_api = CategoryApi(client)
    # 添加订单类型，一个订单类型下面会对应几个图片类型。订单类型和图片类型只需要添加一次就好。
    order_category = OrderCategory(name='槟榔')
    order_category_id = category_api.add_order_category(order_category)
    # 添加图片类型
    image_cateory1 = ImageCategory(name='一等品',
                                   order_category_id=order_category_id)
    image_cateory2 = ImageCategory(name='二等品',
                                   order_category_id=order_category_id)
    image_cateory3 = ImageCategory(name='次品',
                                   order_category_id=order_category_id)
    image_cateory1_id = category_api.add_image_category(image_cateory1)
    image_cateory2_id = category_api.add_image_category(image_cateory2)
    image_cateory3_id = category_api.add_image_category(image_cateory3)
    # 获取订单类型
    order_category = category_api.get_order_categories_by_name(name='槟榔')
    # 根据订单类型获取图片类型
    image_categories = category_api.get_image_categories(
        order_category_id=str(order_category.id))

    image_api = ImageApi(client)
    # 通过opencv读取文件
    img = cv2.imread("slots.png")
    images = []
    slot1_x1, slot1_x2, slot1_y1, slot1_y2 = 390, 580, 70, 220
    slot_img1 = img[slot1_y1:slot1_y2, slot1_x1:slot1_x2]
    if ImageApi.validate_image(slot_img1):
        images.append(slot_img1)
    slot2_x1, slot2_x2, slot2_y1, slot2_y2 = 370, 580, 420, 550
    slot_img2 = img[slot2_y1:slot2_y2, slot2_x1:slot2_x2]
    if ImageApi.validate_image(slot_img2):
        images.append(slot_img2)
    # 上传训练图片
    image_api.upload_training_images(images,
                                     [order_category_id] * len(images),
                                     [image_categories[0].id] * len(images)
                                     )

    # 上传待检测图片
    s1 = datetime.now()
    results = image_api.upload_testing_images(
        images,
        [order_category_id] * len(images),
    )
    s2 = datetime.now()
    print(s1, s2, s2 - s1)
    # 根据返回的类型执行相应的动作
    for result in results:
        print(result)

    status_api = DeviceStatusApi(client)
    # 创建设备可读取状态
    device_readable_status = DeviceStatus()
    # 设置总控站可读取状态
    device_readable_status.master_status['系统状态'] = 1
    device_readable_status.master_status['已入库数量'] = 10
    # 设置上料工位可读取状态
    device_readable_status.loader_status['系统状态'] = 1
    device_readable_status.loader_status['当前步'] = 3
    device_readable_status.loader_status['错误类型'] = 1
    device_readable_status.loader_status['检测触发'] = 1
    # 设置包装工位可读取状态
    device_readable_status.packer_status['系统状态'] = 1
    device_readable_status.packer_status['当前步'] = 3
    device_readable_status.packer_status['错误类型'] = 1
    device_readable_status.packer_status['实时力值'] = 1
    device_readable_status.packer_status['盒盖数量'] = 1
    # 设置仓库工位可读取状态
    device_readable_status.warehouse_status['系统状态'] = 1
    device_readable_status.warehouse_status['当前步'] = 3
    device_readable_status.warehouse_status['错误类型'] = 1
    device_readable_status.warehouse_status['库存数量'] = 1
    device_readable_status.warehouse_status['电机当前位置'] = 1
    device_readable_status.warehouse_status['电机当前速度'] = 1
    status_api.add_device_readable_status(device_readable_status)
    latest_command = status_api.get_device_readable_status()
    print(latest_command)

    command_api = DeviceCommandApi(client)
    # 获取设备命令
    latest_command = command_api.get_device_command()
    print(latest_command)

    signal_api = DeviceSignalApi(client)
    # 创建设备IO信号
    device_signal = DeviceSignal()
    # 设置总控输入信号
    device_signal.master_io.input['开关按钮'] = True
    device_signal.master_io.input['复位按钮'] = False
    device_signal.master_io.input['急停按钮'] = True
    device_signal.master_io.input['手/自动按钮'] = True
    # 设置总控输出信号
    device_signal.master_io.output['黄灯'] = True
    device_signal.master_io.output['绿灯'] = True
    device_signal.master_io.output['红灯'] = False
    device_signal.master_io.output['蜂鸣器'] = True
    # 设置上料工位输入信号
    device_signal.loader_io.input['落料1检测'] = True
    device_signal.loader_io.input['落料2检测'] = True
    device_signal.loader_io.input['工位1检测'] = False
    device_signal.loader_io.input['工位2检测'] = True
    device_signal.loader_io.input['送料伸出位'] = False
    device_signal.loader_io.input['分拣1伸出位'] = True
    device_signal.loader_io.input['分拣2伸出位'] = True
    # 设置上料工位输出信号
    device_signal.loader_io.output['步进1脉冲'] = True
    device_signal.loader_io.output['步进1方向'] = True
    device_signal.loader_io.output['上料电机'] = False
    device_signal.loader_io.output['拍照相机'] = True
    device_signal.loader_io.output['送料缸'] = False
    device_signal.loader_io.output['分拣缸1'] = True
    device_signal.loader_io.output['分拣缸2'] = True
    # 设置包装工位输入信号
    device_signal.packer_io.input['原点'] = True
    device_signal.packer_io.input['左极限'] = True
    device_signal.packer_io.input['右极限'] = True
    device_signal.packer_io.input['阻挡1检测'] = True
    device_signal.packer_io.input['阻挡2检测'] = False
    device_signal.packer_io.input['称重位检测'] = True
    device_signal.packer_io.input['阻挡3检测'] = True
    device_signal.packer_io.input['仓储位检测'] = True
    device_signal.packer_io.input['阻挡1伸出位'] = False
    device_signal.packer_io.input['阻挡2伸出位'] = True
    device_signal.packer_io.input['称重伸出位'] = True
    device_signal.packer_io.input['阻挡3伸出位'] = True
    device_signal.packer_io.input['称重位检测'] = True
    device_signal.packer_io.input['阻挡3检测'] = True
    device_signal.packer_io.input['输送缩回位'] = False
    device_signal.packer_io.input['上盖上升位'] = False
    device_signal.packer_io.input['上盖伸出位'] = True
    device_signal.packer_io.input['盒盖检测'] = True
    # 设置包装工位输出信号
    device_signal.packer_io.output['步进2脉冲'] = True
    device_signal.packer_io.output['步进2方向'] = True
    device_signal.packer_io.output['电机抱闸'] = True
    device_signal.packer_io.output['料盒输送'] = True
    device_signal.packer_io.output['运料输送'] = False
    device_signal.packer_io.output['称重推送'] = True
    device_signal.packer_io.output['阻挡器1'] = False
    device_signal.packer_io.output['阻挡器2'] = True
    device_signal.packer_io.output['阻挡器3'] = True
    device_signal.packer_io.output['吸盘'] = True
    device_signal.packer_io.output['称重升降'] = True
    device_signal.packer_io.output['取盖升降'] = False
    device_signal.packer_io.output['取盖伸出'] = False
    device_signal.packer_io.output['取盖缩回'] = True
    device_signal.packer_io.output['料盒推拉'] = True
    # 设置仓库工位输入信号
    device_signal.warehouse_io.input['原点'] = True
    device_signal.warehouse_io.input['左极限'] = True
    device_signal.warehouse_io.input['右极限'] = True
    device_signal.warehouse_io.input['手爪上升位'] = True
    device_signal.warehouse_io.input['手爪夹紧到位 '] = True
    device_signal.warehouse_io.input['手爪松开到位 '] = True
    device_signal.warehouse_io.input['仓储1检测'] = True
    device_signal.warehouse_io.input['仓储2检测'] = False
    device_signal.warehouse_io.input['仓储3检测'] = True
    device_signal.warehouse_io.input['仓储4检测'] = False
    device_signal.warehouse_io.input['仓储5检测'] = True
    device_signal.warehouse_io.input['仓储6检测'] = True
    # 设置仓库工位输出信号
    device_signal.warehouse_io.output['步进3脉冲'] = True
    device_signal.warehouse_io.output['步进3方向'] = True
    device_signal.warehouse_io.output['手爪升降缸'] = True
    device_signal.warehouse_io.output['手爪夹紧'] = False
    device_signal.warehouse_io.output['手爪松开'] = True
    # 上传信号
    signal_api.add_signal(device_signal)

    error_info_api = ErrorInfoApi(client)
    # 添加错误信息
    error_info = ErrorInfo(code='ERR001', description='XX设备故障',
                           action='查看XX设备')
    error_info_api.create_error_info(error_info)
