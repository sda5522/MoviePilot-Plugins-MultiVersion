from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.plugins import _PluginBase


class DoubanSync(_PluginBase):
    # 插件名称
    plugin_name = "豆瓣想看"
    # 插件描述
    plugin_desc = "同步豆瓣想看数据，自动添加订阅。"
    # 插件图标
    plugin_icon = "douban.png"
    # 插件版本
    plugin_version = "2.1.0"
    # 插件作者
    plugin_author = "jxxghp,dwhmofly"
    # 作者主页
    author_url = "https://github.com/jxxghp"
    # 插件配置项ID前缀
    plugin_config_prefix = "doubansync_"
    # 加载顺序
    plugin_order = 3
    # 可使用的用户级别
    auth_level = 2

    # 私有属性
    _enabled = False

    def init_plugin(self, config: dict = None):
        """初始化插件"""
        if config:
            self._enabled = config.get("enabled", False)
        logger.info(f"豆瓣想看插件初始化完成")

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """配置表单"""
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VSwitch',
                                'props': {
                                    'model': 'enabled'，
                                    'label': '启用插件',
                                }
                            }]
                        }]
                    }
                ]
            }
        ], {
            "enabled": False
        }

    def get_page(self) -> List[dict]:
        """详情页"""
        return [{
            'component': 'div',
            'text': '空壳测试版本'
        }]

    def stop_service(self):
        """停止服务"""
        pass
