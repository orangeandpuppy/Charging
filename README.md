![Python 3.9](https://img.shields.io/badge/python-3.9-green.svg)
![React 18.3.2](https://img.shields.io/badge/react-18.3.2-green.svg)

# Charging: Electric Vehicle Charging Station Software
## License
Copyright (C) 此项目为2021 HYSE04小组大作业——电动车珈电站

<img src="figures/logo.png" width="200" height="200">

## 目录

<!--ts-->
- [Charging: Electric Vehicle Charging Station Software](#charging-electric-vehicle-charging-station-software)
  - [License](#license)
  - [目录](#目录)
  - [Git多人协作](#git多人协作)
    - [准备工作](#准备工作)
    - [拉取代码](#拉取代码)
    - [提交代码](#提交代码)
  - [介绍](#介绍)
    - [建模](#建模)
      - [类图](#类图)
      - [用例图](#用例图)
      - [数据建模](#数据建模)
      - [状态转移图](#状态转移图)
  - [项目分工及实现细节](#项目分工及实现细节)
    - [backend/](#backend)
      - [远程连接MySQL模拟服务器端](#远程连接mysql模拟服务器端)
    - [frontend/](#frontend)
  - [环境搭建](#环境搭建)
  - [用法](#用法)
    - [输入格式规范](#输入格式规范)
    - [充电者](#充电者)
    - [管理员](#管理员)
    - [维修员](#维修员)
<!--te-->


## Git多人协作

仓库地址：https://github.com/orangeandpuppy/Charging.git

### 准备工作

在本机上安装Git，然后新建一个文件夹（注意路径里不能出现中文），右键选择Git Bash Here，输入以下命令：
```bash
git init
git remote add Charging https://github.com/orangeandpuppy/Charging.git
```
此时输入
```bash
git remote
```
会显示Charging，说明添加成功。

### 拉取代码

```bash
git pull Charging master
```
这样就将远程仓库的代码拉取到本地了。

(注意：在更改代码前，一定要先拉取代码，以免出现冲突)

### 提交代码

```bash
git add .
git commit -m "update"
git push Charging master
```
这样就将本地的代码提交到远程仓库master分支了。
如果提示分支不一致，可以使用
```bash
git checkout -b master
```
切换到master分支。


## 介绍

### 建模
#### 类图
![类图](figures/class_diagram.png)
#### 用例图
![用例图](figures/use_case.png)
#### 数据建模
![数据建模](figures/data_model.png)
#### 状态转移图
![状态转移图](figures/transitions.png)

## 项目分工及实现细节
- 项目经理：cyx
- 后端开发：cyx,www,sjg
- 前端开发：zzy,yk
- 测试：cyx,www,sjg,zzy,yk
- 文档：cyx,www,sjg,zzy,yk

### backend/

#### 远程连接MySQL模拟服务器端
1. 安装MySQL  
2. 命令行模式配置MySQL  
- 输入密码，进入MySQL
```angular2html
mysql -u root -p
```
- 创建数据库charging_db,用于存储该项目数据
```angular2html
create database charging_db;
use charging_db;
```
- 创建一个用户remote_connect,密码为123456,用于远程操作该数据库，并赋予charging_db的所有权限
```angular2html
create user 'remote_connect'@'%' identified by '123456';
grant all privileges on charging_db.* to 'remote_connect'@'%';
flush privileges;
```
3. 配置服务器端ip地址  
由于个人电脑ip地址被NAT设备屏蔽后只能看到私有ip地址，该ip地址可能会变化，需要使用内网穿透工具，如贝瑞花生壳  
将本地ip地址映射到公网上，使用该公网ip地址访问服务器端  
配置流程略  

4. 用pymysql连接远程数据库  
安全起见不把remote_connect的密码放在README里了


### frontend/
[yk,zzy]

创建React项目
```
npx create-react-app frontend
```

## 环境搭建

1. 我们建议使用Python 3.9版本，并且强烈建议使用conda进行环境管理。
```
conda create -n Charging python=3.9
conda activate Charging
```
2. 安装依赖
```
pip install -r requirements.txt
```

3.前端需要安装node,npm等工具
node=16.20.2
npm=8.19.4
其他配置见frontend\package.json文件

## 用法

方便测试方使用，暂定

### 输入格式规范
电动车编号格式: 充电站字母（G/X/F）+ 4位数字（0001-9999）(例如：G0001)  
充电桩编号格式: 充电站字母/充电口颜色（R或B）-两位数字 (例如: F/R-01)

### 充电者

### 管理员

### 维修员
