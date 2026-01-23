"""
环境变量操作工具函数集
提供完整的环境变量读取、设置、验证等功能
"""
import os
import platform
import subprocess
import sys
import logging
from typing import Optional, Dict, List, Any, Union, Tuple
from SysManger.debugOut import log

'''环境变量读取函数'''
# 获取环境变量的值
def get_env(key: str, default: Optional[str] = None, required: bool = False, var_type: type = str) -> Any:
    """
    获取环境变量的值

    Args:
        key: 环境变量名称
        default: 默认值（如果环境变量不存在）
        required: 是否为必需的环境变量（True 时如果不存在会退出程序）
        var_type: 变量类型（str, int, float, bool）

    Returns:
        Any: 环境变量的值，根据 var_type 转换类型

    Raises:
        SystemExit: 当 required=True 且环境变量不存在时

    示例:
        >>> api_key = get_env("API_KEY", required=True)
        >>> port = get_env("PORT", default="8080", var_type=int)
        >>> debug = get_env("DEBUG", default="false", var_type=bool)
    """
    try:
        value = os.environ.get(key)

        # 如果环境变量不存在
        if value is None:
            if required:
                log.error(f"必需的环境变量未设置: {key}")
                log.error(f"请设置环境变量: export {key}=<value>")
                sys.exit(1)
            return default

        # 类型转换
        if var_type == bool:
            # 布尔值特殊处理
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        else:
            return value

    except ValueError as e:
        log.error(f"环境变量 {key} 类型转换失败: {e}")
        log.error(f"期望类型: {var_type.__name__}, 实际值: {value}")
        if required:
            sys.exit(1)
        return default
    except Exception as e:
        log.error(f"get_env() error: {e}")
        if required:
            sys.exit(1)
        return default

# 获取环境变量并解析为列表
def get_env_list(key: str, default: Optional[List[str]] = None, separator: str = ",", required: bool = False) -> List[str]:
    """
    获取环境变量并解析为列表（用分隔符分割）

    Args:
        key: 环境变量名称
        default: 默认值（列表）
        separator: 分隔符（默认为逗号）
        required: 是否为必需的环境变量

    Returns:
        List[str]: 字符串列表

    示例:
        >>> # 环境变量: ALLOWED_HOSTS=localhost,127.0.0.1,example.com
        >>> hosts = get_env_list("ALLOWED_HOSTS")
        >>> print(hosts)
        ['localhost', '127.0.0.1', 'example.com']
    """
    value = get_env(key, required=required)

    if value is None:
        return default if default is not None else []

    # 分割并去除空白
    items = [item.strip() for item in value.split(separator) if item.strip()]
    return items

# 获取环境变量并解析为字典
def get_env_dict(key: str, default: Optional[Dict[str, str]] = None, pair_separator: str = ",", kv_separator: str = "=", required: bool = False) -> Dict[str, str]:
    """
    获取环境变量并解析为字典

    Args:
        key: 环境变量名称
        default: 默认值（字典）
        pair_separator: 键值对之间的分隔符（默认为逗号）
        kv_separator: 键和值之间的分隔符（默认为等号）
        required: 是否为必需的环境变量

    Returns:
        Dict[str, str]: 字典

    示例:
        >>> # 环境变量: DATABASE=host=localhost,port=5432,user=admin
        >>> db_config = get_env_dict("DATABASE")
        >>> print(db_config)
        {'host': 'localhost', 'port': '5432', 'user': 'admin'}
    """
    value = get_env(key, required=required)

    if value is None:
        return default if default is not None else {}

    result = {}
    pairs = value.split(pair_separator)

    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue

        if kv_separator in pair:
            k, v = pair.split(kv_separator, 1)
            result[k.strip()] = v.strip()
        else:
            log.warning(f"忽略无效的键值对: {pair}")

    return result


