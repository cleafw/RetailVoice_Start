"""
浏览器控制工具类 - 增强版（修复版）
修复内容：
1. 修复树莓派上chromium/firefox命令检测与实际使用不一致的问题
2. 在_is_browser_available中找到真实可用命令后，更新到supported_browsers中
"""
import subprocess
import platform
import webbrowser
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from SysManger.debugOut import log


@dataclass
class OpenedWebpage:
    """已打开的网页信息"""
    url: str
    browser: str
    pid: Optional[int]
    opened_at: float
    index: int

# 浏览器控制工具类 - 增强版
class BrowserTool:
    """
    浏览器控制工具类 - 增强版（修复版）

    修复内容：
        - 解决了检测到chromium-browser但使用chromium命令导致失败的问题
        - 现在会自动使用检测到的真实可用命令
    """

    def __init__(self):
        """初始化浏览器工具"""
        # 检测当前操作系统
        self.system = platform.system()  # 'Windows', 'Linux', 'Darwin'(macOS)

        # 已打开的网页列表
        self.opened_webpages: List[OpenedWebpage] = []
        self._webpage_counter = 0

        # 根据操作系统配置浏览器
        self._setup_browsers()

        log.info(f"[浏览器控制] 检测到操作系统: {self.system}")
        log.info(f"[浏览器控制] 支持的浏览器: {list(self.supported_browsers.keys())}")

    # 检测是否运行在树莓派上
    def _is_raspberry_pi(self) -> bool:
        """检测是否运行在树莓派上"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
        except:
            return False

    # 根据系统配置浏览器
    def _setup_browsers(self):
        """根据系统配置浏览器"""
        if self.system == 'Windows':
            self.supported_browsers = {
                'edge': 'msedge',
                'chrome': 'chrome',
                'firefox': 'firefox',
                'chromium': 'chromium'
            }
            self.browser_priority = ['edge', 'chrome', 'firefox', 'chromium']

        elif self.system == 'Linux':
            # 检测是否是树莓派
            is_raspberry_pi = self._is_raspberry_pi()

            if is_raspberry_pi:
                log.info("[浏览器控制] 检测到树莓派系统")
                # 初始配置（会在检测时被真实命令替换）
                self.supported_browsers = {
                    'chromium': 'chromium',
                    'firefox': 'firefox'
                }
                self.browser_priority = ['chromium', 'firefox']
            else:
                # 标准 Linux 配置
                self.supported_browsers = {
                    'firefox': 'firefox',
                    'chrome': 'google-chrome',
                    'chromium': 'chromium'
                }
                self.browser_priority = ['firefox', 'chrome', 'chromium']

        elif self.system == 'Darwin':  # macOS
            self.supported_browsers = {
                'safari': 'safari',
                'chrome': 'google chrome',
                'firefox': 'firefox'
            }
            self.browser_priority = ['safari', 'chrome', 'firefox']
        else:
            self.supported_browsers = {}
            self.browser_priority = []

    # 自动检测系统中可用的最佳浏览器
    def _detect_best_browser(self) -> Optional[str]:
        """
        自动检测系统中可用的最佳浏览器

        返回按优先级找到的第一个可用浏览器

        Returns:
            str: 浏览器名称，如果都不可用则返回 None
        """
        log.info("[浏览器控制] 开始检测可用浏览器...")

        for browser_name in self.browser_priority:
            browser_cmd = self.supported_browsers.get(browser_name)
            if not browser_cmd:
                continue

            # 检查浏览器是否可用（会自动更新真实命令）
            if self._is_browser_available(browser_name, browser_cmd):
                log.info(f"[浏览器控制] ✅ 检测到可用浏览器: {browser_name}")
                return browser_name

        log.warning("[浏览器控制] ⚠️ 未检测到任何配置的浏览器，将使用系统默认")
        return None

    # ============ 核心修复点 ============
    def _is_browser_available(self, browser_name: str, browser_cmd: str) -> bool:
        """
        检查指定浏览器是否可用

        【关键修复】找到真实可用命令后，更新到 supported_browsers 中
        """
        try:
            if self.system == 'Windows':
                result = subprocess.run(
                    ['where', browser_cmd],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0

            elif self.system in ['Linux', 'Darwin']:
                # 尝试多个可能的命令
                possible_commands = [browser_cmd]

                # 为特定浏览器添加备选命令
                if browser_name == 'firefox':
                    possible_commands.extend(['firefox-esr', 'firefox'])
                elif browser_name == 'chromium':
                    possible_commands.extend(['chromium-browser', 'chromium'])

                # 逐个尝试
                for cmd in possible_commands:
                    result = subprocess.run(
                        ['which', cmd],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        log.debug(f"[浏览器控制] 找到可用命令: {cmd}")
                        # ========== 关键修复 ==========
                        # 更新 supported_browsers，使用真实找到的命令
                        if cmd != browser_cmd:
                            log.info(f"[浏览器控制] 更新 {browser_name} 的命令: {browser_cmd} -> {cmd}")
                            self.supported_browsers[browser_name] = cmd
                        # ==============================
                        return True

                return False

        except Exception as e:
            log.debug(f"[浏览器控制] 检测 {browser_name} 失败: {str(e)}")
            return False

        return False
    # ====================================

    # 在浏览器中打开指定网页 - 增强版
    def open_webpage(self, url: str, browser: Optional[str] = None) -> Dict[str, any]:
        """
        在浏览器中打开指定网页 - 增强版

        功能说明：
            - 支持 Windows、Linux、macOS
            - browser=None 时自动选择系统最佳浏览器
            - 自动补全 URL 协议（http://、https://）
            - 跟踪所有已打开的网页
            - 优雅降级：如果指定浏览器不可用，使用系统默认浏览器

        Args:
            url: 要打开的网页地址
                示例: "www.bilibili.com" 或 "https://www.youtube.com"
            browser: 浏览器类型，可选值：
                - None (默认，自动选择最佳浏览器)
                - "firefox"
                - "chrome"
                - "chromium"
                - "edge" (Microsoft Edge，仅 Windows)
                - "safari" (Safari，仅 macOS)

        Returns:
            dict: 包含执行结果的字典
                {
                    "success": True/False,
                    "message": "执行结果消息",
                    "browser_used": "浏览器名称",
                    "system": "操作系统",
                    "webpage_index": int  # 新增：网页索引，用于后续关闭
                }

        示例：
             tool = BrowserTool()
             # 自动选择浏览器
             result = tool.open_webpage("www.bilibili.com")
             print(result)
            {'success': True, 'browser_used': 'edge', 'webpage_index': 0}

             # 指定浏览器
             result = tool.open_webpage("www.youtube.com", browser="chrome")
        """
        log.info(f"[浏览器控制] 请求打开网页: {url} (浏览器: {browser}, 系统: {self.system})")

        # -------------------------------------------------------------------------
        # Step 1: URL 格式验证和标准化
        # -------------------------------------------------------------------------
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            log.debug(f"[浏览器控制] URL 已标准化为: {url}")

        # -------------------------------------------------------------------------
        # Step 2: 确定要使用的浏览器
        # -------------------------------------------------------------------------
        if browser is None:
            # 自动检测最佳浏览器
            browser = self._detect_best_browser()
            log.info(f"[浏览器控制] 自动选择浏览器: {browser}")

        # -------------------------------------------------------------------------
        # Step 3: 尝试使用指定浏览器打开
        # -------------------------------------------------------------------------
        browser_cmd = self.supported_browsers.get(browser.lower()) if browser else None
        pid = None

        if browser_cmd:
            try:
                if self.system == 'Windows':
                    result = self._open_on_windows(url, browser_cmd, browser)
                elif self.system == 'Linux':
                    result = self._open_on_linux(url, browser_cmd, browser)
                elif self.system == 'Darwin':
                    result = self._open_on_macos(url, browser_cmd, browser)
                else:
                    result = None

                if result and result['success']:
                    # 记录已打开的网页
                    webpage_index = self._add_opened_webpage(
                        url=url,
                        browser=result['browser_used'],
                        pid=result.get('pid')
                    )
                    result['webpage_index'] = webpage_index
                    return result

            except Exception as e:
                log.warning(f"[浏览器控制] 使用 {browser} 打开失败: {str(e)}")

        # -------------------------------------------------------------------------
        # Step 4: 降级到系统默认浏览器
        # -------------------------------------------------------------------------
        log.info(f"[浏览器控制] 尝试使用系统默认浏览器打开")

        try:
            # 方法 1: 使用 Python 的 webbrowser 模块（跨平台）
            webbrowser.open(url)
            log.info(f"[浏览器控制] ✅ 已使用系统默认浏览器打开: {url}")

            # 记录已打开的网页
            webpage_index = self._add_opened_webpage(
                url=url,
                browser="default",
                pid=None
            )

            return {
                "success": True,
                "message": f"✅ 已在默认浏览器中打开: {url}",
                "browser_used": "default",
                "system": self.system,
                "webpage_index": webpage_index
            }

        except Exception as e1:
            log.warning(f"[浏览器控制] webbrowser 模块失败: {str(e1)}")

            # 方法 2: 使用系统命令
            try:
                if self.system == 'Windows':
                    subprocess.Popen(['cmd', '/c', 'start', url],
                                   shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                elif self.system == 'Linux':
                    subprocess.Popen(['xdg-open', url],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL,
                                   start_new_session=True)
                elif self.system == 'Darwin':
                    subprocess.Popen(['open', url],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                else:
                    raise Exception(f"不支持的操作系统: {self.system}")

                log.info(f"[浏览器控制] ✅ 已使用系统命令打开: {url}")

                # 记录已打开的网页
                webpage_index = self._add_opened_webpage(
                    url=url,
                    browser="default",
                    pid=None
                )

                return {
                    "success": True,
                    "message": f"✅ 已在默认浏览器中打开: {url}",
                    "browser_used": "default",
                    "system": self.system,
                    "webpage_index": webpage_index
                }

            except Exception as e2:
                error_msg = f"打开网页失败: {str(e2)}"
                log.error(f"[浏览器控制] ❌ {error_msg}")
                return {
                    "success": False,
                    "message": f"❌ {error_msg}",
                    "browser_used": None,
                    "system": self.system
                }

    # 在 Windows 上打开浏览器
    def _open_on_windows(self, url: str, browser_cmd: str, browser_name: str) -> Dict[str, any]:
        """在 Windows 上打开浏览器"""
        try:
            process = subprocess.Popen(
                [browser_cmd, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log.info(f"[浏览器控制] ✅ 已在 {browser_name} 浏览器中打开: {url}")
            return {
                "success": True,
                "message": f"✅ 已在 {browser_name} 浏览器中打开: {url}",
                "browser_used": browser_name,
                "system": "Windows",
                "pid": process.pid
            }
        except Exception as e:
            log.error(f"[浏览器控制] ❌ 打开失败: {str(e)}")
            return {"success": False}

    def _open_on_linux(self, url: str, browser_cmd: str, browser_name: str):
        """在 Linux 上打开浏览器 - 树莓派优化版"""
        import os
        import subprocess
        import time

        try:
            # 设置环境变量 (关键!)
            env = os.environ.copy()
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'
                log.info(f"[浏览器控制] 设置 DISPLAY=:0")

            # 启动浏览器（使用更新后的真实命令）
            log.info(f"[浏览器控制] 执行命令: {browser_cmd} {url}")
            process = subprocess.Popen(
                [browser_cmd, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env=env  # 使用包含 DISPLAY 的环境变量
            )

            # 等待确保进程启动
            time.sleep(0.5)

            # 检查进程是否还在运行
            if process.poll() is None:
                log.info(f"[浏览器控制] ✅ 成功打开 {browser_name}: {url}")
                return {
                    "success": True,
                    "message": f"✅ 已在 {browser_name} 浏览器中打开: {url}",
                    "browser_used": browser_name,
                    "system": "Linux",
                    "pid": process.pid
                }
            else:
                log.error(f"[浏览器控制] ❌ 浏览器进程立即退出")
                return {"success": False}

        except Exception as e:
            log.error(f"[浏览器控制] ❌ 打开失败: {str(e)}")
            return {"success": False}

    # 在 macOS 上打开浏览器
    def _open_on_macos(self, url: str, browser_cmd: str, browser_name: str) -> Dict[str, any]:
        """在 macOS 上打开浏览器"""
        try:
            process = subprocess.Popen(
                ['open', '-a', browser_cmd, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            log.info(f"[浏览器控制] ✅ 已在 {browser_name} 浏览器中打开: {url}")
            return {
                "success": True,
                "message": f"✅ 已在 {browser_name} 浏览器中打开: {url}",
                "browser_used": browser_name,
                "system": "Darwin",
                "pid": process.pid
            }

        except Exception as e:
            log.error(f"[浏览器控制] ❌ 打开失败: {str(e)}")
            return {"success": False}

    # 添加已打开的网页到列表
    def _add_opened_webpage(self, url: str, browser: str, pid: Optional[int]) -> int:
        """添加已打开的网页到列表"""
        webpage = OpenedWebpage(
            url=url,
            browser=browser,
            pid=pid,
            opened_at=time.time(),
            index=self._webpage_counter
        )
        self.opened_webpages.append(webpage)
        self._webpage_counter += 1

        log.info(f"[浏览器控制] 已记录网页 #{webpage.index}: {url} ({browser})")

        return webpage.index

    # 列出所有已打开的网页
    def list_opened_webpages(self) -> List[Dict]:
        """
        列出所有已打开的网页

        Returns:
            list: 已打开的网页列表
        """
        result = []
        for wp in self.opened_webpages:
            opened_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(wp.opened_at))
            result.append({
                "index": wp.index,
                "url": wp.url,
                "browser": wp.browser,
                "opened_at": opened_time,
                "pid": wp.pid
            })
        return result

    # 关闭指定网页
    def close_webpage(self, index: Optional[int] = None, url: Optional[str] = None) -> Dict[str, any]:
        """
        关闭指定的网页

        可以通过网页索引或URL来关闭已打开的网页。

        Args:
            index: 网页索引（从0开始）
            url: 网页地址（精确匹配）

        Returns:
            dict: 执行结果
        """
        if index is None and url is None:
            return {
                "success": False,
                "message": "❌ 必须提供 index 或 url 参数"
            }

        # 查找要关闭的网页
        webpage_to_close = None

        if index is not None:
            # 通过索引查找
            for wp in self.opened_webpages:
                if wp.index == index:
                    webpage_to_close = wp
                    break
        elif url is not None:
            # 通过URL查找
            for wp in self.opened_webpages:
                if wp.url == url:
                    webpage_to_close = wp
                    break

        if not webpage_to_close:
            search_by = f"索引 {index}" if index is not None else f"URL {url}"
            return {
                "success": False,
                "message": f"❌ 未找到 {search_by} 对应的网页"
            }

        # 尝试关闭浏览器（只有非default浏览器才能关闭）
        browser_close_msg = ""
        browser_closed = False

        if webpage_to_close.browser != "default":
            result = self.close_browser(webpage_to_close.browser)
            browser_closed = result.get('success', False)
            if not browser_closed:
                browser_close_msg = f"\n⚠️ 浏览器关闭失败: {result.get('message', '未知错误')}"
        else:
            # default 浏览器无法程序化关闭
            browser_close_msg = "\n⚠️ 系统默认浏览器无法自动关闭，请手动关闭浏览器窗口"
            log.warning(f"[浏览器控制] 系统默认浏览器无法自动关闭")

        # 从列表中移除
        self.opened_webpages.remove(webpage_to_close)

        log.info(f"[浏览器控制] 已从列表移除网页 #{webpage_to_close.index}: {webpage_to_close.url}")

        return {
            "success": True,
            "message": f"✅ 已从跟踪列表中移除网页: {webpage_to_close.url}{browser_close_msg}",
            "closed_index": webpage_to_close.index,
            "browser_closed": browser_closed
        }

    # 关闭所有已打开的网页
    def close_all_webpages(self) -> Dict[str, any]:
        """
        关闭所有已打开的网页

        Returns:
            dict: 执行结果
        """
        if not self.opened_webpages:
            return {
                "success": True,
                "message": "ℹ️ 没有已打开的网页",
                "closed_count": 0
            }

        closed_count = len(self.opened_webpages)
        browsers_to_close = set(wp.browser for wp in self.opened_webpages)

        has_default_browser = "default" in browsers_to_close
        browsers_closed = 0
        browsers_failed = 0

        # 关闭所有涉及的浏览器（排除default）
        for browser in browsers_to_close:
            if browser != "default":
                result = self.close_browser(browser)
                if result.get('success'):
                    browsers_closed += 1
                else:
                    browsers_failed += 1

        # 清空列表
        self.opened_webpages.clear()

        log.info(f"[浏览器控制] 已清空所有网页跟踪记录，共 {closed_count} 个")

        # 构建消息
        msg_parts = [f"✅ 已从跟踪列表中移除 {closed_count} 个网页"]

        if browsers_closed > 0:
            msg_parts.append(f"已关闭 {browsers_closed} 个浏览器")

        if has_default_browser:
            msg_parts.append("⚠️ 系统默认浏览器无法自动关闭,请手动关闭浏览器窗口")

        if browsers_failed > 0:
            msg_parts.append(f"⚠️ {browsers_failed} 个浏览器关闭失败")

        return {
            "success": True,
            "message": "\n".join(msg_parts),
            "closed_count": closed_count,
            "browsers_closed": browsers_closed,
            "has_default_browser": has_default_browser
        }

    # 关闭指定浏览器的所有实例 - 跨平台版本
    def close_browser(self, browser: str = 'firefox') -> Dict[str, any]:
        """
        关闭指定浏览器的所有实例 - 跨平台版本

        Args:
            browser: 浏览器类型

        Returns:
            dict: 包含执行结果的字典

        注意：
            - 这会关闭该浏览器的所有窗口和标签页
        """
        log.info(f"[浏览器控制] 请求关闭浏览器: {browser} (系统: {self.system})")

        try:
            browser_process = self.supported_browsers.get(browser.lower())

            if not browser_process:
                error_msg = (
                    f"不支持的浏览器: {browser}。"
                    f"支持的浏览器: {', '.join(self.supported_browsers.keys())}"
                )
                log.warning(f"[浏览器控制] {error_msg}")
                return {
                    "success": False,
                    "message": f"❌ {error_msg}"
                }

            # 根据操作系统使用不同的命令
            if self.system == 'Windows':
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', f'{browser_process}.exe'],
                    check=False,
                    capture_output=True,
                    text=True
                )
                success = result.returncode == 0

            elif self.system == 'Linux':
                result = subprocess.run(
                    ['pkill', '-f', browser_process],
                    check=False,
                    capture_output=True,
                    text=True
                )
                success = result.returncode in [0, 1]

            elif self.system == 'Darwin':
                result = subprocess.run(
                    ['pkill', '-f', browser_process],
                    check=False,
                    capture_output=True,
                    text=True
                )
                success = result.returncode in [0, 1]
            else:
                raise Exception(f"不支持的操作系统: {self.system}")

            if success:
                log.info(f"[浏览器控制] ✅ 已关闭浏览器: {browser}")
                return {
                    "success": True,
                    "message": f"✅ 已关闭 {browser} 浏览器"
                }
            else:
                error_msg = f"关闭浏览器时出错: {result.stderr}"
                log.error(f"[浏览器控制] ❌ {error_msg}")
                return {
                    "success": False,
                    "message": f"❌ {error_msg}"
                }

        except FileNotFoundError as e:
            error_msg = f"系统中未找到关闭浏览器所需的命令: {str(e)}"
            log.error(f"[浏览器控制] ❌ {error_msg}")
            return {
                "success": False,
                "message": f"❌ {error_msg}"
            }

        except Exception as e:
            error_msg = f"关闭浏览器失败: {str(e)}"
            log.error(f"[浏览器控制] ❌ {error_msg}")
            return {
                "success": False,
                "message": f"❌ {error_msg}"
            }

    # 获取当前系统支持的浏览器列表
    def get_supported_browsers(self) -> Dict[str, str]:
        """获取当前系统支持的浏览器列表"""
        return self.supported_browsers.copy()

    # 获取系统信息
    def get_system_info(self) -> Dict[str, any]:
        """
        获取系统信息

        Returns:
            dict: 系统信息
        """
        return {
            "system": self.system,
            "supported_browsers": list(self.supported_browsers.keys()),
            "browser_priority": self.browser_priority,
            "opened_webpages_count": len(self.opened_webpages)
        }

    # ============ 便捷方法 ============

    def search_web(self, query: str, engine: str = "google", browser: Optional[str] = None) -> Dict[str, any]:
        """在浏览器中搜索"""
        search_urls = {
            "google": f"https://www.google.com/search?q={query}",
            "baidu": f"https://www.baidu.com/s?wd={query}"
        }

        search_url = search_urls.get(engine.lower())
        if not search_url:
            return {
                "success": False,
                "message": f"不支持的搜索引擎: {engine}"
            }

        result = self.open_webpage(search_url, browser)
        if result['success']:
            result['search_url'] = search_url
        return result

    def open_youtube(self, search_query: Optional[str] = None, browser: Optional[str] = None) -> Dict[str, any]:
        """打开YouTube"""
        if search_query:
            url = f"https://www.youtube.com/results?search_query={search_query}"
        else:
            url = "https://www.youtube.com"
        return self.open_webpage(url, browser)

    def open_bilibili(self, search_query: Optional[str] = None, browser: Optional[str] = None) -> Dict[str, any]:
        """打开Bilibili"""
        if search_query:
            url = f"https://search.bilibili.com/all?keyword={search_query}"
        else:
            url = "https://www.bilibili.com"
        return self.open_webpage(url, browser)

    def open_multiple_webpages(self, urls: List[str], browser: Optional[str] = None) -> Dict[str, any]:
        """批量打开多个网页"""
        results = []
        indices = []

        for url in urls:
            result = self.open_webpage(url, browser)
            results.append(result)
            if result['success']:
                indices.append(result['webpage_index'])

        opened_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - opened_count

        return {
            "success": opened_count > 0,
            "message": f"成功打开 {opened_count} 个，失败 {failed_count} 个",
            "opened_count": opened_count,
            "failed_count": failed_count,
            "results": results,
            "indices": indices
        }

    def get_webpage_count(self) -> Dict[str, any]:
        """获取已打开的网页数量"""
        count = len(self.opened_webpages)
        return {
            "count": count,
            "message": f"当前已打开 {count} 个网页"
        }

    def close_latest_webpage(self) -> Dict[str, any]:
        """关闭最近打开的网页"""
        if not self.opened_webpages:
            return {
                "success": False,
                "message": "没有已打开的网页"
            }

        latest = max(self.opened_webpages, key=lambda wp: wp.index)
        return self.close_webpage(index=latest.index)

    def close_oldest_webpage(self) -> Dict[str, any]:
        """关闭最早打开的网页"""
        if not self.opened_webpages:
            return {
                "success": False,
                "message": "没有已打开的网页"
            }

        oldest = min(self.opened_webpages, key=lambda wp: wp.index)
        return self.close_webpage(index=oldest.index)


