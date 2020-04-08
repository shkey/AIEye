# AIEye [![The MIT License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](http://opensource.org/licenses/MIT)

一个由 Flask，TensorFlow 和 Gevent 编写并使用 Docker 进行部署的能简单进行白内障识别检测的应用。

演示地址：<http://aieye.fumengji.com:8080>

## 如何部署使用？

> 前提是你的电脑上已经安装了 Docker 和 docker-compose

```bash
# 克隆本仓库至你的电脑（由于启用了 git lfs，需要安装git-lfs进行克隆）
$ git lfs clone https://github.com/shkey/AIEye.git
# 进入本仓库的 deploy 目录
$ cd AIEye/deploy/docker-file
# 运行以下命令进行部署
$ docker-compose up -d
```

如果你是在本地电脑进行部署的，那么就打开浏览器输入 <http://localhost> 进行访问，如果是在云端服务器进行部署的，那么就在浏览器输入你服务器公网 IP 或域名进行访问，查看具体运行效果。

## LICENSE

MIT [@shkey](https://github.com/shkey)