'''环境变量设置函数'''
# 设置环境变量
def set_env(key: str, value: Any, override: bool = True) -> bool:
    """
    设置环境变量

    Args:
        key: 环境变量名称
        value: 环境变量的值（会自动转换为字符串）
        override: 是否覆盖已存在的环境变量

    Returns:
        bool: 设置成功返回 True，已存在且不覆盖返回 False

    示例:
        >>> set_env("API_KEY", "your-api-key")
        >>> set_env("PORT", 8080)
        >>> set_env("DEBUG", True)
    """
    try:
        # 检查是否已存在
        if key in os.environ and not override:
            log.debug(f"环境变量 {key} 已存在，跳过设置")
            return False

        # 转换为字符串并设置
        os.environ[key] = str(value)
        log.debug(f"环境变量已设置: {key}={value}")
        return True

    except Exception as e:
        log.error(f"set_env() error: {e}")
        return False

# 从字典批量设置环境变量
def set_env_from_dict(env_dict: Dict[str, Any], override: bool = True) -> int:
    """
    从字典批量设置环境变量

    Args:
        env_dict: 环境变量字典
        override: 是否覆盖已存在的环境变量

    Returns:
        int: 成功设置的环境变量数量

    示例:
        >>> config = {
        ...     "API_KEY": "xxx",
        ...     "PORT": 8080,
        ...     "DEBUG": True
        ... }
        >>> count = set_env_from_dict(config)
        >>> print(f"设置了 {count} 个环境变量")
    """
    count = 0
    for key, value in env_dict.items():
        if set_env(key, value, override):
            count += 1

    log.info(f"批量设置了 {count} 个环境变量")
    return count

# 设置环境变量（仅当不存在时）
def set_env_if_not_exists(key: str, value: Any) -> bool:
    """
    仅当环境变量不存在时才设置（不覆盖已有值）

    Args:
        key: 环境变量名称
        value: 环境变量的值

    Returns:
        bool: 设置成功返回 True，已存在返回 False

    示例:
        >>> set_env_if_not_exists("PORT", "8080")  # 设置默认端口
    """
    return set_env(key, value, override=False)

'''环境变量删除函数'''
# 删除环境变量
def del_env(key: str) -> bool:
    """
    删除环境变量

    Args:
        key: 环境变量名称

    Returns:
        bool: 删除成功返回 True，不存在返回 False

    示例:
        >>> del_env("TEMP_VAR")
    """
    try:
        if key in os.environ:
            del os.environ[key]
            log.debug(f"环境变量已删除: {key}")
            return True
        else:
            log.debug(f"环境变量不存在: {key}")
            return False
    except Exception as e:
        log.error(f"del_env() error: {e}")
        return False

# 清空指定前缀的环境变量
def clear_env_by_prefix(prefix: str) -> int:
    """
    删除所有指定前缀的环境变量

    Args:
        prefix: 前缀字符串

    Returns:
        int: 删除的环境变量数量

    示例:
        >>> # 删除所有以 TEMP_ 开头的环境变量
        >>> count = clear_env_by_prefix("TEMP_")
        >>> print(f"删除了 {count} 个临时环境变量")
    """
    keys_to_delete = [key for key in os.environ.keys() if key.startswith(prefix)]

    for key in keys_to_delete:
        del os.environ[key]

    log.info(f"删除了 {len(keys_to_delete)} 个前缀为 '{prefix}' 的环境变量")
    return len(keys_to_delete)

'''环境变量检查函数'''
# 检查环境变量是否存在
def check_env(key: str) -> bool:
    """
    检查环境变量是否存在

    Args:
        key: 环境变量名称

    Returns:
        bool: 存在返回 True，不存在返回 False

    示例:
        >>> if check_env("API_KEY"):
        ...     print("API Key 已配置")
    """
    return key in os.environ

# 检查多个必需的环境变量
def check_required_envs(keys: List[str], exit_on_missing: bool = True) -> bool:
    """
    检查多个必需的环境变量是否都已设置

    Args:
        keys: 环境变量名称列表
        exit_on_missing: 如果有缺失是否退出程序

    Returns:
        bool: 全部存在返回 True，有缺失返回 False

    示例:
        >>> required_vars = ["API_KEY", "DATABASE_URL", "SECRET_KEY"]
        >>> check_required_envs(required_vars)
    """
    missing = []

    for key in keys:
        if not check_env(key):
            missing.append(key)

    if missing:
        log.error(f"缺少必需的环境变量: {', '.join(missing)}")
        for key in missing:
            log.error(f"  请设置: export {key}=<value>")

        if exit_on_missing:
            sys.exit(1)
        return False

    log.info(f"所有必需的环境变量已设置: {', '.join(keys)}")
    return True

