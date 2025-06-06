from playwright.async_api import async_playwright
from src_ADB.shell_ADB import adb_forward
from log.log import setup_logger
import asyncio

logger_console = setup_logger("console")
logger_response = setup_logger("response")
logger = setup_logger("system")

class AndroidPrint:
    def __init__(self,_connect_over_cdp: str = "http://localhost:9222"):
        self.connect_alive = None
        self.connect_over_cdp = _connect_over_cdp
        self.playwright = None

    async def connect_browser(self):
            while True:
                try:
                    self.connect_alive = await self.playwright.chromium.connect_over_cdp(self.connect_over_cdp)
                    print("连接成功，监听中...")
                    break
                except Exception as e:
                    print(f"连接浏览器失败……3秒后将再次尝试连接{e}")
                    logger.exception(f"连接浏览器失败……3秒后将再次尝试连接{e}")
                    await asyncio.sleep(3)

    async def handle_console_message(self,msg) -> None:
        """处理网络请求事件（仅适用于 Console 对象）"""
        try:
            if msg.type == "error":
                msg = f"[CONSOLE] {msg.text} @ {msg.location}"
                logger_console.error(msg)
            else:
                logger_console.info(msg)
            print(msg)
        except Exception as e:
            logger_console.exception(e)
            print(f"CONSOLE处理失败: {e}")

    async def handle_response_event(self,res) -> None:
        """处理网络请求事件（仅适用于 Response 对象）"""
        try:
            if res.status == 200:
                res = f"[REQUEST] {res.status} - {res.request}"
                logger_response.info(res)
            else:
                logger_response.error(res)
            print(res)
        except Exception as e:
            logger_response.exception(e)
            print(f"CONSOLE处理失败: {e}")

    async def bind_page_listeners(self,page) -> None:
        """绑定单个页面的事件"""
        page.on("console", self.handle_console_message)
        page.on("response", self.handle_response_event)

    async def context_in_page(self,):
        for context in self.connect_alive.contexts:
            for page in context.pages:
                await self.bind_page_listeners(page)
            context.on("page", self.bind_page_listeners)

    async def run(self):
        if adb_forward() is True:
            print("端口转发成功！")
            logger.info("端口转发成功！")
        else:
            raise Exception("端口转发失败……！")
        async with async_playwright() as self.playwright:
            try:
                await self.connect_browser()
                await self.context_in_page()
                try:
                    while True:
                         await asyncio.sleep(1)# 保持运行
                         if not self.connect_alive.contexts:
                             await self.connect_alive.close() # 关闭实例
                             try:
                                 await self.connect_browser()
                                 await self.context_in_page()
                             except Exception as e:
                                 print(f"连接浏览器失败……3秒后将再次尝试连接{e}")
                                 logger.exception(f"连接浏览器失败……3秒后将再次尝试连接{e}")
                                 await asyncio.sleep(3)
                         else:
                             pass
                except KeyboardInterrupt:
                    # print("结束监听")
                    logger.info("结束监听")
                finally:
                    await self.connect_alive.close()
            except Exception as e:
                print(f"连接浏览器1失败……3秒后将再次尝试连接{e}")
                logger.info(f"连接浏览器1失败……3秒后将再次尝试连接{e}")

if __name__ == "__main__":
    asyncio.run(AndroidPrint().run())
