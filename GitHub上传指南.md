# GitHub 上传指南

## 📋 准备工作

### 1. 确保已安装 Git

**Windows:**
- 下载：https://git-scm.com/download/win
- 安装后验证：打开PowerShell，输入 `git --version`

**已安装Git可跳过此步骤**

---

## 🚀 上传步骤

### 方法1：使用命令行（推荐）

#### 步骤1：在GitHub创建仓库

1. 访问：https://github.com/new
2. **仓库名：** `MoviePilot-Plugins-MultiVersion`
3. **描述：** MoviePilot多版本下载插件
4. **可见性：** Public（公开）或 Private（私有，推荐）
5. **不要勾选** "Add a README file"（我们已经有了）
6. 点击 **Create repository**

#### 步骤2：上传代码

**打开PowerShell，执行以下命令：**

```powershell
# 1. 进入项目目录
cd E:\AI\MP\MoviePilot-Plugins-MultiVersion

# 2. 初始化Git仓库
git init

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "首次提交：多版本下载插件 v1.0.0"

# 5. 设置主分支名为main
git branch -M main

# 6. 关联远程仓库（替换成你的用户名）
git remote add origin https://github.com/你的用户名/MoviePilot-Plugins-MultiVersion.git

# 7. 推送到GitHub
git push -u origin main
```

**注意：** 
- 将 `你的用户名` 替换成你的GitHub用户名
- 首次推送可能需要输入GitHub用户名和密码/Token

---

### 方法2：使用GitHub Desktop（简单）

#### 步骤1：安装GitHub Desktop

下载：https://desktop.github.com/

#### 步骤2：操作

1. 打开GitHub Desktop
2. 点击 **File** → **Add Local Repository**
3. 选择目录：`E:\AI\MP\MoviePilot-Plugins-MultiVersion`
4. 点击 **Publish repository**
5. 填写仓库名：`MoviePilot-Plugins-MultiVersion`
6. 取消勾选 "Keep this code private"（如果想公开）
7. 点击 **Publish repository**

---

## ⚙️ 在MoviePilot中使用

### 步骤1：获取仓库地址

上传成功后，你的仓库地址为：
```
https://github.com/你的用户名/MoviePilot-Plugins-MultiVersion
```

### 步骤2：在MP中添加插件源

1. 进入MoviePilot Web界面
2. 点击 **设置** → **插件**
3. 找到 **第三方插件仓库**
4. 添加你的仓库地址
5. 保存

### 步骤3：安装插件

1. 进入 **插件** 页面
2. 在插件源下拉菜单中选择你的仓库
3. 找到 **多版本下载** 插件
4. 点击 **安装**

### 步骤4：配置插件

1. 安装完成后，点击插件进入配置
2. ✅ 启用插件
3. ⏱️ 设置延迟时间：`20`秒
4. 📋 勾选需要下载的规则组
5. 保存配置

---

## 🔐 GitHub Token设置（如果需要）

如果推送时提示需要Token：

### 1. 创建Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 设置：
   - Note: `MoviePilot Plugins`
   - Expiration: `No expiration`（或选择有效期）
   - 勾选：`repo`（完整勾选）
4. 点击 **Generate token**
5. **复制Token**（只显示一次！）

### 2. 使用Token推送

```powershell
# 方法1：在推送时输入
# 用户名：你的GitHub用户名
# 密码：粘贴Token

# 方法2：设置远程URL（推荐）
git remote set-url origin https://你的Token@github.com/你的用户名/MoviePilot-Plugins-MultiVersion.git
git push -u origin main
```

---

## 📝 更新插件

### 本地修改后推送到GitHub

```powershell
cd E:\AI\MP\MoviePilot-Plugins-MultiVersion

# 1. 查看修改
git status

# 2. 添加修改
git add .

# 3. 提交
git commit -m "更新说明"

# 4. 推送
git push
```

### MP中更新插件

修改 `package.v2.json` 中的版本号，MP会自动检测更新。

---

## 🎯 验证清单

上传前确认：

- ✅ 目录结构正确
  ```
  MoviePilot-Plugins-MultiVersion/
    ├── plugins.v2/
    │   └── multiversiondownload/
    │       ├── __init__.py
    │       └── README.md
    ├── package.v2.json
    ├── README.md
    └── .gitignore
  ```

- ✅ `package.v2.json` 配置正确
- ✅ 插件文件无语法错误
- ✅ README.md 说明清晰

---

## ❓ 常见问题

### Q: 推送失败，提示 "remote: Support for password authentication was removed"

**A:** GitHub不再支持密码认证，需要使用Token。参考上面的"GitHub Token设置"。

### Q: 私有仓库MP能访问吗？

**A:** 可以，但需要配置GitHub Token。建议使用公开仓库。

### Q: 如何让别人也能用我的插件？

**A:** 分享你的仓库地址，让其他人在MP的第三方插件仓库中添加即可。

---

## 🎉 完成！

上传成功后，你的插件就可以通过MP的插件市场安装了！

**仓库地址示例：**
```
https://github.com/你的用户名/MoviePilot-Plugins-MultiVersion
```

**分享给朋友：**
```
在MP的设置→插件→第三方插件仓库中添加：
https://github.com/你的用户名/MoviePilot-Plugins-MultiVersion
```

---

**祝使用愉快！** 🚀

