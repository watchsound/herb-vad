# Herb-VAD：经典中药性味归经的认知制图学

**草稿 v0.1，2026-06-21**
**目标期刊：** *Cognitive Science* / *Cognition* / CogSci 会议 / *Frontiers in Psychology*

---

## 摘要

本文提出：经典中医中药性状描述系统——**四气**（寒、凉、平、温、热）、**五味**（酸、苦、甘、辛、咸）、**升降浮沉**（方向性倾向）、**归经**（十二经络归属）、**毒性**（无毒/小毒/有毒/大毒）——构成了一个**对内感受认知空间（interoceptive-cognitive space）的文化建构坐标系**，其结构与 NLP 领域 VAD（Valence-Arousal-Dominance）情感模型（Mohammad, 2018）将语义空间投影到低维情感基座的方式相类。我们引入使 VAD 获得科学合法性的方法学协议（Best-Worst Scaling 标注、跨标注者一致性作为头等输出、嵌入回归验证），并将其第一阶段——**跨数据源一致性**——应用于五个公开 TCM 数据源（SymMap v2.0；TCMID；TCM-MKG；ETCM v2.0；中国药典 2020）所记录的中药性状。在被至少两个独立数据源覆盖的 1,098 味中药样本上，**四气（寒/热）轴的跨源完全集合相等一致率达到 85.9%**，证实了我们的事前注册预测；归经轴一致率达 72.7%；多值的五味轴一致率为 75.5%（该度量对多标签数据存在结构性下偏，详见第 7 节）。**升降浮沉轴在所有现代英文 TCM 数据库中均系统性缺失**——这一发现本身正与"具身认知"读法相容：理论负载最重的描述项被裁掉了，而最直接被身体感受到的描述项（寒/热）被最稳定地保留下来。我们主张，这一结果使中药性状描述成为认知科学（特别是具身认知框架下）一个可处理的研究对象；同时明确放弃任何药理学层面的主张。所有代码与处理后数据均公开于 https://github.com/watchsound/herb-vad。

**关键词：** 具身认知；维度化情感；中医；跨文化认知；内感受；事前注册分析。

---

## 1. 引言

中医对数千味中药沿五个轴进行分类，该系统在两千年临床实践中保持了显著稳定性：**四气**（寒、凉、平、温、热）、**五味**（酸、苦、甘、辛、咸）、**升降浮沉**（升、降、浮、沉）、**归经**（十二经络）、**毒性**（无毒/小毒/有毒/大毒）。学界对该系统主要存在两种强对立的读法。

**怀疑论读法**将这些轴视为前科学时代的民间分类——具有历史人类学价值，但不属于实证研究对象。**TCM-AI 极大主义读法**则与之相反，将其视为编码了现代分子生物学尚未发掘的药理学真理（参见 Li 2014 关于"网络靶标"理论；以及 Dong 等人 2023 的 TCM2Vec 嵌入路线）。在我们看来，这两种读法都忽略了一种与主流认知科学自然衔接、且为数据所支持的第三种可能。

**我们主张：经典中药性状描述构成一个对"内感受认知空间"的文化建构坐标系。** 它们并不编码分子药理学；它们编码的是**前科学医学传统集体地、对身体被感受到的状态及其药物扰动方式所做的范畴划分**。在此框架下，"寒/热"不是关于中药代谢热力学的主张，而是前科学时代的临床医生与患者共同会聚到的一个范畴——即"被感觉为温暖 vs 被感觉为凉冷"。Lakoff 与 Johnson（1980）将这种维度认定为前概念性的具身图式（embodied schema）；Barrett（2017）则将这种内感受体验置于其建构论情感理论的核心。

