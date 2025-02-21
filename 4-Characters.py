import tkinter as tk
from tkinter import messagebox, Toplevel, Label, ttk
from PIL import Image, ImageDraw, ImageTk
import os
import win32clipboard
from io import BytesIO
import webbrowser
import json
import datetime
import sys
import hashlib
import uuid
import wmi
import base64
from cryptography.fernet import Fernet
import winreg

# 添加全局配置变量
STYLE_CONFIG = {
    'seg_width': 20,
    'seg_height': 30,
    'thickness': 4,
    'spacing': 15,
    'x_start': 5,
    'dot_size': 3,
    'dot_offset_x': -15,
    'dot_offset_y': -5,
    'cell_width': 38,  # 方格宽度
    'cell_height': 38,  # 方格高度
    'square_size': 16,      # 正方形大小
    'square_offset_x': 0,   # 正方形X偏移
    'square_offset_y': 0    # 正方形Y偏移
}

# 添加配置文件路径
CONFIG_FILE = 'character_style.json'

# 添加语言配置
LANG_CONFIG = {
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
        'lang_switch': "English"  # 切换到英文
    },
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
        'lang_switch': "中文"  # 切换到中文
    }
}

# 当前语言设置
current_lang = 'zh_CN'

def get_hardware_id():
    """获取硬件特征码"""
    try:
        computer = wmi.WMI()
        
        # 收集硬件信息
        cpu_info = computer.Win32_Processor()[0].ProcessorId.strip()
        bios_info = computer.Win32_BIOS()[0].SerialNumber.strip()
        disk_info = computer.Win32_DiskDrive()[0].SerialNumber.strip()
        
        # 组合硬件信息
        hardware_str = f"{cpu_info}_{bios_info}_{disk_info}"
        
        # 生成特征码
        return hashlib.sha256(hardware_str.encode()).hexdigest()
    except Exception:
        # 如果获取硬件信息失败，使用备用方法
        mac = uuid.getnode()
        return hashlib.sha256(str(mac).encode()).hexdigest()

class LicenseManager:
    def __init__(self):
        self.key = base64.urlsafe_b64encode(hashlib.sha256(get_hardware_id().encode()).digest())
        self.cipher_suite = Fernet(self.key)
        self.registry_path = r"Software\CharacterGenerator"
        self.registry_name = "license"

    def import_license(self, license_code):
        """导入授权码"""
        try:
            # 解码并解密授权码
            encrypted_data = base64.b64decode(license_code)
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data)
            
            # 验证硬件ID
            if license_data["hardware_id"] != get_hardware_id():
                raise Exception("授权码与当前设备不匹配")
            
            # 保存到注册表
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            winreg.SetValueEx(key, self.registry_name, 0, winreg.REG_BINARY, encrypted_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            raise Exception(f"导入授权码失败: {str(e)}")

    def save_license(self, expiration_date):
        """保存许可信息"""
        try:
            # 创建许可数据
            license_data = {
                "hardware_id": get_hardware_id(),
                "expiration_date": expiration_date.isoformat(),
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # 加密许可数据
            encrypted_data = self.cipher_suite.encrypt(json.dumps(license_data).encode())
            
            # 保存到注册表
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            winreg.SetValueEx(key, self.registry_name, 0, winreg.REG_BINARY, encrypted_data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"保存许可失败: {str(e)}")
            return False

    def load_license(self):
        """加载许可信息"""
        try:
            # 从注册表读取
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_READ)
            encrypted_data = winreg.QueryValueEx(key, self.registry_name)[0]
            winreg.CloseKey(key)
            
            # 解密数据
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data)
            
            # 验证硬件特征码
            if license_data["hardware_id"] != get_hardware_id():
                return None
                
            return datetime.datetime.fromisoformat(license_data["expiration_date"])
        except Exception:
            return None