# 获取环境变量
def validate_env(key: str, valid_values: Optional[List[str]] = None, validator_func: Optional[callable] = None, required: bool = False) -> bool:
    """
    验证环境变量的值是否有效

    Args:
        key: 环境变量名称
        valid_values: 有效值列表（如果提供，值必须在列表中）
        validator_func: 自定义验证函数（返回 bool）
        required: 是否为必需的环境变量

    Returns:
        bool: 验证通过返回 True，失败返回 False

    示例:
        >>> # 验证值是否在列表中
        >>> validate_env("LOG_LEVEL", valid_values=["DEBUG", "INFO", "WARNING", "ERROR"])

        >>> # 自定义验证函数
        >>> validate_env("PORT", validator_func=lambda x: x.isdigit() and 1 <= int(x) <= 65535)
    """
    value = get_env(key, required=required)

    if value is None:
        return not required

    # 检查有效值列表
    if valid_values is not None:
        if value not in valid_values:
            log.error(f"环境变量 {key} 的值无效: {value}")
            log.error(f"有效值: {', '.join(valid_values)}")
            return False

    # 自定义验证函数
    if validator_func is not None:
        try:
            if not validator_func(value):
                log.error(f"环境变量 {key} 验证失败: {value}")
                return False
        except Exception as e:
            log.error(f"环境变量 {key} 验证异常: {e}")
            return False

    return True

# 环境变量信息函数
def list_env(prefix: Optional[str] = None, pattern: Optional[str] = None) -> Dict[str, str]:
    """
    列出环境变量

    Args:
        prefix: 只列出指定前缀的环境变量
        pattern: 只列出包含指定模式的环境变量（模糊匹配）

    Returns:
        Dict[str, str]: 环境变量字典

    示例:
        >>> # 列出所有环境变量
        >>> all_vars = list_env()

        >>> # 列出所有以 MCP_ 开头的环境变量
        >>> mcp_vars = list_env(prefix="MCP_")

        >>> # 列出所有包含 KEY 的环境变量
        >>> key_vars = list_env(pattern="KEY")
    """
    result = {}

    for key, value in os.environ.items():
        # 前缀过滤
        if prefix and not key.startswith(prefix):
            continue

        # 模式过滤
        if pattern and pattern not in key:
            continue

        result[key] = value

    return result

# 打印环境变量
def print_env(prefix: Optional[str] = None, mask_sensitive: bool = True, sensitive_keywords: Optional[List[str]] = None) -> None:
    """
    打印环境变量（用于调试）

    Args:
        prefix: 只打印指定前缀的环境变量
        mask_sensitive: 是否屏蔽敏感信息
        sensitive_keywords: 敏感关键词列表（包含这些关键词的变量会被屏蔽）

    示例:
        >>> # 打印所有 MCP_ 开头的环境变量
        >>> print_env(prefix="MCP_")

        >>> # 打印时屏蔽敏感信息
        >>> print_env(mask_sensitive=True)
    """
    if sensitive_keywords is None:
        sensitive_keywords = ["KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL"]

    env_vars = list_env(prefix=prefix)

    print("=" * 70)
    print(f"环境变量列表 {f'(前缀: {prefix})' if prefix else ''}")
    print("=" * 70)

    if not env_vars:
        print("(无环境变量)")
    else:
        for key, value in sorted(env_vars.items()):
            # 检查是否为敏感信息
            is_sensitive = mask_sensitive and any(
                keyword in key.upper() for keyword in sensitive_keywords
            )

            if is_sensitive:
                masked_value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
                print(f"{key} = {masked_value}")
            else:
                print(f"{key} = {value}")

    print("=" * 70)

# 导出环境变量
def export_env_to_dict(prefix: Optional[str] = None) -> Dict[str, str]:
    """
    导出环境变量到字典（可用于保存或传递）

    Args:
        prefix: 只导出指定前缀的环境变量

    Returns:
        Dict[str, str]: 环境变量字典

    示例:
        >>> env_backup = export_env_to_dict(prefix="MCP_")
        >>> # 后续可以用 set_env_from_dict() 恢复
    """
    return list_env(prefix=prefix)

