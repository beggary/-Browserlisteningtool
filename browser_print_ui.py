from tkinter import ttk, scrolledtext, filedialog, messagebox
from playwright.async_api import async_playwright
from log.log import setup_logger
import asyncio
import threading
import tkinter as tk

logger_console = setup_logger("console")
logger_response = setup_logger("respologgernse")

class PlaywrightMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("浏览器监听工具")
        self.root.geometry("920x600")
        self.root.minsize(800, 500)

        # 设置主题颜色
        self.bg_color = "#f5f7fa"
        self.primary_color = "#4a89dc"
        self.secondary_color = "#3bafda"
        self.text_color = "#333333"

        # 应用字体设置
        self.title_font = ("SimHei", 14, "bold")
        self.normal_font = ("SimHei", 11)

        # 初始化变量
        self.is_running = False
        self.browser = None
        self.context = None
        self.page = None
        self.async_loop = None
        self.monitor_task = None
        self.executable_path = None

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建顶部控制区域
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制区域", padding="10")
        self.control_frame.pack(fill=tk.X, pady=(0, 10))

        # URL输入
        try:
            ttk.Label(self.control_frame, text="URL:", font=self.normal_font).grid(row=0, column=0, padx=(0, 5),
                                                                                   sticky=tk.W)
            self.url_var = tk.StringVar(value="https://www.baidu.com")
            self.url_entry = ttk.Entry(self.control_frame, textvariable=self.url_var, width=50, font=self.normal_font)
            self.url_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        except Exception as e:
            print(f"检查网络状态……{e}")
        # 启动/停止按钮
        self.start_button = ttk.Button(self.control_frame, text="启动监听", command=self.toggle_monitor,
                                       style='Accent.TButton')
        self.start_button.grid(row=0, column=2, padx=5)

        # 清空日志按钮
        self.clear_button = ttk.Button(self.control_frame, text="清空日志", command=self.clear_logs)
        self.clear_button.grid(row=0, column=3, padx=5)

        # 保存日志按钮
        self.save_button = ttk.Button(self.control_frame, text="保存日志", command=self.save_logs)
        self.save_button.grid(row=0, column=4, padx=5)


        self.browser_var = tk.StringVar(value="chromium")


        # 浏览器可执行文件选择
        ttk.Label(self.control_frame, text="浏览器路径:", font=self.normal_font).grid(row=2, column=0, padx=(0, 5),
                                                                                      pady=(10, 0), sticky=tk.W)

        self.executable_path_var = tk.StringVar(value = "启动前需要选择浏览器，最好是chrome")
        self.executable_path_entry = ttk.Entry(self.control_frame, textvariable=self.executable_path_var, width=50,
                                               font=self.normal_font)
        self.executable_path_entry.grid(row=2, column=1, pady=(10, 0), sticky=tk.W)

        self.browse_button = ttk.Button(self.control_frame, text="浏览路径", command=self.browse_executable)
        self.browse_button.grid(row=2, column=2, pady=(10, 0), padx=5, sticky=tk.W)

        self.browse_button2 = ttk.Button(self.control_frame, text="应用路径", command=self.browser_var_free)
        self.browse_button2.grid(row=2, column=3, pady=(10, 0), padx=5, sticky=tk.W)

        # 创建日志显示区域
        self.log_frame = ttk.LabelFrame(self.main_frame, text="浏览器日志", padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        # 日志文本区域
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, font=self.normal_font, bg="black",
                                                  fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 配置样式
        self.setup_styles()

        # 创建异步循环
        self.create_async_loop()

    def setup_styles(self):
        """配置应用样式"""
        style = ttk.Style()

        # 设置主题
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # 配置按钮样式
        style.configure('Accent.TButton', font=self.normal_font, foreground=self.bg_color)
        style.map('Accent.TButton',
                  background=[('active', self.secondary_color), ('!disabled', self.primary_color)])

        # 配置标签样式
        style.configure('TLabel', font=self.normal_font, foreground=self.text_color)
        style.configure('TLabelframe.Label', font=self.normal_font, foreground=self.text_color)

        # 配置输入框样式
        style.configure('TEntry', font=self.normal_font)

        # 配置滚动条样式
        style.configure('Vertical.TScrollbar', gripcount=0)
        style.configure('Horizontal.TScrollbar', gripcount=0)

    def create_async_loop(self):
        """创建并启动异步事件循环"""
        self.async_loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.loop_thread.start()

    def run_async_loop(self):
        """运行异步事件循环"""
        asyncio.set_event_loop(self.async_loop)
        self.async_loop.run_forever()

    def toggle_monitor(self):
        """切换监听状态"""
        if not self.is_running:
            self.start_monitor()
        else:
            self.stop_monitor()

    def start_monitor(self):
        """开始监听网络请求"""
        if self.is_running:
            return

        url = self.url_var.get().strip()
        if not url:
            self.update_log("错误: 请输入有效的URL")
            return

        self.is_running = True
        self.start_button.config(text="停止监听")
        self.status_var.set("正在监听网络请求...")

        # 在异步循环中运行监控任务
        asyncio.run_coroutine_threadsafe(self.start_monitor_task(url), self.async_loop)

    async def start_monitor_task(self, url):
        """异步启动监控任务"""
        try:
            browser_type = self.browser_var.get()
            headless = False

            self.update_log(f"正在启动 浏览器...")

            async with async_playwright() as p:
                # 获取浏览器类型
                browser_type_obj = getattr(p, browser_type)

                # 启动浏览器，传入可执行文件路径（如果有）
                launch_args = {
                    'headless': headless
                }

                if self.executable_path:
                    launch_args['executable_path'] = self.executable_path
                    self.update_log(f"使用自定义浏览器路径: {self.executable_path}")

                self.browser = await browser_type_obj.launch(**launch_args,args=["--start-maximized"])
                self.context = await self.browser.new_context(no_viewport=True)

                # 设置事件监听器
                self.context.on("console", self.handle_console_message)
                self.context.on("response", self.handle_response_event)

                # 创建新页面
                self.page = await self.context.new_page()

                self.update_log(f"正在导航到: {url}")
                self.update_log("=== 开始监听网络请求 ===")
                await self.page.goto(url,timeout=0)

                # 保持监听状态，直到用户停止
                while self.is_running:
                    await asyncio.sleep(1)
                    # 循环中会导致任务悬挂
                    # await asyncio.Future()
                for task in asyncio.all_tasks():
                    print(task)
        except Exception as e:
            self.update_log(f"错误,检查浏览器路径是否正确: {str(e)}")
        finally:
            # 确保资源被正确关闭
            if self.is_running:
                self.is_running = False
                self.root.after(0, self.reset_ui_state)

    def handle_console_message(self, msg):
        """处理控制台消息"""
        log_msg = f"[CONSOLE] {msg.text} {msg.location}"
        try:
            if msg.type == "error":
                logger_console.error(log_msg)
                self.update_log(log_msg)
            else:
                logger_console.info(log_msg)
        except Exception as e:
            logger_console.info(log_msg)
            self.update_log(f"CONSOLE 处理失败: {e}")

    def handle_response_event(self, res):
        """处理响应事件"""
        log_msg = f"[RESPONSE] {res.status} {res.request}"
        try:
            if res.status == 200:
                logger_response.info(log_msg)
                self.update_log(log_msg)
            else:
                logger_response.error(log_msg)
                self.update_log(log_msg)
        except Exception as e:
            logger_response.exception(log_msg)
            self.update_log(f"RESPONSE 处理失败: {e}")

    def update_log(self, message):
        """更新日志显示"""
        # 在主线程中更新UI
        self.root.after(0, lambda: self._update_log_text(message))

    def _update_log_text(self, message):
        """实际更新日志文本的方法"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def stop_monitor(self):
        """停止监听网络请求"""
        if not self.is_running:
            return

        self.is_running = False
        self.start_button.config(text="启动监听")
        self.status_var.set("正在停止监听...")

        # 清理资源
        asyncio.run_coroutine_threadsafe(self.cleanup_resources(), self.async_loop)

    async def cleanup_resources(self):
        """清理浏览器资源"""
        try:
            if self.context:
                await self.context.close()
                self.context = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            self.update_log("=== 监听器已停止 ===")
        except Exception as e:
            # self.update_log(f"清理资源时出错: {str(e)}")
            self.update_log(f"清理资源: {str(e)}")
        finally:
            self.root.after(0, lambda: self.status_var.set("就绪"))

    def clear_logs(self):
        """清空日志显示"""
        self.log_text.delete(1.0, tk.END)

    def reset_ui_state(self):
        """重置UI状态"""
        self.start_button.config(text="启动监听")
        self.status_var.set("就绪")

    def on_closing(self):
        """处理窗口关闭事件"""
        if self.is_running:
            self.stop_monitor()

        # 给清理操作一些时间
        self.root.after(500, self.root.destroy)

    def browse_executable(self):
        """浏览并选择浏览器可执行文件"""
        file_path = filedialog.askopenfilename(
            title="选择浏览器可执行文件",
            filetypes=[
                ("可执行文件", "*.exe"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.executable_path = file_path
            self.executable_path_var.set(file_path)
            self.update_log(f"已选择浏览器路径: {file_path}")

    def browser_var_free(self):
        self.executable_path = self.executable_path_var.get()
        self.update_log(f"已选择浏览器路径: {self.executable_path}")

    def save_logs(self):
        """保存日志到文件"""
        if not self.log_text.get(1.0, tk.END).strip():
            messagebox.showinfo("提示", "没有日志内容可保存")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if filename:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"日志已保存到 {filename}")
                self.update_log(f"日志已保存到 {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存日志时出错: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlaywrightMonitorApp(root)

    # 设置窗口关闭处理
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()