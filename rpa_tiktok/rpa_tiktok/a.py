# 新建Python脚本执行
import uiautomator2 as u2
d = u2.connect("192.168.1.235:5006")  # 指定设备
print(d.info)
# 方案A：导出XML到电脑本地（直接跳过设备保存）
xml_content = d.dump_hierarchy()
print(xml_content)
with open("ui_hierarchy1.xml", "w", encoding="utf-8") as f:
    f.write(xml_content)
# 方案B：先导出到设备/sdcard，再拉取
# d.shell("uiautomator dump /sdcard/ui_hierarchy2.xml")  # uiautomator2封装的shell更稳定
# d.pull("/sdcard/ui_hierarchy2.xml", "./")


# import uiautomator2 as u2

# # 连接设备
# d = u2.connect()  # 多设备时指定序列号：u2.connect("设备序列号")

# def parse_gridview_framelayouts():
#     # 直接通过 class 定位唯一的 GridView（假设页面中只有一个）
#     grid_view = d(className="android.widget.GridView")
    
#     # 检查 GridView 是否存在
#     if not grid_view.exists:
#         print("未找到 GridView")
#         return
    
#     print("找到 GridView，开始解析其子 FrameLayout...")
    
#     # 获取 GridView 下所有 class 为 FrameLayout 的子节点
#     frame_layouts = grid_view.children(className="android.widget.FrameLayout")
    
#     if not frame_layouts:
#         print("GridView 下无 FrameLayout 子节点")
#         return
    
#     # 遍历并解析每个 FrameLayout
#     for index, fl in enumerate(frame_layouts, 1):
#         print(f"\n===== 第 {index} 个 FrameLayout =====")
#         # 获取 FrameLayout 的基本信息
#         fl_info = fl.info
#         print(f"位置：{fl_info.get('bounds')}")
#         print(f"是否可见：{fl_info.get('visibleToUser')}")
        
#         # 解析内部元素（示例：文本、图片）
#         # 1. 提取所有文本（TextView）
#         text_views = fl.children(className="android.widget.TextView")
#         for tv in text_views:
#             text = tv.get_text()
#             if text:
#                 print(f"文本内容：{text}")
        
#         # 2. 提取图片（ImageView）
#         image_views = fl.children(className="android.widget.ImageView")
#         print(f"包含图片数量：{len(image_views)}")

# if __name__ == "__main__":
#     parse_gridview_framelayouts()