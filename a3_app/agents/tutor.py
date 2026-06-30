import json
import re
from agents.base import BaseAgent

class TutorAgent(BaseAgent):
    name = "辅导Agent"
    description = "提供多模态答疑和个性化学习建议"
    
    system_prompt = """你是一位专业的学习辅导老师。请针对用户的问题，提供详细、易懂的解答。

回答要求：
1. 先给出核心概念定义
2. 用生活类比帮助理解
3. 提供公式或代码示例（如果适用）
4. 列出相关知识点
5. 给出练习建议

输出格式要求：
必须返回JSON格式，包含以下字段：
- reply: 详细解答内容（markdown格式）
- exercises: 练习题列表（可选，每项包含title、count、difficulty）
- related_topics: 相关主题列表（字符串数组）"""

    knowledge_base = {
        "链式|chain|复合函数求导": {
            "reply": """**链式法则**本质是"函数的函数"求导方法。

🧮 数学表达：如果 y = f(g(x))，那么 dy/dx = f'(g(x)) · g'(x)

💡 生活类比：就像剥洋葱——从外到内一层层剥开，每层求导后相乘。

📌 示例：y = sin(x² + 1) 的导数
→ 外层 sin → cos(x² + 1)
→ 内层 x² + 1 → 2x
→ 结果：cos(x² + 1) · 2x""",
            "exercises": [{"title": "链式法则专项练习", "count": 3, "difficulty": "中等"}],
            "related": ["复合函数求导", "高阶导数"]
        },
        "梯度下降|gradient|优化器": {
            "reply": """**梯度下降**是机器学习最核心的优化算法。

🔑 核心思想：沿损失函数下降最快的方向（负梯度方向）迭代更新参数。

📐 更新公式：θ_new = θ_old - α · ∇J(θ)

⚙️ 三种变体：
• **BGD**（全量）：稳定但慢，大数据集不适用
• **SGD**（随机）：快速收敛，但震荡大
• **Mini-batch**：折中方案，深度学习标配

💡 学习率 α 是关键超参数——推荐从 0.01 开始试""",
            "exercises": [],
            "related": ["损失函数", "学习率调优", "随机梯度下降", "Adam优化器"]
        },
        "正则化|regularization|l1|l2|过拟合": {
            "reply": """**正则化**用来防止过拟合——模型在训练集上表现好但在测试集上表现差。

📊 L1 正则化（Lasso）：
• 在损失函数后加 λ·Σ|w|
• 产生稀疏解 → 自动特征选择
• 适合特征很多但只有少数重要的场景

📊 L2 正则化（Ridge）：
• 在损失函数后加 λ·Σw²
• 使所有权重均匀缩小 → 更稳定
• 通常项目中先用 L2 试试

🎯 ElasticNet = L1 + L2 的组合，兼顾两者优点""",
            "exercises": [],
            "related": ["过拟合vs欠拟合", "交叉验证", "dropout", "数据增强"]
        },
        "sigmoid|逻辑回归|logistic|分类": {
            "reply": """**逻辑回归**虽然名字带"回归"，但实际上是分类算法（名字是历史遗留问题 😅）。

📐 核心公式：P(y=1|x) = σ(wx+b) = 1/(1+e^-(wx+b))

🎯 Sigmoid 函数将任意实数映射到 (0,1) 区间，天然适合做概率估计。

📌 三步走：
1. 线性组合 wx + b
2. 过 sigmoid → 得到概率值
3. 设阈值（通常 0.5）→ 判为正/负类

💻 sklearn 一行代码：
`from sklearn.linear_model import LogisticRegression`""",
            "exercises": [{"title": "逻辑回归习题", "count": 5, "difficulty": "中等"}],
            "related": ["sigmoid函数", "二分类", "多分类softmax", "混淆矩阵"]
        },
        "决策树|decision tree|cart|信息增益|基尼": {
            "reply": """**决策树**是直观易懂的白盒模型，模拟人类"if-then"决策过程。

🌲 构建步骤：
1. 选择最优特征进行分裂 → 用什么指标？
2. 递归分割直到停止 → 什么时候停？

📊 分裂指标：
• **信息增益**（ID3）：IG = H(父) - Σ(w_i × H(子))
• **增益率**（C4.5）：解决信息增益偏向多值特征的问题
• **基尼指数**（CART）：sklearn默认，计算更高效

🛑 停止条件：
• max_depth（常用 3~6）
• min_samples_split（节点最少样本数）
• min_samples_leaf（叶节点最少样本数）""",
            "exercises": [],
            "related": ["随机森林", "GBDT", "XGBoost", "特征重要性"]
        },
        "交叉验证|cross validation|k-fold": {
            "reply": """**交叉验证**是评估模型泛化能力的金标准。

🔁 K-fold 流程：
1. 将数据分成 K 等份
2. 每次用 K-1 份训练、1 份验证
3. 轮换 K 次，取平均值

📊 推荐参数：
• K = 5 或 10（最常用）
• 分类任务用 StratifiedKFold 保持类别分布
• 时间序列用 TimeSeriesSplit

⚠️ 注意：不要在 CV 前做特征选择——会数据泄露！""",
            "exercises": [],
            "related": ["过拟合检测", "模型选择", "超参数调优", "bootstrap"]
        },
        "神经网络|neural network|深度学习": {
            "reply": """**神经网络**模拟人脑神经元的工作方式。

🧠 基本结构：输入层 → 隐藏层 → 输出层

📐 前向传播：a^(l+1) = σ(W^(l)·a^(l) + b^(l))

🎯 训练三部曲：
1. **前向传播**：计算预测值
2. **计算损失**：与真实值比较
3. **反向传播**：链式法则求梯度，更新参数

📌 激活函数选择：
• ReLU → 隐藏层首选（简单快速）
• Sigmoid → 二分类输出层
• Softmax → 多分类输出层""",
            "exercises": [],
            "related": ["反向传播", "激活函数", "CNN", "RNN"]
        },
    }

    def _mock_llm(self, prompt: str) -> str:
        return json.dumps({
            "reply": f"""关于「{prompt}」这个问题：

我建议从以下几个角度入手理解：

1. **先掌握基础概念**：确保理解核心定义，建议查阅讲义中的相关章节
2. **动手写代码**：用 sklearn / PyTorch 实现一个简单demo，代码是最好的老师
3. **对比学习**：与相似概念做对比，找出异同

需要我生成这个主题的学习资源吗？或者先做几道练习巩固一下？""",
            "exercises": [],
            "related_topics": []
        })

    def _match_knowledge(self, question: str) -> dict | None:
        for pattern, data in self.knowledge_base.items():
            if re.search(pattern, question, re.IGNORECASE):
                return data
        return None

    async def answer_question(self, question: str, context: str = "") -> dict:
        matched = self._match_knowledge(question)
        if matched:
            return {
                "reply": matched["reply"],
                "extra_exercises": matched.get("exercises", []),
                "related_topics": matched.get("related", [])
            }

        prompt = f"""请详细解答以下学习问题：

问题：{question}

上下文（如果有）：{context}

请按照系统提示词要求的JSON格式输出。"""
        
        result = self._call_llm(prompt)
        try:
            llm_result = json.loads(result)
            return {
                "reply": llm_result.get("reply", ""),
                "extra_exercises": llm_result.get("exercises", []),
                "related_topics": llm_result.get("related_topics", [])
            }
        except json.JSONDecodeError:
            mock_result = json.loads(self._mock_llm(question))
            return {
                "reply": mock_result.get("reply", ""),
                "extra_exercises": mock_result.get("exercises", []),
                "related_topics": mock_result.get("related_topics", [])
            }

    async def generate_report(self, stats: dict) -> str:
        hours = stats.get("today_hours", 0)
        accuracy = stats.get("accuracy", 0)
        streak = stats.get("streak_days", 0)
        resources = stats.get("resources_completed", 0)

        prompt = f"""请根据以下学习统计数据生成一份友好的学习报告：

今日学习时长：{hours}小时
练习正确率：{accuracy}%
连续学习天数：{streak}天
已完成资源数：{resources}个

请生成一份鼓励性的学习总结报告，包含今日表现评价和明日建议。"""
        
        result = self._call_llm(prompt)
        try:
            llm_result = json.loads(result)
            return llm_result.get("reply", "")
        except json.JSONDecodeError:
            lines = ["📊 **今日学习总结**", ""]

            if hours >= 2:
                lines.append(f"✅ 学习时长 {hours}h，达到目标！")
            elif hours > 0:
                lines.append(f"📝 学习时长 {hours}h，建议明天增加到 2h")
            else:
                lines.append("📝 今天还没有学习记录，现在开始吧！")

            if accuracy >= 80:
                lines.append(f"✅ 练习正确率 {accuracy}%，表现优秀")
            elif accuracy >= 60:
                lines.append(f"⚠️ 练习正确率 {accuracy}%，建议回顾错题")
            else:
                lines.append(f"🔴 正确率偏低（{accuracy}%），需要加强基础概念理解")

            if streak >= 7:
                lines.append(f"🔥 连续学习 {streak} 天！保持这个节奏")

            lines.append("")
            lines.append("💡 **明日建议**：")
            lines.append("1. 花15分钟复习今天内容")
            lines.append("2. 学习新章节（预计45分钟）")
            lines.append("3. 完成3-5道练习题巩固")
            lines.append("")
            lines.append("加油 💪")

            return "\n".join(lines)

    async def process(self, user_input: str, context: dict = None) -> dict:
        return await self.answer_question(user_input, json.dumps(context or {}))