# 导入环境变量
def load_env_from_file(file_path: str, override: bool = False, encoding: str = "utf-8") -> int:
    """
    从文件加载环境变量（支持 .env 文件格式）

    Args:
        file_path: 文件路径
        override: 是否覆盖已存在的环境变量
        encoding: 文件编码

    Returns:
        int: 加载的环境变量数量

    文件格式:
        KEY1=value1
        KEY2=value2
        # 这是注释
        KEY3="value with spaces"

    示例:
        >>> count = load_env_from_file(".env")
        >>> print(f"加载了 {count} 个环境变量")
    """
    if not os.path.exists(file_path):
        log.warning(f"环境变量文件不存在: {file_path}")
        return 0

    count = 0

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            for line_num, line in enumerate(f, 1):
                # 去除空白和注释
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 去除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # 设置环境变量
                    if set_env(key, value, override):
                        count += 1
                else:
                    log.warning(f"忽略无效行 {line_num}: {line}")

        log.info(f"从 {file_path} 加载了 {count} 个环境变量")
        return count

    except Exception as e:
        log.error(f"load_env_from_file() error: {e}")
        return 0


'''高级工具函数'''
class EnvConfig:
    """
    环境变量配置类（用于管理一组相关的环境变量）

    示例:
        >>> config = EnvConfig(prefix="MCP_")
        >>> config.require("ENDPOINT")
        >>> config.optional("TIMEOUT", default="30", var_type=int)
        >>> config.validate()
        >>> endpoint = config.get("ENDPOINT")
    """

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.required_vars = []
        self.optional_vars = {}
        self.values = {}

    # 添加必需的环境变量
    def require(self, key: str, var_type: type = str):
        """添加必需的环境变量"""
        full_key = f"{self.prefix}{key}"
        self.required_vars.append((key, full_key, var_type))

    # 添加可选的环境变量
    def optional(self, key: str, default: Any = None, var_type: type = str):
        """添加可选的环境变量"""
        full_key = f"{self.prefix}{key}"
        self.optional_vars[key] = (full_key, default, var_type)

    # 验证并加载所有环境变量
    def validate(self) -> bool:
        """验证并加载所有环境变量"""
        # 检查必需变量
        for key, full_key, var_type in self.required_vars:
            value = get_env(full_key, required=True, var_type=var_type)
            self.values[key] = value

        # 加载可选变量
        for key, (full_key, default, var_type) in self.optional_vars.items():
            value = get_env(full_key, default=default, var_type=var_type)
            self.values[key] = value

        return True

    # 获取环境变量
    def get(self, key: str) -> Any:
        """获取环境变量的值"""
        return self.values.get(key)

    # 获取所有环境变量
    def get_all(self) -> Dict[str, Any]:
        """获取所有环境变量"""
        return self.values.copy()


'''系统命令执行函数'''

# 执行系统命令（跨平台支持 Windows/Linux/macOS）
def run_command(command: Union[str, List[str]], shell: bool = True, capture_output: bool = True, timeout: Optional[int] = None, encoding: str = 'utf-8', check: bool = False, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """
    执行系统命令（跨平台支持 Windows/Linux/macOS）

    Args:
        command: 要执行的命令（字符串或列表）
        shell: 是否通过 shell 执行
        capture_output: 是否捕获输出
        timeout: 超时时间（秒）
        encoding: 输出编码
        check: 如果命令失败是否抛出异常
        cwd: 工作目录
        env: 环境变量字典（会合并到当前环境）

    Returns:
        Tuple[int, str, str]: (返回码, 标准输出, 标准错误)

    示例:
        >>> # 简单命令
        >>> code, stdout, stderr = run_command("ls -la")
        >>>
        >>> # Windows 命令
        >>> code, stdout, stderr = run_command("dir")
        >>>
        >>> # Python 命令
        >>> code, stdout, stderr = run_command("python --version")
        >>>
        >>> # 使用列表形式（更安全，避免 shell 注入）
        >>> code, stdout, stderr = run_command(["ls", "-la"], shell=False)
        >>>
        >>> # 设置超时和工作目录
        >>> code, stdout, stderr = run_command("git status", timeout=10, cwd="/path/to/repo")
    """
    try:
        # 合并环境变量
        final_env = os.environ.copy()
        if env:
            final_env.update(env)

        log.debug(f"执行命令: {command}")

        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            timeout=timeout,
            encoding=encoding,
            check=check,
            cwd=cwd,
            env=final_env if env else None
        )

        stdout = result.stdout if result.stdout else ""
        stderr = result.stderr if result.stderr else ""

        log.debug(f"命令返回码: {result.returncode}")

        return result.returncode, stdout, stderr

    except subprocess.TimeoutExpired as e:
        log.error(f"命令执行超时: {command}")
        return -1, "", f"Timeout after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        log.error(f"命令执行失败: {e}")
        return e.returncode, e.stdout or "", e.stderr or ""
    except Exception as e:
        log.error(f"run_command() error: {e}")
        return -1, "", str(e)