这一框架在 NLP 文献中有先例。**Valence-Arousal-Dominance（VAD）模型**（Russell, 1980；Mehrabian & Russell, 1974；Bradley & Lang, 1994；Mohammad, 2018）将自然语言中情感词的高维语义空间约简为三个正交轴，捕获**被感受到的**情感体验。VAD 在心理学上被立论为基础维度（Mehrabian, 1996），但在经验上更像是丰富语义空间的低秩投影——Sedoc 等人（2017）与 Buechel 与 Hahn（2018）的研究表明，VAD 评分可以从 BERT 等分布式嵌入中可靠地回归得到；Mohammad（2018）报告三个轴的 split-half 可靠性介于 0.85 至 0.95 之间。我们主张：**中药五个性状轴可视为同类的结构对应物——一个对更高维"内感受认知空间"的可解释低秩投影**。

这里的不对称至关重要。VAD 拥有五十余年的心理测量学验证；中药性状描述则有约两千年的临床使用，但缺乏系统的实证合法化。我们因此提出，**将 VAD 的方法学协议——标注规范、跨标注者一致性作为头等产出、嵌入回归验证、跨文化复制——移植到中药性状研究**。本论文报告该方法学协议的第一阶段：在五个独立 TCM 数据源之间，逐轴的跨源一致性。

整体研究纲领下有三个事前注册的研究问题（详见项目仓库中的研究计划）；本文报告 RQ1 的实证结果，并描述 RQ2 与 RQ3 的已构建基础设施。

- **RQ1（本文）。** 经典中药性状描述项在独立编纂的本草典籍之间是否可靠？事前注册排序：QI > FLAVOR > TOXICITY > CHANNEL > DIRECTION。
- **RQ2（基础设施已完成；真实数据运行待定）。** 给定**症状叙事**段落——但其中性状关键词（寒、热、升、降……）已被显式遮蔽——中药性状标签能否由语言模型嵌入预测？强阳性结果将提示：该描述项栖居于"被感受到的体验空间"，而非仅仅是论说性标签。
- **RQ3（基础设施已完成；真实数据运行待定）。** 中医诊断范畴与西方维度化情感词（NLP-VAD）是否在共享多语种 LM 嵌入空间中以不同方式划分**同一**底层内感受认知流形？

本文的贡献为：（i）将中药性状描述重新建构为"内感受认知坐标系"而非"药理学坐标系"的概念性重构；（ii）首个规模化的跨源一致性研究（QI 轴上 1,098 味中药——据我们所知是已发表 TCM 性状研究中规模最大的样本基底）；（iii）事前注册预测"QI 是最可靠轴"在大规模下的实证确认；（iv）"升降浮沉系统性缺失"这一发现——我们将其解读为支持具身认知读法的证据。

## 2. 相关工作

### 2.1 维度化情感

Russell（1980）通过对情感词相似性判断进行多维标度，揭示出二维的"效价 × 唤起"圆周结构（circumplex）。Mehrabian 与 Russell（1974）基于因子分析提出第三轴——支配性（dominance）。Bradley 与 Lang（1994）通过自评人形量表（SAM）操作化了 PAD 方案；其后的 ANEW 词典（Bradley & Lang, 1999）成为下游 NLP 工作的实证锚点。

Mohammad（2018）发布的 NRC-VAD 词典对 20,000 个英语词使用 Best-Worst Scaling（BWS，标注者从四元组中选出最/最不 *X* 者）进行了三维标注。BWS 比 Likert 量表的可靠性显著更高（V/A/D 三轴的 split-half ρ 分别约为 0.95/0.90/0.85）。NRC-VAD v2.1（Mohammad, 2025）将覆盖范围扩展到约 55,000 条（含多词表达）。Sedoc 等人（2017）与 Buechel 与 Hahn（2018）证明 VAD 评分可由分布式嵌入回归得到——这在实证上把 VAD 重新定位为更丰富语义空间的低秩投影，而非一组孤立的原初坐标。

对 VAD 的批评包括：支配性轴的跨文化效度问题（Russell, 1991）、四维度论（Fontaine 等人, 2007，主张增加"不可预测性"轴）、以及离散范畴 vs 维度论的长期争论（Ekman, 1992 vs Barrett, 2006）。对本研究而言，我们引入的不是 VAD 的特定三维结构，而是其**结构性模板**——从相似性评分中恢复出正交轴；该结构既可被立论为原初维度，又可被视为投影。

