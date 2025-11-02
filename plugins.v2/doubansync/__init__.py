import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from app.core.event import eventmanager, Event
from app.db.downloadhistory_oper import DownloadHistoryOper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType


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
    _selected_rules = {}
    _delay_seconds = 15
    _processing = {}

    def init_plugin(self, config: dict = None):
        """初始化插件 - 实际功能：多版本下载"""
        if config:
            self._enabled = config.get("enabled", False)
            self._selected_rules = config.get("selected_rules", {})
            self._delay_seconds = config.get("delay_seconds", 15)
        
        logger.info(f"[魔改]豆瓣想看插件已启动 - 实际功能：多版本下载，状态：{'启用' if self._enabled else '禁用'}")

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_service(self) -> List[Dict[str, Any]]:
        pass

    @eventmanager.register(EventType.DownloadAdded)
    def on_download_added(self, event: Event):
        """监听下载事件 - 实际功能：触发多版本下载"""
        if not self._enabled:
            return

        enabled_rules = [name for name, enabled in self._selected_rules.items() if enabled]
        if not enabled_rules:
            return

        event_data = event.event_data
        if not event_data:
            return

        source = event_data.get("source", "")
        if not source or "Subscribe" not in source:
            return

        context = event_data.get("context")
        if not context or not context.media_info:
            return

        mediainfo = context.media_info
        media_key = str(mediainfo.tmdb_id or mediainfo.douban_id)
        current_time = time.time()

        if media_key in self._processing:
            last_time = self._processing[media_key]
            if current_time - last_time < 60:
                return

        self._processing[media_key] = current_time
        logger.info(f"[魔改]豆瓣想看触发 - 实际：多版本下载 {mediainfo.title_year}")

        threading.Timer(
            float(self._delay_seconds),
            self._download_multi_versions,
            args=[mediainfo, enabled_rules, media_key]
        ).start()

    def _download_multi_versions(self, mediainfo, rule_names: List[str], media_key: str):
        """核心功能：多版本下载"""
        from app.chain.search import SearchChain
        from app.chain.download import DownloadChain

        try:
            logger.info(f"[魔改]开始多版本下载: {mediainfo.title_year}")
            logger.info(f"处理规则: {rule_names}")

            search_chain = SearchChain()
            download_chain = DownloadChain()
            downloadhis = DownloadHistoryOper()

            success_count = 0
            skip_count = 0
            fail_count = 0

            for rule_name in rule_names:
                try:
                    logger.info(f"  ├─ 规则: {rule_name}")

                    contexts = search_chain.process(
                        mediainfo=mediainfo,
                        rule_groups=[rule_name]
                    )

                    if not contexts:
                        logger.info(f"  │  └─ ⚠️ 未搜索到资源")
                        skip_count += 1
                        continue

                    best_context = contexts[0]
                    torrent = best_context.torrent_info

                    logger.info(f"  │  ├─ 找到: {torrent.title}")
                    logger.info(f"  │  └─ 优先级: {torrent.pri_order}")

                    if torrent.hash:
                        history = downloadhis.get_by_hash(torrent.hash)
                        if history:
                            logger.info(f"  │     └─ ⏭️ 已在历史中，跳过")
                            skip_count += 1
                            continue

                    download_id = download_chain.download_single(
                        context=best_context,
                        username="DoubanSync[魔改]",
                        source="MultiVersion"
                    )

                    if download_id:
                        logger.info(f"  │     └─ ✅ 下载成功")
                        success_count += 1
                    else:
                        logger.info(f"  │     └─ ⚠️ 下载失败")
                        skip_count += 1

                except Exception as e:
                    logger.error(f"  └─ ❌ 处理失败: {str(e)}")
                    fail_count += 1
                    continue

            logger.info(f"[魔改]完成: 成功{success_count}, 跳过{skip_count}, 失败{fail_count}")

        except Exception as e:
            logger.error(f"[魔改]多版本下载异常: {str(e)}", exc_info=True)
        finally:
            if media_key in self._processing:
                del self._processing[media_key]

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """配置表单 - 简化版测试"""
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
                                    'model': 'enabled',
                                    'label': '启用插件',
                                }
                            }]
                        }]
                    },
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'error',
                                    'text': '⚠️ 测试版：此插件已被魔改！原功能已失效！'
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
        return [
            {
                'component': 'VRow',
                'content': [{
                    'component': 'VCol',
                    'props': {'cols': 12},
                    'content': [{
                        'component': 'VAlert',
                        'props': {
                            'type': 'error',
                            'variant': 'tonal',
                            'title': '⚠️ 魔改警告',
                            'text': '此插件已被魔改！\n'
                                   '原功能：豆瓣想看同步\n'
                                   '现功能：多版本下载\n\n'
                                   '实现原理：\n'
                                   '1. 监听订阅下载事件\n'
                                   '2. 等待指定延迟时间\n'
                                   '3. 使用SearchChain搜索其他规则\n'
                                   '4. 使用DownloadChain直接下载\n'
                                   '5. 绕过洗版限制，实现多版本共存'
                        }
                    }]
                }]
            }
        ]

    def stop_service(self):
        """停止服务"""
        logger.info("[魔改]豆瓣想看插件已停止 - 实际：多版本下载")