def check_expiration():
    """检查软件是否过期"""
    try:
        license_manager = LicenseManager()
        expiration_date = license_manager.load_license()
        
        # 如果没有许可信息，创建新的（半年期限）
        if expiration_date is None:
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=180)
            if not license_manager.save_license(expiration_date):
                raise Exception("无法创建许可信息")
        
        current_date = datetime.datetime.now()
        if current_date > expiration_date:
            messagebox.showerror(
                "软件已过期" if current_lang == 'zh_CN' else "Software Expired",
                "该软件已过期，请联系管理员更新。\n\n"
                f"Hardware ID: {get_hardware_id()}" if current_lang == 'zh_CN' else 
                "This software has expired. Please contact administrator for updates.\n\n"
                f"Hardware ID: {get_hardware_id()}"
            )
            return False
        
        # 计算剩余天数
        days_remaining = (expiration_date - current_date).days
        if days_remaining <= 30:  # 如果剩余天数少于30天，显示提醒
            messagebox.showwarning(
                "使用期限提醒" if current_lang == 'zh_CN' else "Expiration Notice",
                f"软件将在 {days_remaining} 天后过期，请及时更新。\n\n"
                f"Hardware ID: {get_hardware_id()}" if current_lang == 'zh_CN' else
                f"Software will expire in {days_remaining} days. Please update soon.\n\n"
                f"Hardware ID: {get_hardware_id()}"
            )
        return True
    except Exception as e:
        messagebox.showerror(
            "许可验证错误" if current_lang == 'zh_CN' else "License Error",
            f"许可验证失败: {str(e)}\n\n"
            f"Hardware ID: {get_hardware_id()}" if current_lang == 'zh_CN' else
            f"License verification failed: {str(e)}\n\n"
            f"Hardware ID: {get_hardware_id()}"
        )
        return False