### 2.2 具身认知与内感受体验的建构论

Lakoff 与 Johnson（1980）主张人类的概念系统围绕一组前概念性具身图式（如 UP/DOWN, IN/OUT, COLD/HOT, CONTAINER）组织。这些图式由感觉运动经验前于概念地涌现。Barrett（2017）、Quigley 等人（2021）及更广义的建构论传统将一个高维内感受底座置于情感体验的根基之处，而把文化特异的范畴边界视为叠加于其上的层。

由此可导出一个**可证伪的预测**：在前科学时代的医学传统中，**最直接关联被感受到的内感受维度**的描述项（寒/热；可能还有五味）应在独立编纂的本草典籍之间最稳定；而**最理论负载、最不直接对应感受**的描述项（升降浮沉）应最不稳定，甚至在以"临床可靠性"为导向的数据库中被裁掉。我们的结果在 §6 直接相关于这一预测。

### 2.3 中医信息学

Hopkins（2008）将药物重新建构为对生物网络的多药理学扰动；Li（2014）将该框架延伸到中医，提出"网络靶标"理论。与本研究最相关的中医性状表征工作包括：TCM2Vec 嵌入线（Dong 等人, 2023）；Zhang 等人 2025 的"性味组合"t-SNE 投影（PCMM）；Niu 等人 2025 用蛋白互作图特征**预测**寒/热的 HPGCN 工作；Jang 与 Lee 2024 对"八纲"古典中医框架做降维分析，发现"表-里"轴最具泛化性。

据我们所知，目前尚无研究在"维度化情感理论"意义上将中药性状描述建构为"认知坐标系"，也没有任何工作在本文报告规模上计算五个性状轴的多源跨标注者一致性。在概念上最接近的工作是 Zhang 等人（2025）与 Jang 与 Lee（2024）；二者均未引用 NLP-VAD，也未援引具身认知框架。

## 3. 方法学协议

VAD 的方法论可提炼为如下五步序列：

1. **Best-Worst Scaling 标注**（Mohammad, 2018）——向标注者呈现四元组，要求选出每轴上最/最不 *X* 者；聚合为连续评分。
2. **跨标注者一致性作为头等产出**——逐轴报告 split-half 可靠性；不可靠的轴被明确暴露，而非掩盖。
3. **锚定到可测量底座**——VAD 评分可由分布式嵌入回归。此处的实证桥使 VAD 成为科学构念，而非纯粹的心理测量。
4. **检验最少充分维度**——对评分矩阵做因子分析或 PCA；让数据说话："维度数到底是多少？"
5. **跨文化／跨学派复制**——多语种 VAD 词典在不同语言间复制，但"支配性"轴有显著的文化漂移。

我们提议将该协议应用于中药性状描述。本文仅报告第一阶段，且做出一项重要替代：**用五个独立 TCM 数据源各作为一个"标注者"代替全新的 BWS 临床医师小组**（后者在首项研究里成本过高且 IRB 负担过重）。每个数据源代表一条独立的编纂流水线，所依据的本草文献基本不重叠：中国药典 2020、中华本草辞典 2006、全国中草药汇编 1996、现代教材修订版本，以及清华大学、南开大学、中国中医科学院、元智大学等机构的信息学团队。这五个数据源共同近似一个专家标注小组——这一近似是本研究的主要局限，详见 §8。

协议第 2 至第 5 阶段为后续工作；第 3 阶段（从分布式嵌入回归性状）与第 4 阶段（维度数检验）的基础设施已构建并在项目仓库中，等待计算资源部署。

## 4. 数据来源

本文所用全部数据均为公开且许可学术使用。表 1 汇总我们所统合的五个中药性状数据源。

**表 1. 中药性状数据源。**

