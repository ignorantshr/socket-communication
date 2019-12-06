[TOC]

## 简介
简单的socket通信，python2.7实现

## 运行环境
centos7
python2.7

## 安装
执行`./install.sh`安装模块

## 运行
进入到对应目录下，开启两个终端，一个运行服务端：`python server.py`，一个运行客户端：`python client.py`。

## 说明
- chatroom可开启多个客户端
- 所有的客户端都可以发送后门字符串`exit_all`来关闭服务端
