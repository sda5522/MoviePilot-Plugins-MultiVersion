import threading
import time
from typing import Dict, List, Optional

from app.core.event import eventmanager, Event
from app.db.downloadhistory_oper import DownloadHistoryOper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType, MediaType


class MultiVersionDownload(_PluginBase):
    """
    多版本下载插件 V2
    
    核心功能：
    1. 监听订阅下载完成事件
    2. 等待指定时间后（确保MP处理完成）
    3. 根据选中的规则组下载其他版本
    
    技术特点：
    - 完全复用MP的 SearchChain.process() 和 DownloadChain.download_single()
    - 通过检查下载历史避免重复下载
    - 直接调用 DownloadChain 绕过订阅的洗版检查
    - MP自动通过重命名格式区分不同分辨率文件
    """
    
    # 插件名称
    plugin_name = "多版本下载增强版"
    # 插件描述
    plugin_desc = "突破洗版限制，自动下载多个规则组匹配的版本。（增强版）"
    # 插件图标
    plugin_icon = "download.png"
    # 插件版本
    plugin_version = "1.0.1"
    # 插件作者
    plugin_author = "sda5522"
    # 作者主页
    author_url = "https://github.com/sda5522/MoviePilot-Plugins-MultiVersion"
    # 插件配置项ID前缀
    plugin_config_prefix = "multiversiondownloadplus_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 2
    
    # 私有属性
    _enabled = False
    _selected_rules = {}
    _delay_seconds = 15
    _processing = {}  # {tmdbid: timestamp} 防止重复处理
    
    def init_plugin(self, config: dict = None):
        """初始化插件"""
        if config:
            self._enabled = config.get("enabled", False)
            self._selected_rules = config.get("selected_rules", {})
            self._delay_seconds = config.get("delay_seconds", 15)
            
        logger.info(f"多版本下载插件初始化完成，状态：{'启用' if self._enabled else '禁用'}")
        if self._enabled:
            logger.info(f"延迟时间：{self._delay_seconds}秒")
            logger.info(f"已选规则：{[k for k, v in self._selected_rules.items() if v]}")
    
    def get_state(self) -> bool:
        """获取插件状态"""
        return self._enabled
    
    @eventmanager.register(EventType.DownloadAdded)
    def on_download_added(self, event: Event):
        """
        监听下载添加事件
        
        关键：只处理来自订阅的下载
        MP执行订阅搜索并下载后会触发此事件
        """
        if not self._enabled:
            return
        
        # 获取已选择的规则
        enabled_rules = [name for name, enabled in self._selected_rules.items() if enabled]
        if not enabled_rules:
            logger.debug("多版本下载：未选择任何规则，跳过")
            return
        
        # 获取事件数据
        event_data = event.event_data
        if not event_data:
            return
        
        # 检查来源（只处理订阅下载）
        source = event_data.get("source", "")
        if not source or "Subscribe" not in source:
            logger.debug(f"多版本下载：来源不是订阅（{source}），跳过")
            return
        
        # 获取上下文
        context = event_data.get("context")
        if not context:
            return
        
        mediainfo = context.media_info
        if not mediainfo:
            return
        
        # 防止重复处理
        media_key = str(mediainfo.tmdb_id or mediainfo.douban_id)
        current_time = time.time()
        
        if media_key in self._processing:
            last_time = self._processing[media_key]
            if current_time - last_time < 60:  # 1分钟内不重复处理
                logger.debug(f"多版本下载：{mediainfo.title_year} 正在处理中，跳过")
                return
        
        # 记录处理时间
        self._processing[media_key] = current_time
        
        # 延迟执行（等待MP处理完成）
        logger.info(f"多版本下载：检测到订阅下载 {mediainfo.title_year}，将在 {self._delay_seconds} 秒后处理")
        
        threading.Timer(
            float(self._delay_seconds),
            self._download_multi_versions,
            args=[mediainfo, enabled_rules, media_key]
        ).start()
    
    def _download_multi_versions(self, mediainfo, rule_names: List[str], media_key: str):
        """
        核心功能：下载多个规则组匹配的版本
        
        策略：
        1. 使用 SearchChain.process() 搜索（指定规则组）
        2. 检查下载历史（避免重复）
        3. 使用 DownloadChain.download_single() 下载（绕过洗版检查）
        """
        from app.chain.search import SearchChain
        from app.chain.download import DownloadChain
        
        try:
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"开始多版本下载: {mediainfo.title_year}")
            logger.info(f"处理规则: {rule_names}")
            
            search_chain = SearchChain()
            download_chain = DownloadChain()
            downloadhis = DownloadHistoryOper()
            
            success_count = 0
            skip_count = 0
            fail_count = 0
            
            for rule_name in rule_names:
                logger.info(f"正在处理规则: {rule_name}")
                
                try:
                    # 1. 使用MP的搜索API（指定规则组）
                    contexts = search_chain.process(
                        mediainfo=mediainfo,
                        rule_groups=[rule_name]
                    )
                    
                    if not contexts:
                        logger.info(f"  └─ 未搜索到资源")
                        fail_count += 1
                        continue
                    
                    best_context = contexts[0]
                    torrent = best_context.torrent_info
                    
                    logger.info(f"  ├─ 匹配到: {torrent.title}")
                    logger.info(f"  ├─ 优先级: {torrent.pri_order}")
                    
                    # 2. 检查下载历史（避免重复）
                    if torrent.hash:
                        history = downloadhis.get_by_hash(torrent.hash)
                        if history:
                            logger.info(f"  └─ ⏭️ 已下载过（hash相同），跳过")
                            skip_count += 1
                            continue
                    
                    # 3. 直接下载（关键：不经过SubscribeChain，绕过洗版检查）
                    logger.info(f"  ├─ 开始下载...")
                    download_id = download_chain.download_single(
                        context=best_context,
                        username=self.plugin_name,
                        source="MultiVersion"
                    )
                    
                    if download_id:
                        logger.info(f"  └─ ✅ 下载成功")
                        success_count += 1
                    else:
                        logger.info(f"  └─ ⚠️ 下载失败（可能下载器已存在）")
                        skip_count += 1
                        
                except Exception as e:
                    logger.error(f"  └─ ❌ 处理失败: {str(e)}")
                    fail_count += 1
                    continue
            
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"多版本下载完成: {mediainfo.title_year}")
            logger.info(f"成功: {success_count}, 跳过: {skip_count}, 失败: {fail_count}")
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        except Exception as e:
            logger.error(f"多版本下载异常: {str(e)}", exc_info=True)
        finally:
            # 清理处理记录
            if media_key in self._processing:
                del self._processing[media_key]
    
    def get_form(self) -> tuple:
        """配置表单"""
        from app.helper.rule import RuleHelper
        
        # 获取系统规则组
        rule_groups = RuleHelper().get_rule_groups()
        
        # 构建规则选择UI
        rule_items = []
        for group in rule_groups:
            rule_items.append({
                'component': 'VCard',
                'props': {
                    'variant': 'tonal',
                    'class': 'mb-3'
                },
                'content': [
                    {
                        'component': 'VCardTitle',
                        'text': group.name
                    },
                    {
                        'component': 'VCardSubtitle',
                        'text': f"规则: {group.rule_string[:80]}..." if len(group.rule_string) > 80 else f"规则: {group.rule_string}"
                    },
                    {
                        'component': 'VCardText',
                        'content': [{
                            'component': 'VSwitch',
                            'props': {
                                'model': f'selected_rules.{group.name}',
                                'label': '✅ 一并保存此版本',
                                'color': 'primary'
                            }
                        }]
                    }
                ]
            })
        
        return [
            {
                'component': 'VForm',
                'content': [
                    # 主开关
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
                                    'hint': '启用后自动处理所有订阅下载',
                                    'persistent-hint': True,
                                    'color': 'primary'
                                }
                            }]
                        }]
                    },
                    
                    # 延迟时间设置
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12, 'md': 6},
                            'content': [{
                                'component': 'VTextField',
                                'props': {
                                    'model': 'delay_seconds',
                                    'label': '延迟时间（秒）',
                                    'type': 'number',
                                    'hint': 'MP订阅下载完成后等待多久再执行插件（建议15-30秒）',
                                    'persistent-hint': True
                                }
                            }]
                        }]
                    },
                    
                    # 使用说明
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'info',
                                    'variant': 'tonal',
                                    'text': '💡 使用说明\n'
                                           '1. 勾选需要同时下载的规则组\n'
                                           '2. 启用插件后，MP订阅下载完成后会自动触发\n'
                                           '3. 插件会等待指定时间后下载其他规则匹配的版本\n'
                                           '4. 完全复用MP的搜索和下载，安全可靠'
                                }
                            }]
                        }]
                    },
                    
                    # 规则选择区域标题
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'success',
                                    'variant': 'tonal',
                                    'title': '📋 选择需要下载的规则组',
                                    'text': '从MP系统设置中读取，勾选需要一并保存的版本'
                                }
                            }]
                        }]
                    },
                    
                    # 规则列表
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': rule_items if rule_items else [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'warning',
                                    'text': '未找到规则组，请先在系统设置中配置'
                                }
                            }]
                        }]
                    },
                    
                    # 前置条件提醒
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'warning',
                                    'variant': 'tonal',
                                    'title': '⚠️ 前置条件',
                                    'text': '1. 确保MP重命名格式包含 videoFormat 变量（用于区分分辨率）\n'
                                           '2. 建议设置覆盖模式为"从不覆盖"或"大覆盖小"\n'
                                           '3. 洗版功能可以正常开启，插件会自动绕过洗版限制'
                                }
                            }]
                        }]
                    }
                ]
            }
        ], {
            "enabled": False,
            "selected_rules": {},
            "delay_seconds": 15
        }
    
    def get_page(self) -> List[dict]:
        """插件详情页"""
        return [
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VAlert',
                                'props': {
                                    'type': 'info',
                                    'variant': 'tonal',
                                    'title': '🎯 插件原理',
                                    'text': '1. 监听订阅下载完成事件（MP执行订阅搜索并下载后触发）\n'
                                           '2. 等待指定时间（确保MP处理完成）\n'
                                           '3. 使用MP的SearchChain.process()搜索其他规则\n'
                                           '4. 检查下载历史避免重复\n'
                                           '5. 使用MP的DownloadChain.download_single()直接下载（绕过洗版检查）\n'
                                           '6. MP自动重命名和入库（videoFormat区分不同分辨率）'
                                }
                            }
                        ]
                    },
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VAlert',
                                'props': {
                                    'type': 'success',
                                    'variant': 'tonal',
                                    'title': '✅ 技术特点',
                                    'text': '• 完全复用MP官方API，不自己实现搜索下载\n'
                                           '• 直接调用DownloadChain，自动绕过订阅的洗版限制\n'
                                           '• 基于种子hash检查历史，精确去重\n'
                                           '• MP自动重命名，不同分辨率自动区分文件名\n'
                                           '• 下载器自动去重，避免添加重复种子'
                                }
                            }
                        ]
                    },
                    {
                        'component': 'VCol',
                        'props': {'cols': 12},
                        'content': [
                            {
                                'component': 'VAlert',
                                'props': {
                                    'type': 'warning',
                                    'variant': 'tonal',
                                    'title': '📝 使用场景',
                                    'text': '场景1: 用户订阅电影，MP默认下载4K版本\n'
                                           '       插件自动下载1080P版本（供移动设备）\n\n'
                                           '场景2: 用户订阅剧集，开启洗版，MP下载最优版本\n'
                                           '       插件同时下载其他规则匹配的版本（多版本收藏）\n\n'
                                           '场景3: 同时下载不同字幕组、不同压制组的版本'
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    
    def stop_service(self):
        """停止插件"""
        logger.info("多版本下载插件已停止")