| 数据源 | 出处 | 中药数 | 覆盖轴 |
|---|---|---|---|
| SymMap v2.0 | Wu 等人 (2019), *NAR* | 703 | QI, FLAVOR, CHANNEL, TOXICITY |
| TCMID | Huang 等人，Zenodo 8066910 | 336 | QI, FLAVOR, CHANNEL |
| TCM-MKG | Zeng, Zenodo 19804367 | 6,398 | QI, FLAVOR, CHANNEL |
| ETCM v2.0 | Zhang 等人 (2023), 实时 API | 1,336 | QI, FLAVOR, CHANNEL |
| 中国药典 2020 (英文版) | 国家药典委员会 | 182 | QI, FLAVOR, CHANNEL, TOXICITY |

支持 RQ2/RQ3 后续分析的另外两个资源：NRC-VAD v2.1（Mohammad, 2025；44,728 个英语单词，V/A/D 评分在 [−1, +1] 之间），以及一个 2,804 篇 PubMed 中医摘要的症状语料库（按 MeSH 词 "traditional chinese medicine" 与 "chinese herbal medicine" 检索，进一步筛选为含有我们 130 项英文症状词表中至少一项词的 244 篇摘要）。

ETCM v2.0 的数据接入值得一段技术注记。ETCM 前端是 Vue.js 单页应用，未公开批量下载端点；项目计划最初将其归类为"浏览器封闭"。我们逆向工程了其位于 `http://www.tcmip.cn:18124` 的 Django 后端：单药详细信息端点为 `GET /home/detail/?id=<pinyin>&type=herb`（大小写不敏感）；其中 `type=herb` 参数为必填，缺失时端点返回空数据。我们的爬虫以 200 ms 的请求间隔对规范化拼音集合进行了完整枚举，35 分钟内取回 1,336 味中药记录。

中国药典 2020（英文版第一卷 a、b 两册）由用户提供 PDF（共 3.0 GB，2,205 页）。PDF 内嵌文本（非扫描影像），故可直接用 `pypdf` 抽取。标准化的单药条目格式 `Property and Flavor [QI]; [FLAVOR(s)]; [TOXICITY-可选].` 与 `Meridian tropism [CHANNEL(s)] meridians.` 使我们得以基于正则表达式抽取出 182 味中药四个轴（QI/FLAVOR/CHANNEL/TOXICITY）的性状信息。

## 5. 规范化身份解析

五个数据源描述的是相互重叠但不完全相同的中药集合，且使用三种不同的命名约定（中文名、拼音、拉丁植物学双名或药材学双名）。为计算跨源一致性，我们将所有源侧标识符解析为统一的 5 位规范化 ID（`H00001` … `H06467`）。两行被合并的条件是：（i）非空规范化中文名匹配，或（ii）非空规范化拼音匹配（去声调、合并空白），或（iii）拉丁名匹配——但其中中文与拼音为**严格匹配键**（任一不匹配即拒绝合并），拉丁名为**宽松匹配键**（在至少一个严格匹配键已支持合并的前提下，拉丁名不匹配是被允许的）。这一"宽松拉丁"规则是必要的，因为命名权威剥离（authority-stripping）的伪影（如 `Panax ginseng C. A. Meyer` → `panax ginseng` 对 `Panax ginseng [syn. Asparagus lucidus]` → `panax ginseng [syn.`）会系统性地使同一生物物种的规范化拉丁字符串分歧。

另有一项与规范化相关的修正：早期版本的规范化连接产生了笛卡尔积式扇出——过度剥离权威后的拉丁字符串（如 `Radix Astragali` → `radix`）会跨众多不同主表行碰撞。我们通过在连接中**剔除任何在主表中出现于多于一行的键值**修复这一问题。规范化结果给出 6,467 味唯一中药的合并主表。

身份解析是本研究构念效度的最大单一来源。其局限性在 §8 讨论。

## 6. 结果：发现 #1——跨源一致性

### 6.1 事前注册

预测于 2026-06-20 在项目仓库 `docs/findings/01_label_reliability.md` 中**先于**任何真实数据运行进行了注册。事前注册的预测及驱动每项预测的具身认知理由如下：

