# MoviePilot 多版本下载插件 - GitHub上传脚本
# 使用前请先在GitHub创建仓库：https://github.com/new

# ========================================
# 配置区域（请修改）
# ========================================
$GITHUB_USERNAME = "你的GitHub用户名"  # 替换成你的GitHub用户名
$REPO_NAME = "MoviePilot-Plugins-MultiVersion"

# ========================================
# 自动执行（无需修改）
# ========================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "MoviePilot 多版本下载插件 - GitHub上传工具" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已配置用户名
if ($GITHUB_USERNAME -eq "你的GitHub用户名") {
    Write-Host "❌ 错误：请先修改脚本中的 GITHUB_USERNAME" -ForegroundColor Red
    Write-Host ""
    Write-Host "打开文件：上传到GitHub.ps1" -ForegroundColor Yellow
    Write-Host "修改第7行：`$GITHUB_USERNAME = `"你的实际用户名`"" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按Enter键退出"
    exit
}

# 进入项目目录
Write-Host "1. 进入项目目录..." -ForegroundColor Green
Set-Location -Path $PSScriptRoot

# 检查Git是否安装
Write-Host "2. 检查Git安装..." -ForegroundColor Green
try {
    $gitVersion = git --version
    Write-Host "   ✅ Git已安装：$gitVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 错误：未安装Git" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装Git：https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按Enter键退出"
    exit
}

# 初始化Git仓库
Write-Host "3. 初始化Git仓库..." -ForegroundColor Green
if (Test-Path ".git") {
    Write-Host "   ⚠️  已存在.git目录，跳过初始化" -ForegroundColor Yellow
} else {
    git init
    Write-Host "   ✅ Git仓库初始化完成" -ForegroundColor Green
}

# 添加所有文件
Write-Host "4. 添加文件到Git..." -ForegroundColor Green
git add .
Write-Host "   ✅ 文件添加完成" -ForegroundColor Green

# 提交
Write-Host "5. 提交到本地仓库..." -ForegroundColor Green
git commit -m "首次提交：多版本下载插件 v1.0.0"
Write-Host "   ✅ 提交完成" -ForegroundColor Green

# 设置主分支
Write-Host "6. 设置主分支为main..." -ForegroundColor Green
git branch -M main
Write-Host "   ✅ 分支设置完成" -ForegroundColor Green

# 添加远程仓库
Write-Host "7. 关联远程仓库..." -ForegroundColor Green
$remoteUrl = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# 检查是否已有remote
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "   ⚠️  已存在remote，更新URL" -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}
Write-Host "   ✅ 远程仓库：$remoteUrl" -ForegroundColor Green

# 推送到GitHub
Write-Host ""
Write-Host "8. 推送到GitHub..." -ForegroundColor Green
Write-Host "   ⚠️  可能需要输入GitHub用户名和Token" -ForegroundColor Yellow
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✅ 上传成功！" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "仓库地址：" -ForegroundColor Cyan
    Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Cyan
    Write-Host "1. 在MoviePilot中添加此仓库地址" -ForegroundColor White
    Write-Host "   设置 → 插件 → 第三方插件仓库" -ForegroundColor White
    Write-Host "2. 在插件页面安装 '多版本下载' 插件" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "1. 仓库未在GitHub上创建" -ForegroundColor White
    Write-Host "   解决：访问 https://github.com/new 创建仓库" -ForegroundColor White
    Write-Host ""
    Write-Host "2. 需要GitHub Token" -ForegroundColor White
    Write-Host "   解决：访问 https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "   创建Token，推送时使用Token作为密码" -ForegroundColor White
    Write-Host ""
    Write-Host "详细说明请查看：GitHub上传指南.md" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Read-Host "按Enter键退出"