# 执行 Python 命令
def run_python_command(command: Union[str, List[str]], python_path: str = "python3", **kwargs) -> Tuple[int, str, str]:
    """
    执行 Python 命令

    Args:
        command: Python 命令或脚本路径
        python_path: Python 解释器路径（默认 python3）
        **kwargs: 传递给 run_command 的其他参数

    Returns:
        Tuple[int, str, str]: (返回码, 标准输出, 标准错误)

    示例:
        >>> # 执行 Python 脚本
        >>> code, stdout, stderr = run_python_command("script.py")
        >>>
        >>> # 执行 Python 代码
        >>> code, stdout, stderr = run_python_command(["-c", "print('Hello')"])
        >>>
        >>> # 指定 Python 解释器
        >>> code, stdout, stderr = run_python_command("script.py", python_path="python3.10")
    """
    # 检测操作系统，Windows 上默认使用 python
    if platform.system() == "Windows" and python_path == "python3":
        python_path = "python"

    if isinstance(command, str):
        full_command = f"{python_path} {command}"
    else:
        full_command = [python_path] + command

    return run_command(full_command, **kwargs)

# 执行 pip 命令
def run_pip_command(command: str, pip_path: str = "pip3", **kwargs) -> Tuple[int, str, str]:
    """
    执行 pip 命令

    Args:
        command: pip 命令（不需要包含 pip）
        pip_path: pip 路径（默认 pip3）
        **kwargs: 传递给 run_command 的其他参数

    Returns:
        Tuple[int, str, str]: (返回码, 标准输出, 标准错误)

    示例:
        >>> # 安装包
        >>> code, stdout, stderr = run_pip_command("install requests")
        >>>
        >>> # 列出已安装的包
        >>> code, stdout, stderr = run_pip_command("list")
        >>>
        >>> # 使用虚拟环境的 pip
        >>> code, stdout, stderr = run_pip_command("install numpy", pip_path="venv/bin/pip")
    """
    if platform.system() == "Windows" and pip_path == "pip3":
        pip_path = "pip"

    full_command = f"{pip_path} {command}"
    return run_command(full_command, **kwargs)

