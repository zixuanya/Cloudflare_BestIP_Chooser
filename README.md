# Cloudflare_BestIP_Chooser
优选cloudflare ip API搭建，让你的节点飞起来！

# 项目介绍

这个项目可以用于在本地服务器上选择最快的cloudflare ip地址，在使用vless等可通过cloudflare WS反代类型的节点来说非常好用！

项目源码通过生成15W个ip进行全查测试，对服务器有一定要求，测试完成后只挑选50个最快项目IP

（数据内容可被更改，详情查看注释）

每隔3分钟更新一次IP地址，保证cloudflare最快IP的连结最新

# 使用方法

项目工作基于[cloverstd/tcping](https://github.com/cloverstd/tcping)的tcping套件，请下载他的二进制拷贝到linux命令区

下载完成后请执行一次 tcping 来检测是否安装成功

clone本项目，保存在你想要的地方

安装必要插件，aiohttp，flask..不说了自己去问chatgpt

安装完成后直接运行

一切正常的化，就可以在本地`127.0.0.1:5000/cfip`来看到你搭建的优选ip啦

# Q/A

Q：项目是通过什么检测的？

A：使用了[cloverstd/tcping](https://github.com/cloverstd/tcping)大佬开发的TCPING套件，而不是较为不准确的Ping

Q：为什么不使用HTTP真链接延迟测试？、

A：太慢了，生成的ip要等半年才能生成完成，HTTP真链接实际使用上尽管质量比tcping更好，但是对于服务器CPU性能的考验非常的大，还有无法正常工作的异步asyncio http访问问题，故直接抛弃

...

# 说明

本项目仅用于学习研究用途，请合理使用，使用本项目有可能违反[Cloudflare TOS](https://www.cloudflare.com/zh-cn/website-terms/)的相关内容，出现任何问题原作者不承担任何责任。

在使用相关代理服务时，请遵守贵国带来的相关法律效力，本项目只是作为参考演示使用