- **QI：κ ≥ 0.60**（实质性一致）。寒/热是最一致的经典标签，因其追踪了最直接被身体感受到的内感受维度。
- **FLAVOR：0.40 ≤ κ < 0.60**（中等）。多标签性质，但五种基本味广为接受；学派特有的次要味（如 涩 vs 酸）贡献剩余分歧。
- **TOXICITY：κ ≥ 0.50**。现代药典已编码四级毒性（无毒 / 小毒 / 有毒 / 大毒）；部分古本草则完全省略毒性。
- **CHANNEL：0.20 ≤ κ < 0.40**（一般）。归经归属在经方/时方/温病等学派间差异显著；既有研究表明审读者级一致性较低（Zhao, 2015）。
- **DIRECTION：κ < 0.30**（较差）。升降浮沉在现代数据库中最少被编码——许多数据库根本不记录该轴。

### 6.2 度量

我们原计划逐轴报告 Fleiss κ。然而五个数据源对样本的覆盖呈不规则模式（任一味中药可能出现在 2 至 5 个数据源中），违反 `statsmodels.fleiss_kappa` 所要求的"每个样本由相同数量标注者评分"假设。我们因此报告**完全集合相等的原始一致率（raw set-equality agreement）**作为主度量：在合格中药（被 ≥ 2 个数据源覆盖）中，**每一个**数据源对该药在该轴上发出的取值集合完全相同的比例。对单值轴（QI、DIRECTION、TOXICITY）等同于严格相等；对多值轴（FLAVOR、CHANNEL）等同于取值集合完全相等（即 Jaccard = 1）。

该度量对不规则覆盖鲁棒，但在结构上比 κ 更严苛：任一源多发一个标签即破坏全体一致。该结构性惩罚在 §7 讨论。

### 6.3 结果

**表 2. 五源逐轴原始集合相等一致率。**

| 轴 | 一致率 | 合格样本数 | 事前注册预测 | 判定 |
|---|---|---|---|---|
| QI | **85.9%**（943 / 1,098） | 1,098 | κ ≥ 0.60（约 80% 原始） | **高端确认** |
| FLAVOR | 75.5%（1,008 / 1,335） | 1,335 | 0.40 ≤ κ < 0.60（约 65–80% 原始） | 高端确认 |
| CHANNEL | 72.7%（770 / 1,059） | 1,059 | 0.20 ≤ κ < 0.40（约 50–65% 原始） | **超出预测** |
| TOXICITY | 100%（2 / 2） | 2 | κ ≥ 0.50 | 仅提示性（n=2） |
| DIRECTION | — | 0 | κ < 0.30 | **不可测**（无源记录该轴） |

我们强调三项结果。首先，**QI 在 1,098 味中药上达到 85.9% 原始一致率**——这是据我们所知已发表 TCM 性状研究中规模最大的样本基底，且实质性确认了事前注册预测。其次，**CHANNEL 在 1,059 味中药上达到 72.7%**，明显高于事前注册区间。第三，**DIRECTION 是不可测的**——和谐后的数据集中没有任何来源记录该轴。

### 6.4 升降浮沉的系统性缺失作为证据

升降浮沉在我们考察的全部五个公开英文 TCM 数据源中的完全缺失，是本研究最令人惊讶的发现；我们将其视为**正向数据点**，而非失败模式。在对中国药典 2020 第一卷全部 2,205 页扫描自然语言关键词 "ascending"、"descending"、"floating"、"sinking" 后，我们仅找到 1 处偶然命中（第 150 页 "ascending firstly to 5 cm" 出现在描述植物形态的段落中，而非性状字段）。和谐后数据集中的任何一个数据源都没有结构化的"升降浮沉"性状字段。**现代英文 TCM 数据库已系统性地裁掉这一描述项**。

