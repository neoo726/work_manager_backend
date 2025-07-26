#!/bin/bash
# Git历史清理脚本 - 移除敏感信息

echo "🚨 Git历史清理脚本"
echo "此脚本将永久删除git历史中的敏感信息"
echo "请确保已备份仓库！"
echo ""

read -p "是否继续？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
fi

echo "📦 创建备份..."
cd ..
git clone work_manager work_manager_backup_$(date +%Y%m%d_%H%M%S)
cd work_manager

echo "🧹 清理git历史中的敏感文件..."

# 方法1: 使用git filter-branch
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch config.py .env.example' \
  --prune-empty --tag-name-filter cat -- --all

echo "🗑️ 清理引用和垃圾回收..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ 本地清理完成"
echo ""
echo "⚠️ 下一步需要强制推送到远程仓库："
echo "git push origin --force --all"
echo "git push origin --force --tags"
echo ""
echo "🔒 记住要立即更改数据库密码！"
