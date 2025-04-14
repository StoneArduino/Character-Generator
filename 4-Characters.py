# -*- coding: utf-8 -*-
"""
字符生成器 - 可生成数码管风格的字符图像
支持生成数字、字母和特殊字符，可自定义样式，支持中英文切换
"""

import tkinter as tk
from tkinter import messagebox, Toplevel, Label, ttk, scrolledtext
from PIL import Image, ImageDraw, ImageTk
import os
import win32clipboard
from io import BytesIO
import webbrowser
import json
import datetime
import sys
import traceback

# 版本信息
VERSION = "2.0.0"

# 版本变更记录 - 中文版
VERSION_HISTORY_CN = [
    {
        "version": "2.0.0",
        "date": "2025-04-11 19:11",
        "changes": [
            "修复了部分字母大小写不识别的问题",
            "修复了部分数字显示异常的问题",
            "删除了硬件注册码的机制，完全共享该软件的使用权限",
            "添加了版本历史显示组件",
            "添加了作者信息的about显示"
        ]
    },
    {
        "version": "1.0.0",
        "date": "2025-03-06",
        "changes": [
            "支持了指定段的显示",
            "支持了方块的显示",
            "支持了单个字符情况下的小数点的显示",
            "支持了中英文切换",
            "新增了字符样式的自定义功能",
            "添加了硬件注册码机制用于测试"
        ]
    },
    {
        "version": "0.0.0",
        "date": "2024-09-10",
        "changes": [
            "原型设计",
            "规划功能结构"
        ]
    }
]

# 版本变更记录 - 英文版
VERSION_HISTORY_EN = [
    {
        "version": "2.0.0",
        "date": "2025-04-11 19:11",
        "changes": [
            "Fixed case sensitivity issues with letters",
            "Fixed display issues with some numbers",
            "Removed hardware registration mechanism, making the software freely available",
            "Added version history display",
            "Added about information display"
        ]
    },
    {
        "version": "1.0.0",
        "date": "2025-03-06",
        "changes": [
            "Added support for specific segment display",
            "Added support for square display",
            "Added decimal point display for single characters",
            "Added Chinese/English language switching",
            "Added custom character style settings",
            "Added hardware registration mechanism for testing"
        ]
    },
    {
        "version": "0.0.0",
        "date": "2024-09-10",
        "changes": [
            "Initial prototype design",
            "Planned feature structure"
        ]
    }
]

# 添加全局样式配置变量
STYLE_CONFIG = {
    'seg_width': 20,              # 段宽度 - 字符横向大小
    'seg_height': 30,             # 段高度 - 字符纵向大小
    'thickness': 4,               # 线条粗细 - 字符线条宽度
    'spacing': 15,                # 间距 - 字符间的间隔
    'x_start': 5,                 # X起点 - 字符起始X坐标偏移
    'dot_size': 3,                # 小数点大小
    'dot_offset_x': -15,          # 小数点X偏移
    'dot_offset_y': -5,           # 小数点Y偏移
    'cell_width': 38,             # 方格宽度 - 每个字符所占单元格宽度
    'cell_height': 38,            # 方格高度 - 每个字符所占单元格高度
    'square_size': 16,            # 正方形大小 - "*"字符显示的方块大小
    'square_offset_x': 0,         # 正方形X偏移 - "*"字符X方向偏移量
    'square_offset_y': 0          # 正方形Y偏移 - "*"字符Y方向偏移量
}

# 样式配置文件保存路径
CONFIG_FILE = 'character_style.json'

# 多语言配置 - 支持中文和英文界面
LANG_CONFIG = {
    # 中文界面文本配置
    'zh_CN': {
        'title': "字符生成器",
        'input_label': "请输入字符:",
        'help_text': "支持输入:\n• 数字和字母\n• *显示方块\n• (abcdefg)显示指定段\n•a: 顶部横线\n•b: 右上竖线\n•c: 中间横线\n•d: 左下竖线\n•e: 底部横线\n•f: 左上竖线\n•g: 右下竖线",
        'generate_btn': "生成字符",
        'style_btn': "调节样式",
        'preview_label': "预览",
        'input_group': "输入",
        'style_title': "样式调节",
        'preview_title': "实时预览",
        'save_btn': "保存样式",
        'reset_btn': "重置默认",
        'adjust_options': "调节选项",
        'char_settings': "字符设置",
        'grid_settings': "方格设置",
        'dot_settings': "小数点设置",
        'square_settings': "方块设置",
        'success_msg': "图片已生成并复制到剪贴板",
        'error_title': "输入错误",
        'min_char_error': "请输入至少一个字符",
        'max_char_error': "最多输入4个字符(不含小数点)",
        'invalid_char_error': "只能输入数字、字母、特殊字符(*、_)或段选择(a-g)",
        'segment_error': "段选择格式错误：缺少右括号",
        'char_width': "字符宽度",
        'char_height': "字符高度",
        'line_thickness': "线条粗细",
        'grid_width': "方格宽度",
        'grid_height': "方格高度",
        'char_spacing': "字符间距",
        'dot_size': "小数点大小",
        'square_size': "方块大小",
        'x_offset': "X偏移",
        'y_offset': "Y偏移",
        'import_license': "导入授权",
        'show_hardware_id': "显示硬件ID",
        'hardware_id_title': "硬件ID",
        'hardware_id_label': "您的硬件ID是:",
        'copy_id': "复制ID",
        'lang_switch': "English"  # 切换到英文按钮文本
    },
    # 英文界面文本配置
    'en_US': {
        'title': "Character Generator",
        'input_label': "Enter characters:",
        'help_text': "Supported input:\n• Numbers and letters\n• * for square\n• (abcdefg) for segments\n•a: Top line\n•b: Top right\n•c: Middle line\n•d: Bottom left\n•e: Bottom line\n•f: Top left\n•g: Bottom right",
        'generate_btn': "Generate",
        'style_btn': "Style",
        'preview_label': "Preview",
        'input_group': "Input",
        'style_title': "Style Adjustment",
        'preview_title': "Live Preview",
        'save_btn': "Save Style",
        'reset_btn': "Reset",
        'adjust_options': "Adjustment Options",
        'char_settings': "Character Settings",
        'grid_settings': "Grid Settings",
        'dot_settings': "Dot Settings",
        'square_settings': "Square Settings",
        'success_msg': "Image generated and copied to clipboard",
        'error_title': "Input Error",
        'min_char_error': "Please enter at least one character",
        'max_char_error': "Maximum 4 characters allowed (excluding dots)",
        'invalid_char_error': "Only numbers, letters, special characters (*,_) or segments (a-g) allowed",
        'segment_error': "Segment selection error: missing right parenthesis",
        'char_width': "Width",
        'char_height': "Height",
        'line_thickness': "Thickness",
        'grid_width': "Grid Width",
        'grid_height': "Grid Height",
        'char_spacing': "Spacing",
        'dot_size': "Dot Size",
        'square_size': "Square Size",
        'x_offset': "X Offset",
        'y_offset': "Y Offset",
        'import_license': "Import License",
        'show_hardware_id': "Show Hardware ID",
        'hardware_id_title': "Hardware ID",
        'hardware_id_label': "Your Hardware ID is:",
        'copy_id': "Copy ID",
        'lang_switch': "中文"  # 切换到中文按钮文本
    }
}