# 获取系统信息
def get_system_info() -> Dict[str, str]:
    """
    获取系统信息

    Returns:
        Dict[str, str]: 系统信息字典

    示例:
        >>> info = get_system_info()
        >>> print(info['system'])  # Windows, Linux, Darwin
        >>> print(info['python_version'])
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }

# 判断是否为 Windows 系统
def is_windows() -> bool:
    """判断是否为 Windows 系统"""
    return platform.system() == "Windows"

# 判断是否为 Linux 系统
def is_linux() -> bool:
    """判断是否为 Linux 系统"""
    return platform.system() == "Linux"

# 判断是否为 macOS 系统
def is_macos() -> bool:
    """判断是否为 macOS 系统"""
    return platform.system() == "Darwin"

# 异步执行系统命令
def run_command_async(command: Union[str, List[str]], shell: bool = True, encoding: str = 'utf-8', cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.Popen:
    """
    异步执行系统命令（不等待命令完成）

    Args:
        command: 要执行的命令
        shell: 是否通过 shell 执行
        encoding: 输出编码
        cwd: 工作目录
        env: 环境变量字典

    Returns:
        subprocess.Popen: 进程对象

    示例:
        >>> # 启动后台进程
        >>> process = run_command_async("python server.py")
        >>> print(f"进程 PID: {process.pid}")
        >>>
        >>> # 稍后检查进程状态
        >>> if process.poll() is None:
        ...     print("进程仍在运行")
        >>>
        >>> # 等待进程完成
        >>> stdout, stderr = process.communicate()
        >>>
        >>> # 终止进程
        >>> process.terminate()
    """
    try:
        final_env = os.environ.copy()
        if env:
            final_env.update(env)

        log.debug(f"异步执行命令: {command}")

        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=encoding,
            cwd=cwd,
            env=final_env if env else None
        )

        log.debug(f"进程已启动，PID: {process.pid}")
        return process

    except Exception as e:
        log.error(f"run_command_async() error: {e}")
        raise

# 终止进程
def kill_process(pid: int, force: bool = False) -> bool:
    """
    终止进程

    Args:
        pid: 进程 ID
        force: 是否强制终止（Windows 上使用 /F，Linux 上使用 SIGKILL）

    Returns:
        bool: 成功返回 True

    示例:
        >>> kill_process(1234)
        >>> kill_process(1234, force=True)
    """
    try:
        if is_windows():
            flag = "/F" if force else "/T"
            code, _, _ = run_command(f"taskkill {flag} /PID {pid}")
        else:
            signal = "SIGKILL" if force else "SIGTERM"
            code, _, _ = run_command(f"kill -{signal} {pid}")

        return code == 0
    except Exception as e:
        log.error(f"kill_process() error: {e}")
        return False


# ============================================================================
# 使用示例
# ============================================================================

# if __name__ == "__main__":
#     # 配置日志
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )
#
#     print("=" * 70)
#     print("环境变量工具函数示例")
#     print("=" * 70)
#
#     # 1. 设置环境变量
#     print("\n[1] 设置环境变量")
#     set_env("TEST_VAR", "hello")
#     set_env("TEST_PORT", 8080)
#     set_env("TEST_DEBUG", True)
#
#     # 2. 读取环境变量
#     print("\n[2] 读取环境变量")
#     value = get_env("TEST_VAR")
#     port = get_env("TEST_PORT", var_type=int)
#     debug = get_env("TEST_DEBUG", var_type=bool)
#     print(f"TEST_VAR = {value} (type: {type(value).__name__})")
#     print(f"TEST_PORT = {port} (type: {type(port).__name__})")
#     print(f"TEST_DEBUG = {debug} (type: {type(debug).__name__})")
#
#     # 3. 批量设置
#     print("\n[3] 批量设置环境变量")
#     config = {
#         "TEST_API_KEY": "abc123",
#         "TEST_TIMEOUT": 30,
#         "TEST_ENABLED": True
#     }
#     set_env_from_dict(config)
#
#     # 4. 列表和字典解析
#     print("\n[4] 解析列表和字典格式")
#     set_env("TEST_HOSTS", "localhost,127.0.0.1,example.com")
#     hosts = get_env_list("TEST_HOSTS")
#     print(f"Hosts: {hosts}")
#
#     set_env("TEST_DB", "host=localhost,port=5432,user=admin")
#     db_config = get_env_dict("TEST_DB")
#     print(f"DB Config: {db_config}")
#
#     # 5. 检查和验证
#     print("\n[5] 检查和验证")
#     exists = check_env("TEST_VAR")
#     print(f"TEST_VAR exists: {exists}")
#
#     # 6. 打印环境变量
#     print("\n[6] 打印环境变量（TEST_ 开头）")
#     print_env(prefix="TEST_")
#
#     # 7. 使用 EnvConfig 类
#     print("\n[7] 使用 EnvConfig 类")
#     env_config = EnvConfig(prefix="TEST_")
#     env_config.require("API_KEY")
#     env_config.optional("RETRY", default="3", var_type=int)
#     env_config.validate()
#     print(f"配置: {env_config.get_all()}")
#
#     # 8. 清理
#     print("\n[8] 清理测试环境变量")
#     count = clear_env_by_prefix("TEST_")
#     print(f"清理了 {count} 个环境变量")
#
#     print("\n" + "=" * 70)
#     print("示例完成！")
#     print("=" * 70)