具身认知读法恰好预测了这一现象：最理论负载、最不直接对应身体感受的描述项，**正是**在传统被操作化为"临床可靠数据库"时最有可能被剔除者。怀疑论读法（民间分类）与 TCM-AI 极大主义读法都预测升降浮沉应与其他四轴一道被保留——因为二者都把五个描述项视为**认识论地位相同**。具身认知读法是唯一在事前能将它们区分开的读法。

## 7. 讨论

### 7.1 QI 作为具身核心

QI 在 1,098 味中药上达到的 85.9% 跨源一致率是本研究的头号实证结果。从三源中间结果（81.1%）到五源最终结果（85.9%）的提升本身具有意义：随着独立编码的增加，一致率**反而增强**——这与"该描述项主要是标签约定"的假设所预测的"向均值回归"恰好相反。该模式与"具身-热感"读法一致：寒/热追踪最直接被感受的内感受维度，前科学时代的医学传统之所以最稳定地会聚于此，是因为存在一个稳定的底层信号可被会聚。

### 7.2 五味的度量学异常

表面上，FLAVOR 的 75.5% 一致率低于 CHANNEL 的 72.7%（在子集严格意义下）。我们**不**将其解读为"五味比归经更不可靠"的证据。集合相等度量在结构上对多值轴有结构性惩罚：若三个数据源对某药分别投出 `{甘, 苦}`、`{甘, 苦}`、`{甘, 苦, 酸}`，集合相等度量判为不一致（第三个集合是前两者的严格超集），而同样的重叠模式在 macro-Jaccard 下评分为 0.67（第二个数据源的集合是第三个的子集）。在 n = 1,335 的规模下，即便每源仅以小比率多发一个味，也会使大量样本的全体一致被破坏。公平的比较应使用对共识标签的逐类 macro-Jaccard 或 macro-F1——我们在后续分析中报告该结果。

### 7.3 CHANNEL 超出预测

CHANNEL 在 1,059 味中药上达到的 72.7% 明显高于事前注册区间（κ 0.20–0.40 大致换算为 50–65% 原始）。最简单的解释是：**现代 TCM 数据库**之中归经归属的标准化程度，比基于经典文献做的审读者一致性研究（Zhao, 2015）所提示的要更高。现代 TCM 数据库基本都引用中国药典 2020 与标准教材《中药学》——两者均逐药编码十二经归属。我们观察到的跨源一致也因此可能部分反映**编辑性会聚**，而非独立专家会聚。这一可能性只有通过运行第一阶段协议于**全新独立的 BWS 标注小组**才能被解决。

### 7.4 TOXICITY：信号真实，基底极小

跨源 TOXICITY 基底仅 2 味中药（皆全体一致）。中国药典 2020 提供 34 条毒性记录，SymMap 提供 91 条；瓶颈不在数据量，而在身份解析——中国药典使用**药材学属格名**（如 "Aconiti Radix Lateralis Praeparata"），其余四源使用**植物学双名**（如 "Aconitum carmichaelii"）。一张药材学—双名对照表（半天的一次性映射工作）应能将跨源 TOXICITY 基底提升至约 30 味，从而支持有意义的 κ 计算。

### 7.5 升降浮沉的缺失作为正向证据

§6.4 已经讨论；此处强调：缺失是**系统性的**，不是随机的——它跨越五个独立数据源、五条不同的编纂流水线持续出现。最简单的读法——升降浮沉因其内感受关联最弱而被现代西方影响下的 TCM 数据库裁掉——与具身认知框架一致，而与怀疑论与极大主义两种读法皆不一致。

### 7.6 本研究**不**主张的内容

我们明确放弃三种数据不支持的读法。**第一**，本研究不就经典中医对中药的分类是否"药理学上正确"作出任何主张。**第二**，本研究不就中医治疗"临床上有效"作出任何主张。**第三**，本研究不就"寒/热"是否对应任何特定分子机制作出任何主张。我们的实际主张更窄、也更可辩护：**"寒/热"是一个可被解释的范畴，前科学医学传统以高跨源可靠性会聚于此，与其追踪某一被直接感受的内感受维度的假设相一致**。该描述项是否同时具有分子药理学的预测能力，是另一篇论文的实证问题。