def get_segments_rect(x_offset, y_offset, seg_width, seg_height, thickness):
    def rectangle(x, y, width, height):
        return [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height)
        ]

    def rotated_square(x, y, size, offset_x, offset_y):
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

    return {
        'top': rectangle(x_offset, y_offset, seg_width, thickness),
        'top_left': rectangle(x_offset, y_offset, thickness, seg_height // 2),
        'top_right': rectangle(x_offset + seg_width - thickness, y_offset, thickness, seg_height // 2),
        'middle': rectangle(x_offset, y_offset + seg_height // 2 - thickness // 2, seg_width, thickness),
        'bottom_left': rectangle(x_offset, y_offset + seg_height // 2, thickness, seg_height // 2),
        'bottom_right': rectangle(x_offset + seg_width - thickness, y_offset + seg_height // 2, thickness, seg_height // 2),
        'bottom': rectangle(x_offset, y_offset + seg_height - thickness, seg_width, thickness),
        'dot': rectangle(x_offset + seg_width - thickness, y_offset + seg_height - thickness, thickness, thickness),
        # 将菱形改为旋转的正方形
        'diamond': rotated_square(
            x_offset + thickness, 
            y_offset + thickness,
            STYLE_CONFIG['square_size'],
            STYLE_CONFIG['square_offset_x'],
            STYLE_CONFIG['square_offset_y']
        )
    }

def draw_digit(draw, digit, x_offset, y_offset, seg_width, seg_height, thickness, get_segments):
    segments = get_segments(x_offset, y_offset, seg_width, seg_height, thickness)
    
    print(f"\nDebug - draw_digit:")
    print(f"Drawing digit: '{digit}'")
    print(f"Position: x={x_offset}, y={y_offset}")
    print(f"Size: width={seg_width}, height={seg_height}")
    
    # 扩展字符映射以支持自定义段显示
    digit_to_segments = {
        '0': ['top', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'bottom'],
        'O': ['top', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'bottom'],
        '1': ['top_right', 'bottom_right'],
        '2': ['top', 'top_right', 'middle', 'bottom_left', 'bottom'],
        '3': ['top', 'top_right', 'middle', 'bottom_right', 'bottom'],
        '4': ['top_left', 'middle', 'top_right', 'bottom_right'],
        '5': ['top', 'top_left', 'middle', 'bottom_right', 'bottom'],
        'S': ['top', 'top_left', 'middle', 'bottom_right', 'bottom'],
        's': ['top', 'top_left', 'middle', 'bottom_right', 'bottom'],
        '6': ['top', 'top_left', 'middle', 'bottom_left', 'bottom_right', 'bottom'],
        '7': ['top', 'top_right', 'bottom_right'],
        '8': ['top', 'top_left', 'top_right', 'middle', 'bottom_left', 'bottom_right', 'bottom'],
        'H': ['top_left', 'top_right', 'middle', 'bottom_left', 'bottom_right'],
        'h': ['top_left', 'middle', 'bottom_left', 'bottom_right'],
        '9': ['top', 'top_left', 'top_right', 'middle', 'bottom_right', 'bottom'],
        'A': ['top', 'top_left', 'top_right', 'middle', 'bottom_left', 'bottom_right'],
        'B': ['top_left', 'middle', 'bottom_left', 'bottom_right', 'bottom'],
        'b': ['top_left', 'middle', 'bottom_left', 'bottom_right', 'bottom'],
        'C': ['top', 'top_left', 'bottom_left', 'bottom'],
        'D': ['top_right', 'middle', 'bottom_left', 'bottom_right', 'bottom'],
        'd': ['top_right', 'middle', 'bottom_left', 'bottom_right', 'bottom'],
        'E': ['top', 'top_left', 'middle', 'bottom_left', 'bottom'],
        'e': ['top', 'top_left', 'middle', 'bottom_left', 'bottom'],
        'F': ['top', 'top_left', 'middle', 'bottom_left'],
        'f': ['top', 'top_left', 'middle', 'bottom_left'],
        '_': ['bottom'],
        ' ': [],
        't': ['top_left', 'middle', 'bottom_left', 'bottom'],
        'T': ['top_left', 'middle', 'bottom_left', 'bottom'],
        'L': ['top_left', 'bottom_left', 'bottom'],
        'l': ['top_left', 'bottom_left', 'bottom'],
        'U': ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'bottom'],
        'u': ['bottom_left', 'bottom_right', 'bottom'],
        'R': ['bottom_left', 'middle'],
        'r': ['bottom_left', 'middle'],
        'o': ['middle', 'bottom_left', 'bottom_right', 'bottom'],
        'P': ['top', 'top_left', 'top_right', 'middle', 'bottom_left'],
        'J': ['top_right', 'bottom_right', 'bottom'],
        '.': ['dot'],
        'c': ['middle', 'bottom_left', 'bottom'],
        'n': ['middle', 'bottom_left', 'bottom_right'],
        # 添加菱形显示
        '*': ['diamond'],
        # 添加自定义段显示支持
        'a': ['top'],
        'b': ['top_right'],
        'c': ['middle'],
        'd': ['bottom_left'],
        'e': ['bottom'],
        'f': ['top_left'],
        'g': ['bottom_right']
    }
    
    # 支持自定义段组合
    if digit.startswith('(') and digit.endswith(')'):
        print(f"Debug - Segment mode detected for: {digit}")
        segments_to_show = [c.lower() for c in digit[1:-1]]  # 转换为小写
        print(f"Segments to show: {segments_to_show}")
        
        for seg in segments_to_show:
            print(f"Processing segment: {seg}")
            if seg in digit_to_segments:
                print(f"  Found mapping for {seg}: {digit_to_segments[seg]}")
                for segment in digit_to_segments[seg]:
                    print(f"    Drawing segment: {segment}")
                    draw.polygon(segments[segment], fill='black')
            else:
                print(f"  Warning: No mapping found for segment {seg}")
    else:
        print("Debug - Normal digit mode")
        segments_to_draw = digit_to_segments.get(digit, [])
        print(f"Segments to draw: {segments_to_draw}")
        for segment in segments_to_draw:
            print(f"  Drawing segment: {segment}")
        draw.polygon(segments[segment], fill='black')

def image_to_clipboard(image):
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            global STYLE_CONFIG
            STYLE_CONFIG.update(json.load(f))

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(STYLE_CONFIG, f, indent=4)

class StyleAdjustWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title(LANG_CONFIG[current_lang]['style_title'])
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(False, False)
        
        # 主容器
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['preview_title'], 
                                     padding="10")
        preview_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.grid(row=0, column=0, pady=5)
        
        # 调节控件区域
        controls_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['adjust_options'], 
                                      padding="10")
        controls_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        
        # 分类调节选项
        self.create_adjustment_sections(controls_frame)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        save_btn = ttk.Button(button_frame, 
                            text=LANG_CONFIG[current_lang]['save_btn'], 
                            command=self.save_style, 
                            width=15)
        save_btn.grid(row=0, column=0, padx=10)
        
        reset_btn = ttk.Button(button_frame, 
                             text=LANG_CONFIG[current_lang]['reset_btn'], 
                             command=self.reset_style, 
                             width=15)
        reset_btn.grid(row=0, column=1, padx=10)

        # 语言切换按钮区域 - 放在最底部
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=3, column=0, pady=(5, 0), sticky='e')
        
        self.lang_btn = ttk.Button(lang_frame, 
                                 text='English' if current_lang == 'zh_CN' else '中文',
                                 command=self.switch_language,
                                 style='Language.TButton',
                                 width=8)
        self.lang_btn.grid(row=0, column=0)

        # 初始化预览
        self.update_preview()

    def switch_language(self):
        # 调用全局语言切换
        switch_language()
        # 更新样式窗口的语言
        self.update_window_language()

    def update_window_language(self):
        # 更新窗口标题
        self.window.title(LANG_CONFIG[current_lang]['style_title'])
        
        # 更新预览区域标题
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

        # 重新创建调节选项
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
        # 将调节选项分类
        sections = {
            LANG_CONFIG[current_lang]['char_settings']: [
                (LANG_CONFIG[current_lang]['char_width'], 'seg_width', 10, 30),
                (LANG_CONFIG[current_lang]['char_height'], 'seg_height', 20, 40),
                (LANG_CONFIG[current_lang]['line_thickness'], 'thickness', 2, 6)
            ],
            LANG_CONFIG[current_lang]['grid_settings']: [
                (LANG_CONFIG[current_lang]['grid_width'], 'cell_width', 15, 50),
                (LANG_CONFIG[current_lang]['grid_height'], 'cell_height', 15, 50),
                (LANG_CONFIG[current_lang]['char_spacing'], 'spacing', 8, 25)
            ],
            LANG_CONFIG[current_lang]['dot_settings']: [
                (LANG_CONFIG[current_lang]['dot_size'], 'dot_size', 2, 5),
                (LANG_CONFIG[current_lang]['x_offset'], 'dot_offset_x', -15, 15),
                (LANG_CONFIG[current_lang]['y_offset'], 'dot_offset_y', -5, 5)
            ],
            LANG_CONFIG[current_lang]['square_settings']: [
                (LANG_CONFIG[current_lang]['square_size'], 'square_size', 8, 30),
                (LANG_CONFIG[current_lang]['x_offset'], 'square_offset_x', -15, 15),
                (LANG_CONFIG[current_lang]['y_offset'], 'square_offset_y', -15, 15)
            ]
        }
        
        row = 0
        for section_name, adjustments in sections.items():
            section_frame = ttk.LabelFrame(parent, text=section_name, padding="5")
            section_frame.grid(row=row, column=0, padx=5, pady=5, sticky='ew')
            
            for idx, (label_text, config_key, min_val, max_val) in enumerate(adjustments):
                self.create_adjustment_row(section_frame, idx, label_text, config_key, min_val, max_val)
            
            row += 1

    def create_adjustment_row(self, parent, row, label_text, config_key, min_val, max_val):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, pady=2, sticky='ew')
        
        ttk.Label(frame, text=label_text, width=8).grid(row=0, column=0, padx=5)
        
        scale = ttk.Scale(
            frame,
            from_=min_val,
            to=max_val,
            value=STYLE_CONFIG[config_key],
            orient=tk.HORIZONTAL,
            length=150,
            command=lambda v, key=config_key: self.on_scale_change(v, key)
        )
        scale.grid(row=0, column=1, padx=5)
        
        value_label = ttk.Label(frame, width=3)
        value_label.grid(row=0, column=2, padx=5)
        value_label.configure(text=str(STYLE_CONFIG[config_key]))
        setattr(self, f"{config_key}_label", value_label)

    def on_scale_change(self, value, key):
        value = round(float(value))
        STYLE_CONFIG[key] = value
        getattr(self, f"{key}_label").configure(text=str(value))
        self.update_preview()  # 确保值改变时更新预览

    def update_preview(self):
        # 使用配置中的方格大小
        CELL_WIDTH = STYLE_CONFIG['cell_width']
        CELL_HEIGHT = STYLE_CONFIG['cell_height']
        TOTAL_WIDTH = CELL_WIDTH * 4
        TOTAL_HEIGHT = CELL_HEIGHT
        
        # 创建预览图像
        image = Image.new('RGB', (TOTAL_WIDTH, TOTAL_HEIGHT), 'white')
        draw = ImageDraw.Draw(image)
        
        # 绘制方格边框
        for y in [0, CELL_HEIGHT]:
            draw.line([(0, y), (TOTAL_WIDTH, y)], fill='black', width=1)
        
        for x in range(5):
            x_pos = x * CELL_WIDTH
            if x == 4:
                x_pos = TOTAL_WIDTH - 1
            draw.line([(x_pos, 0), (x_pos, TOTAL_HEIGHT)], 
                     fill='black', width=1)

        # 确保底部边框完整显示
        draw.line([(0, TOTAL_HEIGHT - 1), (TOTAL_WIDTH - 1, TOTAL_HEIGHT - 1)], 
                 fill='black', width=1)

        # 绘制示例字符
        chars = ["1", "2", "3", "4"]  # 使用数字便于观察间距
        for i, char in enumerate(chars):
            # 计算字符在方格中的居中位置，考虑间距
            char_width = STYLE_CONFIG['seg_width']
            char_height = STYLE_CONFIG['seg_height']
            spacing = STYLE_CONFIG['spacing']
            
            # 基础X位置加上间距调整
            base_x = i * CELL_WIDTH
            x = base_x + (CELL_WIDTH - char_width - spacing) // 2 + STYLE_CONFIG['x_start']
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

        # 更新预览显示
        photo = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo

    def save_style(self):
        save_config()
        messagebox.showinfo("成功", "样式配置已保存")

    def reset_style(self):
        global STYLE_CONFIG
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
        self.update_preview()
        for key in STYLE_CONFIG:
            getattr(self, f"{key}_label").configure(text=str(STYLE_CONFIG[key]))

