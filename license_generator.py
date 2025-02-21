import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import hashlib
import json
import base64
from cryptography.fernet import Fernet
import winreg
import re

class LicenseGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("授权工具")
        self.root.geometry("500x400")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 硬件ID输入区域
        id_frame = ttk.Frame(main_frame)
        id_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(id_frame, text="硬件ID:").grid(row=0, column=0, sticky=tk.W)
        self.hardware_id = ttk.Entry(id_frame, width=50)
        self.hardware_id.grid(row=0, column=1, padx=5)
        
        # 从剪贴板获取ID按钮
        ttk.Button(id_frame, text="从剪贴板获取", 
                  command=self.paste_hardware_id).grid(row=0, column=2, padx=5)
        
        # 授权时长选择
        ttk.Label(main_frame, text="授权时长:").grid(row=1, column=0, sticky=tk.W)
        duration_frame = ttk.Frame(main_frame)
        duration_frame.grid(row=1, column=1, sticky=tk.W)
        
        self.duration = tk.StringVar(value="180")
        self.duration_entry = ttk.Entry(duration_frame, width=10, textvariable=self.duration)
        self.duration_entry.grid(row=0, column=0, padx=5)
        
        ttk.Label(duration_frame, text="天").grid(row=0, column=1)
        
        # 快速选择按钮
        quick_select = ttk.Frame(main_frame)
        quick_select.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Button(quick_select, text="半年", 
                  command=lambda: self.duration.set("180")).grid(row=0, column=0, padx=2)
        ttk.Button(quick_select, text="一年", 
                  command=lambda: self.duration.set("365")).grid(row=0, column=1, padx=2)
        ttk.Button(quick_select, text="永久", 
                  command=lambda: self.duration.set("3650")).grid(row=0, column=2, padx=2)
        
        # 生成授权码按钮
        ttk.Button(main_frame, text="生成授权码", 
                  command=self.generate_license).grid(row=3, column=0, columnspan=2, pady=20)
        
        # 授权码显示
        ttk.Label(main_frame, text="授权码:").grid(row=4, column=0, sticky=tk.W)
        self.license_text = tk.Text(main_frame, height=8, width=50)
        self.license_text.grid(row=4, column=1, padx=5, pady=5)
        
        # 复制按钮
        ttk.Button(main_frame, text="复制授权码", 
                  command=self.copy_license).grid(row=5, column=0, columnspan=2, pady=10)

    def paste_hardware_id(self):
        """从剪贴板获取硬件ID"""
        try:
            clipboard_text = self.root.clipboard_get().strip()
            # 查找硬件ID格式的文本
            match = re.search(r'Hardware ID: ([a-fA-F0-9]{64})', clipboard_text)
            if match:
                hardware_id = match.group(1)
                self.hardware_id.delete(0, tk.END)
                self.hardware_id.insert(0, hardware_id)
                messagebox.showinfo("成功", "已获取硬件ID")
            else:
                messagebox.showerror("错误", "剪贴板中未找到有效的硬件ID")
        except Exception as e:
            messagebox.showerror("错误", f"获取硬件ID失败: {str(e)}")

    def generate_license(self):
        try:
            hardware_id = self.hardware_id.get().strip()
            if not hardware_id:
                messagebox.showerror("错误", "请输入硬件ID")
                return
            
            days = int(self.duration.get())
            if days <= 0:
                messagebox.showerror("错误", "授权时长必须大于0")
                return
            
            # 生成授权数据
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=days)
            license_data = {
                "hardware_id": hardware_id,
                "expiration_date": expiration_date.isoformat(),
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # 使用硬件ID生成密钥
            key = base64.urlsafe_b64encode(hashlib.sha256(hardware_id.encode()).digest())
            cipher_suite = Fernet(key)
            
            # 加密授权数据
            encrypted_data = cipher_suite.encrypt(json.dumps(license_data).encode())
            license_code = base64.b64encode(encrypted_data).decode()
            
            # 显示授权码
            self.license_text.delete(1.0, tk.END)
            self.license_text.insert(tk.END, license_code)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成授权码失败: {str(e)}")

    def copy_license(self):
        license_code = self.license_text.get(1.0, tk.END).strip()
        if license_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(license_code)
            messagebox.showinfo("成功", "授权码已复制到剪贴板")
        else:
            messagebox.showwarning("提示", "请先生成授权码")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LicenseGenerator()
    app.run() 