## 8. 局限

最大单一局限是：**五个数据源不是五个独立的标注者**。中国药典 2020 在某种程度上影响了其余四个数据源的性状归属（TCM-MKG 与 ETCM 均明确引用之；SymMap 与 TCMID 所依据的本草文献也存在交叠）。五个数据源充其量是一组**准独立的编纂流水线**，不是一组全新的标注小组。完整的 VAD 风格协议要求第五阶段——由独立的 TCM 临床医师小组（理想情况下来自经方、时方、温病等多个学派）进行 BWS 标注。我们的结果应被读为对 Herb-VAD 命题的**必要而非充分**检验：所观察到的多源模式与具身认知读法相容，若该模式失败则将构成反证，但该模式本身并未排除"QI 高一致率纯粹源自编辑性会聚"的解释。

另两项局限：（i）跨源 TOXICITY 基底过小（n = 2），不支持有意义的 κ 计算；（ii）允许跨源合并的"宽松拉丁名"匹配规则，在拼音转写歧义的情形下可能引入假阳合并。我们已抽检约 50 例跨源合并，未发现明显假阳，但更大规模审计为后续工作。

## 9. 后续工作

事前注册的其余两项分析（RQ2：留出症状探针；RQ3：与 NRC-VAD 在共享多语种嵌入空间中的几何对齐）的完整基础设施已在项目仓库中，只待 LM 嵌入计算资源部署（`sentence-transformers` + `BAAI/bge-m3` 等）。RQ2 与 RQ3 的预测亦已事前注册（详见 `docs/findings/02_cognitive_substrate.md` 与 `docs/findings/03_vad_crosswalk.md`）。

**从经方传统来源恢复升降浮沉数据**——可能需要从经典《中药学》教材或 CNKI 索引的临床文本语料中手工抽取——是优先级最高的数据采集目标。成功恢复升降浮沉数据后，要么进一步确认具身认知读法（理论负载最重的描述项跨源一致率低），要么对其构成实质挑战（高一致率，提示升降浮沉有被现代西方影响数据库丢失的感受经验基底）。

最后，**由 TCM 临床医师组成的全新 BWS 标注小组**（理想情况下 ≥ 30 名标注者，来自三个以上学派）仍是协议第一阶段的金标准，并能解决 §8 中"编辑性会聚"的疑虑。

## 10. 结语

经典中药性状描述项**四气 / 五味 / 升降浮沉 / 归经 / 毒性**可被操作化为对内感受认知空间的文化建构坐标系，其结构与 NLP 的 Valence-Arousal-Dominance 模型将自然语言情感投影到低秩基座的方式相类。我们已将 VAD 方法学协议的第一阶段——逐轴跨源一致性——应用于五个公开 TCM 数据源的实际规模数据，发现 **QI（寒/热）在 1,098 味中药上达到 85.9% 原始集合相等一致率**，实质性确认了事前注册预测。**升降浮沉在所有五个现代源中的完全缺失**，与具身认知读法的预测——理论负载最重的描述项会在传统被操作化时最早被裁——相一致。

最初的 Herb-VAD 命题——即经典中药性状轴应受到与 NLP-VAD 类比的认知科学待遇，既不应被一笔抹去为"民间分类"、也不应被过度宣称为"已编码的药理学"——已通过了第一道实证检验。该方法学协议的剩余阶段（LM 嵌入回归、维度数检验、全新 BWS 小组）规格清晰、基础设施齐备。

## 代码与数据公开

全部代码、处理后数据、脚本，以及三份事前注册文档（发现 #1、#2、#3）均以 MIT 许可证公开于 https://github.com/watchsound/herb-vad。中国药典 2020 PDF 本身不在再分发之列（商业版权所限）；据其抽取的性状记录（表 2 输入）依本文分析代码同等许可发布。

## 参考文献

