

# 2025/05/30 v1.0：初始版本

## 支持 PC 和安卓浏览器监听，实现日志按大小分割

## 依赖库：
    pip install playwright                   核心库组件
    pip install pyinstaller                  打包库组件
    python -m playwright install chromium    安装库原生Chromium浏览器

## 项目结构：
    Browser_Print_v1/
    ├── dist/                # 应用打包输出目录
    │   └── exe
    ├── log/
    │   └── log.py           # 自定义日志模块
    ├── src_ADB/
    │   └── shell_ADB.py     # 用来连接 ADB 转发端口
    ├── android_print.py     # 安卓 浏览器 核心逻辑 （集成到其他工具，就从这里调函数）
    ├── android_print_ui.py  # 安卓 浏览器 打包 exe
    ├── browser_print.py     # pc 浏览器 核心逻辑  （集成到其他工具，就从这里调函数）
    ├── browser_print_ui.py  # pc 浏览器 打包 exe
    └── README.md

## 脚本运行前准备：
    安卓：
        1. 连接电脑，并打开USB调试模式
        2. 使用chrome浏览器，或chrome内核非魔改国产浏览器
        3. 打开chrome浏览器
        end
    PC：
        1.使用chrome、edge浏览器，或chrome内核非魔改国产浏览器
        end

## 运行脚本\调用方法：
    安卓：
    android_print.py: 
        
        主入口：
        asyncio.run(AndroidPrint().run())
        
            方法说明：
            adb_forward() # 配置ADB端口转发
            connect_browser() # 连接浏览器
            bind_page_listeners() # 引用消息处理函数
            context_in_page() # 启用异步时间监听
    END

    PC（必须填入浏览器执行文件路径）：
    browser_print.py:
        主入口：
        asyncio.run(main("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"))
    END

    打包：
    pyinstaller --onefile android_print_ui.py

## 其他：
    * pc浏览器 如需更换启动目标网站，请修改 page.goto() 中的 URL。
    * 可以在 handle_console_message() 和 handle_response_event() 中添加更复杂的处理逻辑。
    * 日志容量每达到 10 MB 会自动进行分，储存于脚本/应用程序根目录下
        * maxBytes # 决定分割容量        
        * backupCount # 决定分割次数
