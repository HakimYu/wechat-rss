from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import requests
import feedparser
from datetime import datetime


@register("wechat-rss", "HakimYu", "公众号文章推送 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.command("getWechatRss")
    async def getWechatRss(self, event: AstrMessageEvent):
        '''获取公众号文章推送指令'''
        response = requests.get(self.config.rss_url)

        if response.status_code != 200:
            yield event.plain_result("获取RSS内容失败")
            return

        try:
            feed = feedparser.parse(response.text)

            # 获取Feed基本信息
            feed_title = feed.feed.get('title', '未知')
            feed_updated = feed.feed.get('updated', '未知时间')

            result = f"📰 {feed_title}\n"
            result += f"更新时间: {feed_updated}\n"
            result += "=" * 30 + "\n\n"

            for entry in feed.entries[:5]:  # 获取最新的5篇文章
                # 获取文章标题（去除CDATA标记）
                title = entry.title.replace('<![CDATA[', '').replace(
                    ']]>', '') if hasattr(entry, 'title') else '无标题'

                # 获取作者信息
                author = entry.author if hasattr(entry, 'author') else '未知作者'

                # 获取发布时间
                published = entry.updated if hasattr(
                    entry, 'updated') else '未知时间'

                # 获取链接
                link = entry.link if hasattr(entry, 'link') else '#'

                result += f"📝 {title}\n"
                result += f"✍️ 作者: {author}\n"
                result += f"🕒 时间: {published}\n"
                result += f"🔗 链接: {link}\n"
                result += "-------------------\n"

            yield event.plain_result(result)

        except Exception as e:
            logger.error(f"解析RSS失败: {str(e)}")
            yield event.plain_result("解析RSS内容出错")