# 默认语言设置为中文
current_lang = 'zh_CN'

def get_segments_rect(x_offset, y_offset, seg_width, seg_height, thickness):
    """
    生成数码管字符各段的坐标信息
    定义字符的各个段（如顶部横线、左上竖线等）的位置和形状
    
    参数:
        x_offset (int): 字符X坐标起点
        y_offset (int): 字符Y坐标起点
        seg_width (int): 段宽度
        seg_height (int): 段高度
        thickness (int): 线条粗细
        
    返回:
        dict: 包含各段坐标的字典
    """
    def rectangle(x, y, width, height):
        """
        创建矩形的四个顶点坐标
        用于绘制字符的直线段
        
        返回:
            list: 包含四个顶点坐标的列表
        """
        return [
            (x, y),                      # 左上角
            (x + width, y),              # 右上角
            (x + width, y + height),     # 右下角
            (x, y + height)              # 左下角
        ]

    def rotated_square(x, y, size, offset_x, offset_y):
        """
        创建旋转45度的正方形坐标
        用于绘制'*'符号的菱形
        
        返回:
            list: 包含四个顶点坐标的列表
        """
        # 计算正方形的中心点，考虑偏移量
        center_x = x + size // 2 + offset_x
        center_y = y + size // 2 + offset_y
        # 计算旋转45度的正方形的四个顶点
        half_size = size // 2
        return [
            (center_x, center_y - half_size),  # 上点
            (center_x + half_size, center_y),  # 右点
            (center_x, center_y + half_size),  # 下点
            (center_x - half_size, center_y)   # 左点
        ]

    # 返回包含所有段坐标的字典
    return {
        'top': rectangle(x_offset, y_offset, seg_width, thickness),  # 顶部横线
        'top_left': rectangle(x_offset, y_offset, thickness, seg_height // 2),  # 左上竖线
        'top_right': rectangle(x_offset + seg_width - thickness, y_offset, thickness, seg_height // 2),  # 右上竖线
        'middle': rectangle(x_offset, y_offset + seg_height // 2 - thickness // 2, seg_width, thickness),  # 中间横线
        'bottom_left': rectangle(x_offset, y_offset + seg_height // 2, thickness, seg_height // 2),  # 左下竖线
        'bottom_right': rectangle(x_offset + seg_width - thickness, y_offset + seg_height // 2, thickness, seg_height // 2),  # 右下竖线
        'bottom': rectangle(x_offset, y_offset + seg_height - thickness, seg_width, thickness),  # 底部横线
        'dot': rectangle(x_offset + seg_width - thickness, y_offset + seg_height - thickness, thickness, thickness),  # 小数点
        # 菱形/旋转的正方形 - 用于显示'*'符号
        'diamond': rotated_square(
            x_offset + thickness, 
            y_offset + thickness,
            STYLE_CONFIG['square_size'],
            STYLE_CONFIG['square_offset_x'],
            STYLE_CONFIG['square_offset_y']
        )
    }

def draw_digit(draw, digit, x_offset, y_offset, seg_width, seg_height, thickness, get_segments):
    """
    绘制单个字符
    根据字符类型，绘制对应的数码管段
    
    参数:
        draw: PIL的ImageDraw对象
        digit (str): 要绘制的字符
        x_offset (int): X坐标起点
        y_offset (int): Y坐标起点
        seg_width (int): 段宽度
        seg_height (int): 段高度
        thickness (int): 线条粗细
        get_segments: 获取段坐标的函数
    """
    # 获取所有段的坐标信息
    segments = get_segments(x_offset, y_offset, seg_width, seg_height, thickness)
    
    # 调试信息输出
    print(f"\nDebug - draw_digit:")
    print(f"Drawing character: '{digit}'")
    print(f"Position: x={x_offset}, y={y_offset}")
    print(f"Size: width={seg_width}, height={seg_height}")
    print(f"Thickness: {thickness}")

    # 字符到段的映射字典 - 定义每个字符应该显示哪些段
    digit_to_segments = {
        # 数字映射
        '0': ['top', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'bottom'],  # 数字0
        'O': ['top', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'bottom'],  # 字母O，同数字0
        '1': ['top_right', 'bottom_right'],  # 数字1
        'I': ['top_right', 'bottom_right'],  # 字母I，同数字1
        '2': ['top', 'top_right', 'middle', 'bottom_left', 'bottom'],  # 数字2
        'Z': ['top', 'top_right', 'middle', 'bottom_left', 'bottom'],  # 字母Z，同数字2
        'z': ['top', 'top_right', 'middle', 'bottom_left', 'bottom'],  # 小写z，同数字2S
        '3': ['top', 'top_right', 'middle', 'bottom_right', 'bottom'],  # 数字3
        '4': ['top_left', 'middle', 'top_right', 'bottom_right'],  # 数字4
        '5': ['top', 'top_left', 'middle', 'bottom_right', 'bottom'],  # 数字5
        'S': ['top', 'top_left', 'middle', 'bottom_right', 'bottom'],  # 字母S，同数字5
        's': ['top', 'top_left', 'middle', 'bottom_right', 'bottom'],  # 小写s，同数字5
        '6': ['top', 'top_left', 'middle', 'bottom_left', 'bottom_right', 'bottom'],  # 数字6
        '7': ['top', 'top_right', 'bottom_right'],  # 数字7
        '8': ['top', 'top_left', 'top_right', 'middle', 'bottom_left', 'bottom_right', 'bottom'],  # 数字8
        'H': ['top_left', 'top_right', 'middle', 'bottom_left', 'bottom_right'],  # 字母H
        'h': ['top_left', 'middle', 'bottom_left', 'bottom_right'],  # 小写h
        '9': ['top', 'top_left', 'top_right', 'middle', 'bottom_right', 'bottom'],  # 数字9
        'g': ['top', 'top_left', 'top_right', 'middle', 'bottom_right', 'bottom'],  # g
        'G': ['top', 'top_left', 'top_right', 'middle', 'bottom_right', 'bottom'],  # G
        'i': [ 'bottom_right'],  # i
        # 字母映射
        'A': ['top', 'top_left', 'top_right', 'middle', 'bottom_left', 'bottom_right'],  # 字母A
        'B': ['top_left', 'middle', 'bottom_left', 'bottom_right', 'bottom'],  # 字母B，大写字母B是8，在数显里就类似8了，所以强制为b
        'b': ['top_left', 'middle', 'bottom_left', 'bottom_right', 'bottom'],  # 小写b
        'C': ['top', 'top_left', 'bottom_left', 'bottom'],  # 字母C
        'c': ['middle', 'bottom_left', 'bottom'],  # 小写c
        'D': ['top_right', 'middle', 'bottom_left', 'bottom_right', 'bottom'],  # 字母D,强制为小写字母d
        'd': ['top_right', 'middle', 'bottom_left', 'bottom_right', 'bottom'],  # 小写d
        'E': ['top', 'top_left', 'middle', 'bottom_left', 'bottom'],  # 字母E
        'e': ['top', 'top_left', 'middle', 'bottom_left', 'bottom'],  # 小写e
        'F': ['top', 'top_left', 'middle', 'bottom_left'],  # 字母F
        'f': ['top', 'top_left', 'middle', 'bottom_left'],  # 小写f
        
        # 特殊字符映射
        '*': ['diamond'],  # 星号显示为菱形
        '.': ['dot'],      # 点号
        '_': ['bottom'],   # 下划线只显示底部横线
        ' ': [],           # 空格不显示任何段
        't': ['top_left', 'middle', 'bottom_left', 'bottom'],  # 小写t
        'T': ['top_left', 'middle', 'bottom_left', 'bottom'],  # 字母T
        'L': ['top_left', 'bottom_left', 'bottom'],  # 字母L
        'l': ['top_left', 'bottom_left'],  # 小写l
        'U': ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'bottom'],  # 字母U
        'u': ['bottom_left', 'bottom_right', 'bottom'],  # 小写u
        'R': ['bottom_left', 'middle'],  # 字母R
        'r': ['bottom_left', 'middle'],  # 小写r
        'o': ['middle', 'bottom_left', 'bottom_right', 'bottom'],  # 小写o
        'P': ['top', 'top_left', 'top_right', 'middle', 'bottom_left'],  # 字母P
        'J': ['top_right', 'bottom_right', 'bottom'],  # 字母J
        'j': ['top_right', 'bottom_right', 'bottom'],  # 小写j
        'c': ['middle', 'bottom_left', 'bottom'],  # 小写c
        'n': ['middle', 'bottom_left', 'bottom_right'],  # 小写n
        'N': ['middle', 'bottom_left', 'bottom_right'],  # 字母N
        'X': ['top_left', 'top_right', 'middle','bottom_left', 'bottom_right'],  # 字母X
        'x': ['top_left', 'top_right', 'middle','bottom_left', 'bottom_right'],  # 小写x
        # 重复定义，可能是误写
        # '*': ['diamond'],
    }

    # 段名称到实际段的映射 - 用于自定义段选择模式
    segment_mapping = {
        'a': ['top'],         # a段 - 顶部横线
        'b': ['top_right'],   # b段 - 右上竖线
        'c': ['middle'],      # c段 - 中间横线
        'd': ['bottom_left'],  # d段 - 左下竖线
        'e': ['bottom'],      # e段 - 底部横线
        'f': ['top_left'],    # f段 - 左上竖线
        'g': ['bottom_right']  # g段 - 右下竖线
    }

    try:
        # 处理段选择模式 - 例如(abcdefg)表示显示特定段
        if digit.startswith('(') and digit.endswith(')'):
            print(f"Debug - Segment selection mode:")
            segments_to_show = [c.lower() for c in digit[1:-1]]  # 提取括号内的段名
            print(f"Requested segments: {segments_to_show}")
            
            # 绘制请求的段
            for seg in segments_to_show:
                if seg in segment_mapping:
                    print(f"  Drawing segment {seg}: {segment_mapping[seg]}")
                    for segment in segment_mapping[seg]:
                        draw.polygon(segments[segment], fill='black')
                else:
                    print(f"  Warning: Invalid segment '{seg}'")
        
        # 处理普通字符 - 使用预定义的字符映射
        else:
            print(f"Debug - Normal character mode:")
            if digit in digit_to_segments:
                segments_to_draw = digit_to_segments[digit]
                print(f"Segments for '{digit}': {segments_to_draw}")
                # 绘制字符的所有段
                for segment in segments_to_draw:
                    print(f"  Drawing segment: {segment}")
                    draw.polygon(segments[segment], fill='black')
            else:
                print(f"Warning: Unknown character '{digit}'")

    except Exception as e:
        # 捕获并记录绘制过程中的错误
        print(f"Error drawing character '{digit}': {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")

def image_to_clipboard(image):
    """
    将图像复制到剪贴板
    将PIL图像对象转换为Windows剪贴板可用的格式并复制
    
    参数:
        image: PIL图像对象
    """
    # 创建字节流用于存储BMP格式数据
    output = BytesIO()
    # 将图像转换为RGB格式并保存为BMP
    image.convert("RGB").save(output, "BMP")
    # 获取BMP数据，跳过头部14字节(BMP文件头)
    data = output.getvalue()[14:]
    output.close()
    
    # 操作Windows剪贴板
    win32clipboard.OpenClipboard()  # 打开剪贴板
    win32clipboard.EmptyClipboard()  # 清空剪贴板内容
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)  # 设置位图数据
    win32clipboard.CloseClipboard()  # 关闭剪贴板

def load_config():
    """
    加载样式配置
    从配置文件读取保存的样式设置
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            global STYLE_CONFIG
            STYLE_CONFIG.update(json.load(f))

def save_config():
    """
    保存样式配置
    将当前样式设置保存到配置文件
    """
    with open(CONFIG_FILE, 'w') as f:
        json.dump(STYLE_CONFIG, f, indent=4)

class StyleAdjustWindow:
    """
    样式调整窗口类
    提供图形界面用于调整字符生成的各种样式参数
    包括字符大小、线条粗细、间距等
    """
    def __init__(self, parent):
        """
        初始化样式调整窗口
        
        参数:
            parent: 父窗口对象，通常是主应用窗口
        """
        # 创建顶层窗口
        self.window = tk.Toplevel(parent)
        self.window.title(LANG_CONFIG[current_lang]['style_title'])  # 设置窗口标题
        self.window.configure(bg='#f0f0f0')  # 设置背景颜色
        self.window.resizable(False, False)  # 禁止调整窗口大小
        
        # 创建主容器框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # 创建预览区域
        preview_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['preview_title'], 
                                     padding="10")
        preview_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # 预览标签 - 用于显示实时预览图像
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.grid(row=0, column=0, pady=5)
        
        # 创建调节控件区域
        controls_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['adjust_options'], 
                                      padding="10")
        controls_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        # 创建分类的调节选项
        self.create_adjustment_sections(controls_frame)
        
        # 创建按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        # 保存样式按钮
        save_btn = ttk.Button(button_frame, 
                            text=LANG_CONFIG[current_lang]['save_btn'], 
                            command=self.save_style, 
                            width=15)
        save_btn.grid(row=0, column=0, padx=10)
        
        # 重置默认按钮
        reset_btn = ttk.Button(button_frame, 
                             text=LANG_CONFIG[current_lang]['reset_btn'], 
                             command=self.reset_style, 
                             width=15)
        reset_btn.grid(row=0, column=1, padx=10)

        # 语言切换按钮区域 - 放在最底部
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=3, column=0, pady=(5, 0), sticky='e')
        
        # 创建语言切换按钮
        self.lang_btn = ttk.Button(lang_frame, 
                                 text='English' if current_lang == 'zh_CN' else '中文',
                                 command=self.switch_language,
                                 style='Language.TButton',
                                 width=8)
        self.lang_btn.grid(row=0, column=0)

        # 初始化预览图像
        self.update_preview()

    def switch_language(self):
        """
        切换界面语言
        调用全局语言切换函数，并更新当前窗口的语言
        """
        # 调用全局语言切换函数
        switch_language()
        # 更新样式窗口的语言
        self.update_window_language()

    def update_window_language(self):
        """
        更新窗口的所有文本为当前选择的语言
        包括窗口标题、标签文本和按钮文本
        """
        # 更新窗口标题
        self.window.title(LANG_CONFIG[current_lang]['style_title'])
        
        # 更新预览区域和调整选项区域的标题
        for child in self.window.winfo_children():
            if isinstance(child, ttk.Frame):
                for frame in child.winfo_children():
                    if isinstance(frame, ttk.LabelFrame):
                        if 'preview' in str(frame):
                            frame.configure(text=LANG_CONFIG[current_lang]['preview_title'])
                        elif 'adjust' in str(frame):
                            frame.configure(text=LANG_CONFIG[current_lang]['adjust_options'])

        # 更新按钮文本
        for child in self.window.winfo_children():
            if isinstance(child, ttk.Frame):
                for frame in child.winfo_children():
                    if isinstance(frame, ttk.Frame):
                        for button in frame.winfo_children():
                            if isinstance(button, ttk.Button):
                                if 'save' in str(button):
                                    button.configure(text=LANG_CONFIG[current_lang]['save_btn'])
                                elif 'reset' in str(button):
                                    button.configure(text=LANG_CONFIG[current_lang]['reset_btn'])
                                elif 'lang' in str(button):
                                    button.configure(text='English' if current_lang == 'zh_CN' else '中文')

        # 重新创建调节选项区域
        for child in self.window.winfo_children():
            if isinstance(child, ttk.Frame):
                for frame in child.winfo_children():
                    if isinstance(frame, ttk.LabelFrame):
                        if 'controls' in str(frame):
                            # 清除现有的控件
                            for widget in frame.winfo_children():
                                widget.destroy()
                            # 重新创建调节选项
                            self.create_adjustment_sections(frame)

    def create_adjustment_sections(self, parent):
        """
        创建分类的样式调整区域
        将调整选项分为字符设置、方格设置、小数点设置和方块设置四类
        
        参数:
            parent: 父容器，用于放置调整控件
        """
        # 定义分类的调节选项
        sections = {
            # 字符设置区域
            LANG_CONFIG[current_lang]['char_settings']: [
                (LANG_CONFIG[current_lang]['char_width'], 'seg_width', 10, 30),  # 字符宽度
                (LANG_CONFIG[current_lang]['char_height'], 'seg_height', 20, 40),  # 字符高度
                (LANG_CONFIG[current_lang]['line_thickness'], 'thickness', 2, 6)  # 线条粗细
            ],
            # 方格设置区域
            LANG_CONFIG[current_lang]['grid_settings']: [
                (LANG_CONFIG[current_lang]['grid_width'], 'cell_width', 15, 50),  # 方格宽度
                (LANG_CONFIG[current_lang]['grid_height'], 'cell_height', 15, 50),  # 方格高度
                (LANG_CONFIG[current_lang]['char_spacing'], 'spacing', 8, 25)  # 字符间距
            ],
            # 小数点设置区域
            LANG_CONFIG[current_lang]['dot_settings']: [
                (LANG_CONFIG[current_lang]['dot_size'], 'dot_size', 2, 5),  # 小数点大小
                (LANG_CONFIG[current_lang]['x_offset'], 'dot_offset_x', -15, 15),  # X偏移
                (LANG_CONFIG[current_lang]['y_offset'], 'dot_offset_y', -15, 15)  # Y偏移
            ],
            # 方块设置区域 - 用于"*"字符
            LANG_CONFIG[current_lang]['square_settings']: [
                (LANG_CONFIG[current_lang]['square_size'], 'square_size', 8, 30),  # 方块大小
                (LANG_CONFIG[current_lang]['x_offset'], 'square_offset_x', -15, 15),  # X偏移
                (LANG_CONFIG[current_lang]['y_offset'], 'square_offset_y', -15, 15)  # Y偏移
            ]
        }
        
        # 创建每个分类的框架和调整控件
        row = 0
        for section_name, adjustments in sections.items():
            # 为每类调整创建标签框
            section_frame = ttk.LabelFrame(parent, text=section_name, padding="5")
            section_frame.grid(row=row, column=0, padx=5, pady=5, sticky='ew')
            
            # 在每个分类框架中添加调整控件
            for idx, (label_text, config_key, min_val, max_val) in enumerate(adjustments):
                self.create_adjustment_row(section_frame, idx, label_text, config_key, min_val, max_val)
            
            row += 1

    def create_adjustment_row(self, parent, row, label_text, config_key, min_val, max_val):
        """
        创建单个调整控件行
        包含标签、滑动条和数值显示
        
        参数:
            parent: 父容器
            row (int): 行索引
            label_text (str): 标签文本
            config_key (str): 配置键名
            min_val (int): 最小值
            max_val (int): 最大值
        """
        # 创建控件容器框架
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, pady=2, sticky='ew')
        
        # 添加标签
        ttk.Label(frame, text=label_text, width=8).grid(row=0, column=0, padx=5)
        
        # 添加滑动条控件
        scale = ttk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            value=STYLE_CONFIG[config_key],  # 设置当前值
            orient=tk.HORIZONTAL,
            length=150,
            command=lambda v, key=config_key: self.on_scale_change(v, key)  # 滑动时调用的函数
        )
        scale.grid(row=0, column=1, padx=5)
        
        # 添加显示当前值的标签
        value_label = ttk.Label(frame, width=3)
        value_label.grid(row=0, column=2, padx=5)
        value_label.configure(text=str(STYLE_CONFIG[config_key]))
        # 保存标签的引用，以便后续更新
        setattr(self, f"{config_key}_label", value_label)

    def on_scale_change(self, value, key):
        """
        滑动条值改变时的回调函数
        更新配置值和显示标签
        
        参数:
            value (float): 滑动条的当前值
            key (str): 对应的配置键名
        """
        # 四舍五入为整数
        value = round(float(value))
        # 更新全局配置
        STYLE_CONFIG[key] = value
        # 更新显示的值
        getattr(self, f"{key}_label").configure(text=str(value))
        # 实时更新预览图像
        self.update_preview()

    def update_preview(self):
        """
        更新预览图像
        根据当前样式设置生成预览图像
        """
        # 使用配置中的方格大小
        CELL_WIDTH = STYLE_CONFIG['cell_width']
        CELL_HEIGHT = STYLE_CONFIG['cell_height']
        TOTAL_WIDTH = CELL_WIDTH * 4  # 总宽度容纳4个字符
        TOTAL_HEIGHT = CELL_HEIGHT    # 高度为单个字符高度
        
        # 创建预览图像 - 白色背景
        image = Image.new('RGB', (TOTAL_WIDTH, TOTAL_HEIGHT), 'white')
        draw = ImageDraw.Draw(image)
        
        # 绘制水平边框线
        for y in [0, CELL_HEIGHT]:
            draw.line([(0, y), (TOTAL_WIDTH, y)], fill='black', width=1)
        
        # 绘制垂直边框线
        for x in range(5):  # 5根线分隔4个单元格
            x_pos = x * CELL_WIDTH
            if x == 4:  # 最后一根线在最右边
                x_pos = TOTAL_WIDTH - 1
            draw.line([(x_pos, 0), (x_pos, TOTAL_HEIGHT)], 
                     fill='black', width=1)

        # 确保底部边框完整显示
        draw.line([(0, TOTAL_HEIGHT - 1), (TOTAL_WIDTH - 1, TOTAL_HEIGHT - 1)], 
                 fill='black', width=1)

        # 绘制示例字符
        chars = ["8", "*", "8", "8"]  # 使用这些字符预览效果
        for i, char in enumerate(chars):
            # 计算字符在方格中的居中位置
            char_width = STYLE_CONFIG['seg_width']
            char_height = STYLE_CONFIG['seg_height']
            spacing = STYLE_CONFIG['spacing']
            
            # 计算字符X坐标 - 基础X位置加上间距调整
            base_x = i * CELL_WIDTH
            x = base_x + (CELL_WIDTH - char_width - spacing) // 2 + STYLE_CONFIG['x_start']
            # 计算字符Y坐标 - 垂直居中
            y = (CELL_HEIGHT - char_height) // 2
            
            # 绘制字符
            draw_digit(draw, char, x, y,
                      char_width, char_height,
                      STYLE_CONFIG['thickness'], get_segments_rect)

            # 为每个字符添加小数点（包括最后一个）
            dot_x = base_x + CELL_WIDTH - STYLE_CONFIG['dot_offset_x']
            dot_y = CELL_HEIGHT - STYLE_CONFIG['dot_offset_y'] - STYLE_CONFIG['dot_size']
            draw.rectangle([
                (dot_x, dot_y),
                (dot_x + STYLE_CONFIG['dot_size'], dot_y + STYLE_CONFIG['dot_size'])
            ], fill='black')

        # 将图像转换为Tkinter可用的格式
        photo = ImageTk.PhotoImage(image)
        # 更新预览标签显示
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo  # 保持引用防止被垃圾回收

    def save_style(self):
        """
        保存当前样式设置
        将样式配置写入文件并显示确认消息
        """
        save_config()  # 调用全局保存函数
        messagebox.showinfo("成功", "样式配置已保存")

    def reset_style(self):
        """
        重置样式为默认值
        恢复所有设置到初始状态并更新界面
        """
        global STYLE_CONFIG
        # 重置为默认配置
        STYLE_CONFIG = {
            'seg_width': 20,
            'seg_height': 30,
            'thickness': 4,
            'spacing': 15,
            'x_start': 5,
            'dot_size': 3,
            'dot_offset_x': -15,
            'dot_offset_y': -5,
            'cell_width': 38,
            'cell_height': 38,
            'square_size': 16,
            'square_offset_x': 0,
            'square_offset_y': 0
        }
        # 更新预览和显示值
        self.update_preview()
        for key in STYLE_CONFIG:
            getattr(self, f"{key}_label").configure(text=str(STYLE_CONFIG[key]))

def generate_image():
    try:
        input_text = entry_text.get()   # FIXME:不转为大写
        text_without_dot = input_text.replace('.', '')
        
        print("\nDebug - generate_image:")
        print(f"Input text: {input_text}")
        print(f"Text without dots: {text_without_dot}")
        
        if not text_without_dot:
            raise ValueError(LANG_CONFIG[current_lang]['min_char_error'])

        # 初始化图片和相关变量
        CELL_WIDTH = STYLE_CONFIG['cell_width']
        CELL_HEIGHT = STYLE_CONFIG['cell_height']
        TOTAL_WIDTH = CELL_WIDTH * 4
        TOTAL_HEIGHT = CELL_HEIGHT
        
        image = Image.new('RGB', (TOTAL_WIDTH, TOTAL_HEIGHT), 'white')
        draw = ImageDraw.Draw(image)

        # 计算有效字符数并处理段选择
        effective_length = 0
        i = 0
        processed_chars = []  # 存储处理后的字符
        dot_positions = []    # 存储小数点位置

        # 第一步：处理字符和收集小数点位置
        char_index = 0
        input_index = 0
        while input_index < len(input_text):
            if input_text[input_index] == '.':
                if char_index > 0:  # 确保前面有字符
                    dot_positions.append(char_index - 1)
                input_index += 1
            elif input_text[input_index] == '(':
                # 处理段选择
                end_pos = input_text.find(')', input_index)
                if end_pos == -1:
                    raise ValueError(LANG_CONFIG[current_lang]['segment_error'])
                segment_group = input_text[input_index:end_pos+1]
                processed_chars.append(segment_group)
                print(f"Debug: Found segment group: {segment_group}")
                effective_length += 1
                char_index += 1
                input_index = end_pos + 1
            else:
                processed_chars.append(input_text[input_index])
                effective_length += 1
                char_index += 1
                input_index += 1

        print(f"Debug: Processed chars: {processed_chars}")
        print(f"Debug: Dot positions: {dot_positions}")

        if effective_length > 4:
            raise ValueError(LANG_CONFIG[current_lang]['max_char_error'])

        # 绘制方格边框
        for y in [0, CELL_HEIGHT]:
            draw.line([(0, y), (TOTAL_WIDTH, y)], fill='black', width=1)
        
        for x in range(5):
            x_pos = x * CELL_WIDTH
            if x == 4:
                x_pos = TOTAL_WIDTH - 1
            draw.line([(x_pos, 0), (x_pos, TOTAL_HEIGHT)], 
                     fill='black', width=1)

        draw.line([(0, TOTAL_HEIGHT - 1), (TOTAL_WIDTH - 1, TOTAL_HEIGHT - 1)], 
                 fill='black', width=1)

        # 第二步：绘制字符
        print("\nDebug: 开始绘制字符")
        for i, char in enumerate(processed_chars):
            print(f"Drawing processed char: {char}")
            # 计算字符在方格中的居中位置
            char_width = STYLE_CONFIG['seg_width']
            char_height = STYLE_CONFIG['seg_height']
            x = i * CELL_WIDTH + (CELL_WIDTH - char_width) // 2
            y = (CELL_HEIGHT - char_height) // 2
            
            # 绘制字符
            draw_digit(draw, char, x, y,
                      char_width, char_height,
                      STYLE_CONFIG['thickness'], get_segments_rect)
            print(f"Completed drawing char at index {i}")

        # 第三步：绘制小数点
        print(f"Debug: Drawing dots at positions: {dot_positions}")
        for pos in dot_positions:
            dot_x = (pos + 1) * CELL_WIDTH - STYLE_CONFIG['dot_offset_x']
            dot_y = CELL_HEIGHT - STYLE_CONFIG['dot_offset_y'] - STYLE_CONFIG['dot_size']
            
            print(f"Debug: Drawing dot at x={dot_x}, y={dot_y}")
            draw.rectangle([
                (dot_x, dot_y),
                (dot_x + STYLE_CONFIG['dot_size'], dot_y + STYLE_CONFIG['dot_size'])
            ], fill='black')

        # 保存和显示图片
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.png")
        image.save(file_path)
        image_to_clipboard(image)
        messagebox.showinfo("Success", LANG_CONFIG[current_lang]['success_msg'])
        
        preview_image(image)
    except ValueError as e:
        messagebox.showerror(LANG_CONFIG[current_lang]['error_title'], str(e))
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

def preview_image(image):
    """在主窗口预览图片"""
    # 调整图片大小以适应预览
    preview_width = 200  # 设置预览宽度
    ratio = preview_width / image.size[0]
    preview_height = int(image.size[1] * ratio)
    
    # 创建预览图片
    preview = image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(preview)
    
    # 更新预览标签
    preview_label.configure(image=photo)
    preview_label.image = photo  # 保持引用以防止被垃圾回收

def validate_input(P):
    # 移除小数点后检查字符数
    text_without_dot = P.replace('.', '')
    # 检查非点字符是否在允许范围内
    valid_chars = all(c.isdigit() or c.upper() in 'ABCDEFTLUHURSOPJN_' for c in text_without_dot)
    return len(text_without_dot) <= 4 and valid_chars

def open_email():
    webbrowser.open("mailto:yue.xu@schindler.com")

def get_char(r, g, b, alpha=256):
    # 修复转义字符问题
    ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
    
    if alpha == 0:
        return ' '
    
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
    unit = (256.0 + 1) / length
    
    return ascii_char[int(gray/unit)]

def switch_language():
    global current_lang
    current_lang = 'en_US' if current_lang == 'zh_CN' else 'zh_CN'
    update_ui_language()

def update_ui_language():
    """
    更新界面语言
    将所有界面元素更新为当前选择的语言
    """
    # 更新主窗口标题
    root.title(LANG_CONFIG[current_lang]['title'])
    
    # 更新输入区域文本
    input_frame.configure(text=LANG_CONFIG[current_lang]['input_group'])
    input_label.configure(text=LANG_CONFIG[current_lang]['input_label'])
    help_label.configure(text=LANG_CONFIG[current_lang]['help_text'])
    
    # 更新主要按钮文本
    generate_btn.configure(text=LANG_CONFIG[current_lang]['generate_btn'])
    style_btn.configure(text=LANG_CONFIG[current_lang]['style_btn'])
    
    # 更新底部按钮文本
    version_btn.configure(text="版本历史" if current_lang == 'zh_CN' else "Version History")
    about_btn.configure(text="关于" if current_lang == 'zh_CN' else "About")
    lang_btn.configure(text=LANG_CONFIG[current_lang]['lang_switch'])
    
    # 更新预览区域标题
    preview_frame.configure(text=LANG_CONFIG[current_lang]['preview_label'])

def show_version_history():
    """
    显示版本变更历史
    创建一个对话框显示软件的版本更新记录
    """
    # 创建对话框
    dialog = tk.Toplevel(root)
    dialog.title("版本历史" if current_lang == 'zh_CN' else "Version History")
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    
    # 创建主框架
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 创建标题标签
    title_label = ttk.Label(
        main_frame, 
        text="字符生成器版本历史" if current_lang == 'zh_CN' else "Character Generator Version History",
        font=('Arial', 12, 'bold')
    )
    title_label.pack(pady=(0, 15))
    
    # 创建滚动文本区域
    text_area = scrolledtext.ScrolledText(
        main_frame, 
        wrap=tk.WORD,
        width=50,
        height=15,
        font=('Arial', 10)
    )
    text_area.pack(fill=tk.BOTH, expand=True)
    text_area.configure(state='normal')
    
    # 根据当前语言选择对应的版本历史
    version_history = VERSION_HISTORY_CN if current_lang == 'zh_CN' else VERSION_HISTORY_EN
    
    # 添加版本历史内容
    for version_info in version_history:
        # 添加版本号和日期
        version_text = f"版本 {version_info['version']} ({version_info['date']})\n" if current_lang == 'zh_CN' else \
                       f"Version {version_info['version']} ({version_info['date']})\n"
        text_area.insert(tk.END, version_text, "version")
        
        # 添加变更内容
        for change in version_info['changes']:
            text_area.insert(tk.END, f"• {change}\n", "change")
        
        text_area.insert(tk.END, "\n")
    
    # 设置标签样式
    text_area.tag_configure("version", font=('Arial', 10, 'bold'))
    text_area.tag_configure("change", font=('Arial', 9))
    
    # 设置为只读
    text_area.configure(state='disabled')
    
    # 添加关闭按钮
    close_btn = ttk.Button(
        main_frame, 
        text="关闭" if current_lang == 'zh_CN' else "Close",
        command=dialog.destroy
    )
    close_btn.pack(pady=15)

def show_about():
    """
    显示关于信息
    创建一个对话框显示软件信息和开发者信息
    """
    # 创建对话框
    dialog = tk.Toplevel(root)
    dialog.title("关于" if current_lang == 'zh_CN' else "About")
    dialog.geometry("400x300")
    dialog.resizable(False, False)
    
    # 创建主框架
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 创建标题标签
    title_label = ttk.Label(
        main_frame, 
        text="字符生成器" if current_lang == 'zh_CN' else "Character Generator",
        font=('Arial', 14, 'bold')
    )
    title_label.pack(pady=(0, 5))
    
    # 创建版本标签
    version_label = ttk.Label(
        main_frame, 
        text=f"版本 {VERSION}" if current_lang == 'zh_CN' else f"Version {VERSION}",
        font=('Arial', 10)
    )
    version_label.pack(pady=(0, 15))
    
    # 创建描述标签
    description_text = (
        "字符生成器是一个用于创建数码管风格字符的工具，"
        "支持数字、字母和特殊字符的生成，"
        "可以自定义字符样式和大小。"
    ) if current_lang == 'zh_CN' else (
        "Character Generator is a tool for creating "
        "seven-segment display style characters. "
        "It supports numbers, letters and special characters, "
        "with customizable styles and sizes."
    )
    
    description_label = ttk.Label(
        main_frame, 
        text=description_text,
        font=('Arial', 9),
        wraplength=350,
        justify='center'
    )
    description_label.pack(pady=10)
    
    # 创建开发者信息标签
    developer_label = ttk.Label(
        main_frame, 
        text="开发者: Yue Xu" if current_lang == 'zh_CN' else "Developer: Yue Xu",
        font=('Arial', 9)
    )
    developer_label.pack(pady=5)
    
    # 创建邮箱标签（可点击）
    email_label = ttk.Label(
        main_frame, 
        text="yue.xu@schindler.com",
        font=('Arial', 9),
        foreground='blue',
        cursor='hand2'
    )
    email_label.pack(pady=5)
    email_label.bind("<Button-1>", lambda e: open_email())
    
    # 创建版权标签
    copyright_label = ttk.Label(
        main_frame, 
        text=f"© {datetime.datetime.now().year} Schindler",
        font=('Arial', 9)
    )
    copyright_label.pack(pady=10)
    
    # 添加关闭按钮
    close_btn = ttk.Button(
        main_frame, 
        text="关闭" if current_lang == 'zh_CN' else "Close",
        command=dialog.destroy
    )
    close_btn.pack(pady=5)

def create_main_window():
    """
    创建主窗口
    设置应用程序的主界面布局和控件
    """
    global root, input_frame, input_label, help_label, generate_btn, style_btn, lang_btn, preview_frame
    global version_btn, about_btn
    
    # 设置窗口标题和样式
    root.title(LANG_CONFIG[current_lang]['title'])
    root.configure(bg='#f0f0f0')  # 设置背景色
    root.resizable(False, False)  # 禁止调整窗口大小
    
    # 创建主容器
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 创建输入区域
    input_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['input_group'], padding="10")
    input_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    # 输入标签
    input_label = ttk.Label(input_frame, text=LANG_CONFIG[current_lang]['input_label'])
    input_label.grid(row=0, column=0, padx=5)
    
    # 输入文本框
    global entry_text
    entry_text = ttk.Entry(input_frame, width=15)
    entry_text.grid(row=0, column=1, padx=5)
    
    # 帮助文本标签
    help_label = ttk.Label(input_frame, text=LANG_CONFIG[current_lang]['help_text'], justify='left')
    help_label.grid(row=1, column=0, columnspan=2, pady=(5,0), sticky='w')
    
    # 创建功能按钮区域
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, pady=10)
    
    # 生成字符按钮
    generate_btn = ttk.Button(button_frame, text=LANG_CONFIG[current_lang]['generate_btn'], 
                            command=generate_image)
    generate_btn.grid(row=0, column=0, padx=5)
    
    # 调节样式按钮
    style_btn = ttk.Button(button_frame, text=LANG_CONFIG[current_lang]['style_btn'], 
                          command=lambda: StyleAdjustWindow(root))
    style_btn.grid(row=0, column=1, padx=5)
    
    # 创建底部按钮区域
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.grid(row=3, column=0, pady=(5, 0), sticky='e')
    
    # 定义底部按钮样式
    style = ttk.Style()
    style.configure('Bottom.TButton', padding=3)  # 小巧的按钮样式
    
    # 版本历史按钮
    version_btn = ttk.Button(bottom_frame, 
                         text="版本历史" if current_lang == 'zh_CN' else "Version History",
                         command=show_version_history,
                         style='Bottom.TButton',
                         width=10)
    version_btn.grid(row=0, column=0, padx=2)
    
    # 关于按钮
    about_btn = ttk.Button(bottom_frame,
                          text="关于" if current_lang == 'zh_CN' else "About",
                          command=show_about,
                          style='Bottom.TButton',
                          width=10)
    about_btn.grid(row=0, column=1, padx=2)
    
    # 语言切换按钮
    global lang_btn
    lang_btn = ttk.Button(bottom_frame, 
                         text=LANG_CONFIG[current_lang]['lang_switch'],
                         command=switch_language,
                         style='Bottom.TButton',
                         width=8)
    lang_btn.grid(row=0, column=2, padx=2)

    # 创建预览区域
    preview_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['preview_label'], 
                                 padding="10")
    preview_frame.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
    
    # 预览图像标签
    global preview_label
    preview_label = ttk.Label(preview_frame)
    preview_label.grid(row=0, column=0, pady=5)
    
    # 创建初始空白预览图片
    empty_image = Image.new('RGB', (200, 50), 'white')
    preview_image(empty_image)

# 程序入口点
if __name__ == '__main__':
    try:
        # 创建主窗口
        root = tk.Tk()
        create_main_window()
        # 加载保存的样式配置
        load_config()
        # 启动事件循环
        root.mainloop()
    except Exception as e:
        # 捕获启动过程中的任何错误
        messagebox.showerror(
            "错误" if current_lang == 'zh_CN' else "Error",
            f"程序启动失败: {str(e)}" if current_lang == 'zh_CN' else f"Failed to start: {str(e)}"
        )
        sys.exit(1)