def generate_image():
    try:
        input_text = entry_text.get().upper()
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
    """更新界面语言"""
    # 更新主窗口
    root.title(LANG_CONFIG[current_lang]['title'])
    
    # 更新输入区域
    input_frame.configure(text=LANG_CONFIG[current_lang]['input_group'])
    input_label.configure(text=LANG_CONFIG[current_lang]['input_label'])
    help_label.configure(text=LANG_CONFIG[current_lang]['help_text'])
    
    # 更新主要按钮
    generate_btn.configure(text=LANG_CONFIG[current_lang]['generate_btn'])
    style_btn.configure(text=LANG_CONFIG[current_lang]['style_btn'])
    
    # 更新底部按钮
    import_btn.configure(text=LANG_CONFIG[current_lang]['import_license'])
    show_id_btn.configure(text=LANG_CONFIG[current_lang]['show_hardware_id'])
    lang_btn.configure(text=LANG_CONFIG[current_lang]['lang_switch'])
    
    # 更新预览标签
    preview_frame.configure(text=LANG_CONFIG[current_lang]['preview_label'])

def create_main_window():
    global root, input_frame, input_label, help_label, generate_btn, style_btn, lang_btn, preview_frame
    
    root.title(LANG_CONFIG[current_lang]['title'])
    root.configure(bg='#f0f0f0')
    root.resizable(False, False)
    
    # 主容器
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 输入区域
    input_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['input_group'], padding="10")
    input_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    
    input_label = ttk.Label(input_frame, text=LANG_CONFIG[current_lang]['input_label'])
    input_label.grid(row=0, column=0, padx=5)
    
    global entry_text
    entry_text = ttk.Entry(input_frame, width=15)
    entry_text.grid(row=0, column=1, padx=5)
    
    help_label = ttk.Label(input_frame, text=LANG_CONFIG[current_lang]['help_text'], justify='left')
    help_label.grid(row=1, column=0, columnspan=2, pady=(5,0), sticky='w')
    
    # 功能按钮区域
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, pady=10)
    
    generate_btn = ttk.Button(button_frame, text=LANG_CONFIG[current_lang]['generate_btn'], 
                            command=generate_image)
    generate_btn.grid(row=0, column=0, padx=5)
    
    style_btn = ttk.Button(button_frame, text=LANG_CONFIG[current_lang]['style_btn'], 
                          command=lambda: StyleAdjustWindow(root))
    style_btn.grid(row=0, column=1, padx=5)
    
    # 底部按钮区域
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.grid(row=3, column=0, pady=(5, 0), sticky='e')
    
    # 使用更小巧的按钮样式
    style = ttk.Style()
    style.configure('Bottom.TButton', padding=3)
    
    # 导入授权按钮
    global import_btn
    import_btn = ttk.Button(bottom_frame, 
                         text=LANG_CONFIG[current_lang]['import_license'],
                         command=import_license,
                         style='Bottom.TButton',
                         width=10)
    import_btn.grid(row=0, column=0, padx=2)
    
    # 显示硬件ID按钮
    global show_id_btn
    show_id_btn = ttk.Button(bottom_frame,
                          text=LANG_CONFIG[current_lang]['show_hardware_id'],
                          command=show_hardware_id,
                          style='Bottom.TButton',
                          width=10)
    show_id_btn.grid(row=0, column=1, padx=2)
    
    # 语言切换按钮
    global lang_btn
    lang_btn = ttk.Button(bottom_frame, 
                         text=LANG_CONFIG[current_lang]['lang_switch'],
                         command=switch_language,
                         style='Bottom.TButton',
                         width=8)
    lang_btn.grid(row=0, column=2, padx=2)

    # 预览区域
    preview_frame = ttk.LabelFrame(main_frame, text=LANG_CONFIG[current_lang]['preview_label'], 
                                 padding="10")
    preview_frame.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
    
    global preview_label
    preview_label = ttk.Label(preview_frame)
    preview_label.grid(row=0, column=0, pady=5)
    
    # 创建空白预览图片
    empty_image = Image.new('RGB', (200, 50), 'white')
    preview_image(empty_image)

