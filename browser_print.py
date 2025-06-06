from playwright.async_api import async_playwright
from log.log import setup_logger
import asyncio

logger_console = setup_logger("console")
logger_response = setup_logger("response")

async def handle_console_message(msg) -> None:
    """处理网络请求事件（仅适用于 Console 对象）"""
    try:
        if msg.type == "error":
            msg = f"[CONSOLE] {msg.text} @ {msg.location}"
            logger_console.error(msg)
        else:
            logger_console.info(msg)
    except Exception as e:
        logger_console.exception(f"Console处理失败: {e}")

async def handle_response_event(res) -> None:
    """处理网络请求事件（仅适用于 Response 对象）"""
    try:
        if res.status == 200:
            res = f"[REQUEST] {res.status} - {res.request}"
            logger_response.info(res)
        else:
            logger_response.error(res)
    except Exception as e:
        logger_response.exception(f"Response处理失败: {e}")

async def main(browser_path: str=None) -> None:
    async with async_playwright() as p:
        if browser_path is None:
            raise ValueError("必须提供 browser_path 参数")
        else:
            pass
        browser = await p.chromium.launch(headless=False, # 是否要开启藏头模式
                                          executable_path = browser_path,
                                          args=["--start-maximized"])
        # 创建浏览器上下文时禁用 viewport 限制，使用浏览器原生窗口尺寸
        context = await browser.new_context(no_viewport=True)
        context.on("console", handle_console_message)
        context.on("response", handle_response_event)
        page = await context.new_page()
        try:
            await page.goto("https://www.baidu.com",timeout=0)
        except Exception as e:
            print(f"检查网络状态……{e}")
        try:
            while True:
                await asyncio.sleep(1) # 保护性心跳
        except KeyboardInterrupt:
            print("\n=== 监听器已停止 ===")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    # 这里传浏览器的执行文件
    asyncio.run(main("C:\Program Files\Google\Chrome\Application\chrome.exe"))