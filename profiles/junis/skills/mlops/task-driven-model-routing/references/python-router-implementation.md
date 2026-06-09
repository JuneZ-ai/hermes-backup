# Python 路由引擎实现

完整实现位于用户 Windows 目录：`C:\Users\18502\WorkBuddy\model_router.py`

## 核心类结构

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RouteResult:
    model_id: str      # 推荐模型ID
    pool: str          # 所属模型池
    score: int         # 优先级分数
    scene: str         # 匹配到的场景名
    reason: str        # 推理理由
    primary: str       # 首选模型
    secondary: Optional[str] = None
    fallback: Optional[str] = None
    warnings: list = None

class ModelRouter:
    def __init__(self, available_models: set = None):
        """初始化路由引擎"""
    
    def classify_scene(self, task: str) -> tuple:
        """识别任务场景"""
    
    def route(self, task: str) -> RouteResult:
        """主路由方法"""
    
    def check_gaps(self) -> list:
        """检查模型配置差距"""
```

## 路由流程

```
task → classify_scene() → resolve_model() → RouteResult
```

### classify_scene
1. 将任务描述转为小写
2. 遍历 SCENE_KEYWORDS 字典，匹配各场景的关键词列表
3. 返回匹配度最高的场景

### resolve_model
1. 按 primary → secondary → fallback 优先级
2. 检查每个模型是否在 available_models 中
3. 如果全不可用，返回最高分的可用模型
4. 终极保底：deepseek-v4-flash

### scene_keywords 结构

```python
SCENE_KEYWORDS = {
    "复杂代码": {
        "keywords": ["重构", "架构", "系统设计", "复杂代码", ...],
        "primary": "glm-5",
        "secondary": "kimi-k2.6",
        "fallback": "minimax-m2.7",
    },
    "UI截图视觉": {
        "keywords": ["截图", "截图转代码", "设计稿", "UI", ...],
        "primary": "glm-5v-turbo",
        "secondary": "kimi-k2.6",
        "fallback": "kimi-k2.5",
    },
    "长文档分析": {
        "keywords": ["长文档", "PDF分析", "报告分析", ...],
        "primary": "deepseek-v4-flash",
        "secondary": "kimi-k2.6",
        "fallback": "kimi-k2.5",
    },
    # ... 共 8 个场景
}
```

## 与 WorkBuddy models.json 集成

路由引擎的 `available_models` 参数应从 WB 的 `models.json` 提取：

```python
import json

with open("C:/Users/18502/.workbuddy/models.json") as f:
    wb_models_data = json.load(f)

wb_model_ids = {m["id"] for m in wb_models_data}
router = ModelRouter(available_models=wb_model_ids)
```

## 检查差距

```python
gaps = router.check_gaps()
# → [{"model_id": "glm-5v-turbo", "name": "GLM-5V-Turbo (视觉)", ...}]
```

返回推荐但 WB 中未配置的模型列表。