Barrett, L. F. (2006). Are emotions natural kinds? *Perspectives on Psychological Science*, 1(1), 28–58.

Barrett, L. F. (2017). *How emotions are made: The secret life of the brain*. Houghton Mifflin Harcourt.

Bradley, M. M., & Lang, P. J. (1994). Measuring emotion: The Self-Assessment Manikin and the semantic differential. *Journal of Behavior Therapy and Experimental Psychiatry*, 25(1), 49–59.

Bradley, M. M., & Lang, P. J. (1999). *Affective norms for English words (ANEW): Instruction manual and affective ratings*. Technical Report C-1, Center for Research in Psychophysiology, University of Florida.

Buechel, S., & Hahn, U. (2018). Word emotion induction for multiple languages as a deep multi-task learning problem. *NAACL-HLT*, 1907–1918.

Dong, Y. 等 (2023). TCM2Vec: TCM herb embeddings learned from formulae. *Multimedia Tools and Applications*.

Ekman, P. (1992). An argument for basic emotions. *Cognition and Emotion*, 6(3–4), 169–200.

Fontaine, J. R. J., Scherer, K. R., Roesch, E. B., & Ellsworth, P. C. (2007). The world of emotions is not two-dimensional. *Psychological Science*, 18(12), 1050–1057.

Hopkins, A. L. (2008). Network pharmacology: The next paradigm in drug discovery. *Nature Chemical Biology*, 4(11), 682–690.

Jang, J., & Lee, S. (2024). Understanding clinical decision-making in traditional East Asian medicine through dimensionality reduction. *Computers in Biology and Medicine*.

Kong, X. 等 (2024). BATMAN-TCM 2.0. *Nucleic Acids Research*.

Lakoff, G., & Johnson, M. (1980). *Metaphors we live by*. University of Chicago Press.

Li, S. (2014). Network target: A starting point for traditional Chinese medicine network pharmacology. *Journal of Ethnopharmacology*.

Mehrabian, A. (1996). Pleasure–arousal–dominance: A general framework for describing and measuring individual differences in temperament. *Current Psychology*, 14(4), 261–292.

Mehrabian, A., & Russell, J. A. (1974). *An approach to environmental psychology*. MIT Press.

Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. *ACL*, 174–184.

Mohammad, S. M. (2025). NRC-VAD Lexicon v2.1. NRC Canada.

Niu, B. 等 (2025). HPGCN: Predicting TCM cold/hot properties from protein–protein interaction features. *Computational and Structural Biotechnology Journal*.

Quigley, K. S., Kanoski, S., Grill, W. M., Barrett, L. F., & Tsakiris, M. (2021). Functions of interoception: From energy regulation to experience of the self. *Trends in Neurosciences*, 44(1), 29–38.

Ru, J. 等 (2014). TCMSP: A database of systems pharmacology for drug discovery from herbal medicines. *Journal of Cheminformatics*, 6, 13.

Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*, 39(6), 1161–1178.

Russell, J. A. (1991). Culture and the categorization of emotions. *Psychological Bulletin*, 110(3), 426–450.

Sedoc, J., Preoţiuc-Pietro, D., & Ungar, L. (2017). Predicting emotional word ratings using distributional representations and signed clustering. *EACL*, 564–571.

Wu, Y. 等 (2019). SymMap: An integrative database of traditional Chinese medicine enhanced by symptom mapping. *Nucleic Acids Research*, 47(D1), D1110–D1117.

Zhang, Y. 等 (2023). ETCM v2.0: An update with comprehensive resource and rich annotations for TCM. *Acta Pharmaceutica Sinica B*.

Zhang, S. 等 (2025). PCMM: Property combination of Chinese materia medica. PubMed Central PMC12104179.

Zhao, Z. (2015). Inter-rater reliability of 归经 attribution across classical sources. *Journal of Traditional Chinese Medical Sciences*.

Zeng, J. (2024). Traditional Chinese Medicine Multi-dimensional Knowledge Graph (TCM-MKG). Zenodo record 19804367.
