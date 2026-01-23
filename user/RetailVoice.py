



'''语音识别系统'''
from globalData.GObj import GObj


# 打开 SenseCraft Voice 语音识别系统
def open_sensecraft_voice(browser: str = None) -> dict:
    """
    打开 SenseCraft Voice 语音识别系统（别名：语音识别管理平台、会议纪要管理平台）

    打开由 Seeed Studio 开发的 SenseCraft Voice 语音识别系统的Web管理平台。
    该系统运行在云端，使用 reRouter 设备搭配 reSpeaker XVF3800 麦克风阵列
    进行高质量的语音采集和识别。

    SenseCraft Voice 是一个专业的语音识别和对话系统，提供完整的管理功能：

    1. 【仪表盘 Dashboard】- 系统总览
       - 总记录数：显示累计语音记录数量和今日增量（例如：124,575条，今日+973）
       - 点位数量：显示已配置的门店/设备数量（例如：5个门店下所有点位）
       - 今日完成数据：显示当天数据采集完成进度（例如：23%，已完成3/13个设备）
       - 关键词触发：显示今日触发关键词次数（例如：2次）
       - 今日采集趋势图：按时间展示24小时内的语音采集量分布
       - 今日活跃设备：显示活跃话筒设备数量和设备生产记录
       - 最近记录：展示最新的语音交互记录列表
       - 关键词热度分析：统计关键词出现频率（全部/传播量/舆后/投诉）

    2. 【AI分析】- AI智能分析与录音管理
       - 与AI助手对话分析语音内容
       - 获取数据洞察和业务建议
       - 支持优化询问策略
       - 录音记录查询和管理
       - 按门店/点位/时间筛选数据
       - 实时语音对话功能

    3. 【录音管理】- 全部设备录音
       - 搜索录音（支持MAC地址搜索）
       - 按录音状态筛选（全部/已录音/未录音）
       - 查看设备列表和录音详情
       - 支持按开始日期和结束日期范围筛选
       - 导出和重置功能

    4. 【门店管理】- 店铺与设备管理
       - 门店管理：创建和管理门店信息
       - 点位管理：配置具体的设备部署位置
       - 设备管理：管理麦克风阵列等硬件设备
       - 查看门店名称、门店代码、地址、联系人信息
       - 实时监控设备状态（正常/未分配）
       - 编辑、定位、复制、删除操作

    5. 【后台配置】- 系统设置
       - 关键词配置：设置需要监控的关键词和近义词
       - 用户管理：管理系统用户权限
       - 系统维护接口：配置API和系统参数
       - 标记颜色设置：自定义关键词标记颜色

    硬件配置：
    - 主控设备：reRouter（Seeed Studio网关设备）
    - 麦克风阵列：reSpeaker XVF3800（4麦远场语音采集模组）
    - 部署方式：云端管理平台 + 本地设备采集

    Args:
        browser (str, optional): 浏览器类型，默认为None（自动选择系统最佳浏览器）
            可选值:
                - None: 自动选择（Windows用Edge，Linux用Firefox，macOS用Safari）
                - "firefox": Mozilla Firefox
                - "chrome": Google Chrome
                - "chromium": Chromium 浏览器
                - "edge": Microsoft Edge（仅 Windows）
                - "safari": Safari（仅 macOS）

    Returns:
        dict: 执行结果
            {
                "success": bool,              # 是否成功打开
                "message": str,               # 执行消息
                "browser_used": str,          # 实际使用的浏览器
                "system": str,                # 操作系统
                "webpage_index": int,         # 网页索引
                "url": str                    # 打开的URL地址
            }

    Examples:
        - "打开SenseCraft Voice"
        - "打开语音识别系统"
        - "打开SenseCraft语音管理平台"
        - "用Firefox打开Seeed语音系统"
        - "打开录音管理系统"
        - "查看语音数据统计"
        - "打开语音识别系统仪表盘"

    Note:
        - 需要网络连接访问云端平台
        - 建议使用现代浏览器（Chrome/Firefox/Edge）以获得最佳体验
        - 首次访问可能需要登录账号
        - 部分功能可能需要管理员权限
        - 实时语音对话功能需要授权浏览器使用麦克风权限
    """
    print(f"open_sensecraft_voice called: browser={browser}")

    # SenseCraft Voice 云端管理平台地址
    url = "https://test-voice-web.seeed.cn/"

    result = GObj.browser.open_webpage(url, browser)

    if result.get("success"):
        result["url"] = url
        result["message"] = "✅ 成功打开 SenseCraft Voice 语音识别系统"

    return result


# 打开 reRouter 本地语音识别服务
def open_rerouter_voice_service(browser: str = None) -> dict:
    """
    打开 reRouter 本地语音识别服务（别名：会议纪要系统）

    打开运行在 reRouter 设备上的本地语音识别服务页面。
    该服务提供实时语音采集、处理和基础的设备控制功能。

    这是与 SenseCraft Voice 云端平台配套使用的本地设备服务，
    负责实际的语音采集和初步处理，然后将数据上传到云端平台进行分析。

    本地服务功能：
    - 实时语音采集：使用 reSpeaker XVF3800 麦克风阵列采集音频
    - 设备状态监控：查看麦克风、网络等硬件状态
    - 基础配置：网络设置、音量调节等
    - 录音控制：启动/停止录音
    - 日志查看：查看本地运行日志

    硬件配置：
    - 主控设备：reRouter（网关设备）
    - 麦克风阵列：reSpeaker XVF3800（4麦远场拾音）
    - 网络地址：192.168.2.142（局域网IP）
    - 访问端口：8090（本地服务端口）

    Args:
        browser (str, optional): 浏览器类型，默认为None（自动选择系统最佳浏览器）
            可选值:
                - None: 自动选择（Windows用Edge，Linux用Firefox，macOS用Safari）
                - "firefox": Mozilla Firefox
                - "chrome": Google Chrome
                - "chromium": Chromium 浏览器
                - "edge": Microsoft Edge（仅 Windows）
                - "safari": Safari（仅 macOS）

    Returns:
        dict: 执行结果
            {
                "success": bool,              # 是否成功打开
                "message": str,               # 执行消息
                "browser_used": str,          # 实际使用的浏览器
                "system": str,                # 操作系统
                "webpage_index": int,         # 网页索引
                "url": str,                   # 打开的URL地址
                "device_ip": str              # 设备IP地址
            }

    Examples:
        - "打开reRouter语音服务"
        - "打开本地语音识别服务"
        - "打开192.168.2.142语音服务"
        - "查看reRouter设备状态"
        - "打开麦克风控制页面"

    Note:
        - 需要确保设备在同一局域网内（192.168.2.x网段）
        - 需要能够访问 http://192.168.2.142:8090
        - 确保 reRouter 设备已启动
        - 确保 reSpeaker XVF3800 麦克风阵列已连接
        - 建议使用支持WebRTC的现代浏览器
        - 实时语音功能需要授权浏览器使用麦克风权限
    """
    print(f"open_rerouter_voice_service called: browser={browser}")

    # reRouter 本地服务地址
    device_ip = "192.168.2.142"
    port = "8090"
    url = f"http://{device_ip}:{port}"

    result = GObj.browser.open_webpage(url, browser)

    if result.get("success"):
        result["url"] = url
        result["device_ip"] = device_ip
        result["message"] = "✅ 成功打开 reRouter 本地语音识别服务"

    return result
