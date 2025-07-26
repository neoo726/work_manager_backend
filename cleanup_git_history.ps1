# Git历史清理脚本 - PowerShell版本
# 移除git历史中的敏感信息

Write-Host "🚨 Git历史清理脚本" -ForegroundColor Red
Write-Host "此脚本将永久删除git历史中的敏感信息" -ForegroundColor Yellow
Write-Host "请确保已备份仓库！" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "是否继续？(y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "操作已取消" -ForegroundColor Green
    exit
}

Write-Host "📦 创建备份..." -ForegroundColor Blue
$backupName = "work_manager_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Set-Location ..
git clone work_manager $backupName
Set-Location work_manager

Write-Host "🧹 清理git历史中的敏感文件..." -ForegroundColor Blue

# 使用git filter-branch清理历史
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch config.py .env.example" --prune-empty --tag-name-filter cat -- --all

Write-Host "🗑️ 清理引用和垃圾回收..." -ForegroundColor Blue
Remove-Item -Recurse -Force .git/refs/original/ -ErrorAction SilentlyContinue
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "✅ 本地清理完成" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️ 下一步需要强制推送到远程仓库：" -ForegroundColor Yellow
Write-Host "git push origin --force --all" -ForegroundColor Cyan
Write-Host "git push origin --force --tags" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔒 记住要立即更改数据库密码！" -ForegroundColor Red