def import_license():
    """导入授权码"""
    try:
        # 获取剪贴板内容
        license_code = root.clipboard_get().strip()
        if not license_code:
            messagebox.showerror(
                "错误" if current_lang == 'zh_CN' else "Error",
                "请先复制授权码" if current_lang == 'zh_CN' else "Please copy license code first"
            )
            return
        
        # 导入授权
        license_manager = LicenseManager()
        if license_manager.import_license(license_code):
            messagebox.showinfo(
                "成功" if current_lang == 'zh_CN' else "Success",
                "授权导入成功" if current_lang == 'zh_CN' else "License imported successfully"
            )
            # 重新检查过期状态
            check_expiration()
    except Exception as e:
        messagebox.showerror(
            "错误" if current_lang == 'zh_CN' else "Error",
            str(e)
        )

def show_hardware_id():
    """显示硬件ID"""
    hardware_id = get_hardware_id()
    # 创建一个对话框显示硬件ID
    dialog = tk.Toplevel(root)
    dialog.title(LANG_CONFIG[current_lang].get('hardware_id_title', "硬件ID"))
    dialog.geometry("600x200")
    dialog.resizable(False, False)
    
    # 创建主框架
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.grid(row=0, column=0, sticky='nsew')
    
    # 显示硬件ID
    ttk.Label(main_frame, 
             text=LANG_CONFIG[current_lang].get('hardware_id_label', "您的硬件ID是:"),
             font=('Arial', 10)).grid(row=0, column=0, pady=(0,10))
    
    id_text = ttk.Entry(main_frame, width=70)
    id_text.insert(0, hardware_id)
    id_text.configure(state='readonly')
    id_text.grid(row=1, column=0, pady=5)
    
    # 复制按钮
    copy_btn = ttk.Button(main_frame, 
                         text=LANG_CONFIG[current_lang].get('copy_id', "复制ID"),
                         command=lambda: copy_to_clipboard(hardware_id, dialog))
    copy_btn.grid(row=2, column=0, pady=20)

def copy_to_clipboard(text, dialog=None):
    """复制文本到剪贴板"""
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo(
        "成功" if current_lang == 'zh_CN' else "Success",
        "硬件ID已复制到剪贴板" if current_lang == 'zh_CN' else "Hardware ID copied to clipboard"
    )
    if dialog:
        dialog.destroy()

# 程序启动时加载配置
if __name__ == '__main__':
    try:
        if check_expiration():  # 检查是否过期
            root = tk.Tk()
            create_main_window()
            load_config()
            root.mainloop()
        else:
            sys.exit(1)
    except Exception as e:
        messagebox.showerror(
            "错误" if current_lang == 'zh_CN' else "Error",
            f"程序启动失败: {str(e)}" if current_lang == 'zh_CN' else
            f"Failed to start: {str(e)}"
        )
