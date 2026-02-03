# 项目检查Skill (Project Check Skill)

## 描述
用于在添加新模块或文件之前检查项目全局，避免冗余创建。该技能可以扫描整个项目，查找相似的文件、内容或功能，帮助开发者避免重复创建相似的模块或功能。

## 功能特性

### 1. 文件扫描
- **全局扫描**: 扫描项目中所有相关类型的文件
- **模式匹配**: 支持多种文件扩展名的匹配

### 2. 内容搜索
- **关键词搜索**: 在项目文件中搜索指定关键词
- **相似性检测**: 检测与目标内容相似的现有代码

### 3. 冗余检查
- **名称冲突检测**: 检测相似的文件名
- **功能重复检测**: 检测类似的功能实现
- **推荐建议**: 提供是否继续创建的建议

### 4. 报告生成
- **详细报告**: 生成格式化的检查报告
- **匹配详情**: 展示所有匹配项的详细信息

## 使用方法

### 检查项目冗余（推荐用法）
```python
from skills.project_check_skill import check_project_before_creation

# 检查是否应该创建新技能
report = check_project_before_creation('my_new_skill', 'class MyNewSkill')
print(report)
```

### 搜索项目内容
```python
from skills.project_check_skill import scan_project_content

# 搜索项目中的特定内容
results = scan_project_content('class.*Skill')
for file_path, line_num, content in results:
    print(f"{file_path}:{line_num} - {content}")
```

### 查找现有技能
```python
from skills.project_check_skill import find_existing_skills

# 查找项目中已有的技能模块
skills = find_existing_skills()
for skill in skills:
    print(skill)
```

### 使用类方法
```python
from skills.project_check_skill import ProjectCheckSkill

checker = ProjectCheckSkill()
result = checker.check_redundancy_before_creation('my_new_module', 'some_functionality_hint')
report = checker.generate_report(result)
print(report)
```

## 报告解读

检查报告包含以下部分：
- **确切匹配**: 完全匹配提议名称的文件
- **相似名称**: 名称相似的文件
- **相似内容**: 内容相似的代码行
- **存在类似功能**: 实现类似功能的文件
- **建议**: 是否继续创建的建议

## 配置
- **项目根目录**: 默认为 `/home/admin/clawd/daily_stock_analysis`
- **搜索扩展名**: 默认包括 `.py`, `.md`, `.json`, `.txt`, `.cfg`, `.conf`

## 优势
- **避免重复**: 防止创建功能重复的模块
- **提高效率**: 快速定位现有功能
- **保持整洁**: 维护项目的简洁性
- **易于维护**: 减少代码冗余