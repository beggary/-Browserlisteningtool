from tkinter import scrolledtext
from playwright.async_api import async_playwright
from src_ADB.shell_ADB import adb_forward
from log.log import setup_logger
import asyncio
import threading
import tkinter as tk

logger_console = setup_logger("console")
logger_response = setup_logger("response")
logger = setup_logger("system")

class BrowserMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("android 浏览器监听工具")
        self.running = False

        # 自适应的日志展示区
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(root, text="开始监听", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=10,pady=10,)

        self.stop_button = tk.Button(root, text="停止监听", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10,pady=10,)

    def console_e_log(self, msg):
        self.text_area.insert(tk.END, msg + '\n')
        self.text_area.see(tk.END)
        logger_console.error(msg)

    def console_i_log(self, msg):
        self.text_area.insert(tk.END, msg + '\n')
        self.text_area.see(tk.END)
        logger_console.info(msg)

    def response_i_log(self, msg):
        self.text_area.insert(tk.END, msg + '\n')
        self.text_area.see(tk.END)
        logger_response.info(msg)

    def response_e_log(self, msg):
        self.text_area.insert(tk.END, msg + '\n')
        self.text_area.see(tk.END)
        logger_response.error(msg)


    def t_log(self, msg):
        self.text_area.insert(tk.END, msg + '\n')
        self.text_area.see(tk.END)
        logger.exception(msg)

    def start_monitoring(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.run_async_loop, daemon=True).start()

    def stop_monitoring(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_async_loop(self):
        asyncio.run(self.monitor_browser())

    async def handle_console_message(self, msg):
        try:
            if msg.type == "error":
                text = f"[CONSOLE] {msg.text} @ {msg.location}"
                self.root.after(0, self.console_e_log, text)
            else:
                self.root.after(0, self.console_i_log, msg.text)
        except Exception as e:
            self.root.after(0, self.t_log, f"CONSOLE处理失败: {e}")

    async def handle_response_event(self, res):
        try:
            if res.status == 200:
                text = f"[REQUEST] {res.status} - {res.request}"
                self.root.after(0, self.response_e_log, text)
            else:
                self.root.after(0, self.response_i_log, str(res))
        except Exception as e:
            self.root.after(0, self.response_i_log, f"RESPONSE处理失败: {e}")

    async def bind_page_listeners(self, page):
        page.on("console", self.handle_console_message)
        page.on("response", self.handle_response_event)

    async def monitor_browser(self):
        if not adb_forward():
            self.root.after(0, self.t_log, "端口转发失败……确认USB调试状态是否开启……")
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return
        self.root.after(0, self.t_log, "端口转发成功！")

        async with async_playwright() as p:
            browser = None
            while self.running:
                try:
                    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                    self.root.after(0, self.t_log, "连接成功，监听中...")
                    break
                except Exception as e:
                    self.root.after(0, self.t_log, f"浏览器连接失败，确认chrome浏览器开启，3秒后重试：{e}")
                    await asyncio.sleep(3)
            if not browser:
                return
            for context in browser.contexts:
                for page in context.pages:
                    await self.bind_page_listeners(page)
                context.on("page", self.bind_page_listeners)
            try:
                while self.running:
                    await asyncio.sleep(1)
                    if not browser.contexts:
                        await browser.close()
                        browser = None
                        while self.running and browser is None:
                            try:
                                browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                                self.root.after(0, self.t_log, "重新连接成功，监听中...")
                                for context in browser.contexts:
                                    for page in context.pages:
                                        await self.bind_page_listeners(page)
                                    context.on("page", self.bind_page_listeners)
                            except Exception as e:
                                self.root.after(0, self.t_log, f"重连浏览器失败，3秒后重试：{e}")
                                await asyncio.sleep(3)
                    else:
                        pass
            except Exception as e:
                self.root.after(0, self.t_log, f"监听中断：{e}")
            finally:
                if browser:
                    await browser.close()
                self.root.after(0, self.t_log, "监听结束")
                self.stop_monitoring()

if __name__ == "__main__":
    root = tk.Tk()
    app = BrowserMonitorApp(root)
    root.mainloop()
