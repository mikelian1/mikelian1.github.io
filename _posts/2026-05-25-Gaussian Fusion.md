---
title: "Gaussian Fusion"
date: 2026-05-25
permalink: /posts/2026/05/gaussianfusion/
tags:
  - Autonomous Driving
excerpt: "Notes for a GaussianFusion presentation outline."
---
# GaussianFusion 汇报

## 研究背景

1. 相比传统多模块的流程，端到端的自动驾驶策略（从传感器数据直接生成驾驶决策）可以精简决策流程。
2. 优势在于 pipeline 的各个模块可以联合优化，相互促进。
3. 引入多模态联合策略，可以提升系统决策性能与鲁棒性。

## 传统方法分析--flatten fusion
- 把不同模态的 embeddings 融合到共用的语义空间
- 通常基于**注意力机制**融合
- 高效 + 对空间位置信息要求低

===

- 可解释性弱
- 融合结果空间信息弱（不适合场景重现这类任务）

## 传统方法分析--BEV fusion
- 先把各个模态数据各自透射到BEV系（获得了三维空间信息）
- 再在 BEV 中融合
- 在物体检测/场景重现等下游任务中表现好

<->

*缺点*：

- 计算/显存开销大
- 稠密（不必要）
- 对分辨率极其敏感

## 用 Gaussian 取代 BEV
### gaussian 的特征
1. 物理可解释性（每个gaussian包含位置、尺度、旋转、语义和显隐式特征）
2. 信息紧凑性
3. 稀疏性
用 Gaussian 覆盖目标物体所在的关键区域


### 3D Gaussian 的不足
- 数据集很少做三维表注，难以监督、优化
- Gaussian splatting 原本运用场景与 E2E 存在错位
- 3D gaussian 的信息可能没有被充分利用


### 2D Gaussian
- 更紧凑，运用效率更高
- 可直接渲染在 BEV 中，利于利用数据集做监督

> 保留 BEV 的空间特征，但远比 BEV 稀疏，性能更友好


## Gaussian 表示
- mean(xy) / scale / heading / rotation / semantic logits(7维)
- explicit / implicit features


- 每个 Gaussian 是场景中的一个可学习“软区域”，它会在训练中移动、变形，并携带语义和规划信息
- 多个 Gaussian 叠加起来，形成对 BEV 场景的稀疏表达。
- 背景区域不需要大量表示能力，Gaussian 会逐渐聚集到车辆、车道、可行驶区域等 foreground。


![alt text](/assets/images/gaussianfusion/image-5.png)

## 整体框架

```
 多传感器输入 
 → image/point encoder
 → Gaussian initialization
 → Gaussian encoder refinement
 → Gaussian decoder
```
> [!NOTE]
> 输入：图像及其变换矩阵、雷达点云及其变换矩阵
> 输出：此后的车辆轨迹-时间关系

---
<img src="/assets/images/gaussianfusion/image.png" height="400">

## 双分支设计

> [!NOTE]
> 自动驾驶既需要可解释的局部空间/语义信息，也需要对规划有用的全局上下文信息，单一 embedding 很难兼顾这两者，故分成两支。

- explicit feature：负责局部几何/语义和 map construction
- implicit feature：负责全局 planning cue，只服务轨迹规划

### explicit feature

- 负责“看得见、能监督”的场景结构
- 从传感器输入的局部区域产生（deformable attention，参考点就在gaussian附近）
<->
主要职责:

1. 更新 Gaussian 的物理属性
2. 辅助 map construction
3. 学习局部语义和空间结构。


### implicit feature
- 不依赖几何投影
- 和全局多模态特征交互
- 主要服务 trajectory planning
- 不用于更新物理属性

## Gaussian Init

功能：<br>初始化 explicit Gaussian 和 implicit Gaussian<br>本身不处理 backbone 得到的数据

===

```Python
random_samples_front=448  # exp前方448个
random_samples_back=64    # exp后方64个
implicit_samples=512      # imp共计512个
```
---

### explicit Gaussian

> mean(xy) / scale / heading / semantic(7维) / rotation / **feature**

1. 初始位置在各自矩形区域内随机
2. 初始sclae、朝向固定
3. 初始semantic, feature随机
4. 与 ego_status 无关

---

### implicit Gaussian

- 每个 implicit gaussian 的特征是：<br>
自车状态 + 每个 token 自己的 learnable embedding
- 只有 feature，暂时没有物理信息，后续由`GaussianRefiner`解码
- 这时更像 token，但是代码为了统一接口，也用`GaussianPrediction`容器装它

> [!NOTE]
> 原始自车状态包括位移。速度。加速度。油门刹车等，后被 Linear 至更高维


## Gaussian Encoder

### 整体流程

![alt text](/assets/images/gaussianfusion/image-1.png)
---
```
Each block:
1. self_attn
Gaussian 和 Gaussian 之间交互
2. norm
3. cross_attn_pts
Gaussian 从 point feature 里取信息
4. norm
```
<->
```
5. cross_attn_img
Gaussian 从 image feature 里取信息
6. norm
7. ffn
对每个 Gaussian feature 做非线性更新
8. norm
```

---
### 信息更新顺序
```
   多模态特征
 → 先更新 explicit feature
 → 再更新 implicit feature
 → Gaussian 之间互相通信
 → 最后用 explicit feature 更新物理属性
```


### 输入

`forward(self, image_feature, pts_feature, gaussian, *args, **kwargs):`

1. `feat_flatten_img, spatial_shapes_img, level_start_index_img, kwargs = image_feature`
2. `feat_flatten_pts, spatial_shapes_pts, level_start_index_pts = pts_feature`
3. 当前 gaussians 的物理信息

### 位置编码
```
  Gaussian means: [B, G, 2]
→ sine positional embedding
→ Linear + ReLU + LN + Linear↓
→ pos_embedding: [B, G, d_model]
```

- 把 Gaussian 的空间位置编码成 Transformer 可以使用的向量
- attention 机制对 token 的顺序不敏感。如果不拼接位置，模型不能区分<br>Gaussian 的位置
- 在之后 attention 中使用


## Gaussian Encoder--self attention

> 输入只有旧 gaussian feature 与位置编码，利用自注意力输出新 gaussian feature

1. 每个显式 Gaussian 根据自己的 feature 和位置编码，关注其他显式 Gaussian
2. 获得场景中其他 Gaussian 的上下文信息与自身位置信息
3. 放在与 image 和 points 的 cross-attention 之前，提升 feature 效果

---

$$
\left\{\mathbf{f}_{1}^{exp\prime}, \dots , \mathbf{f}_{P}^{exp\prime}\right\} = \operatorname{SelfAttn}\left(\left\{\mathbf{f}_{1}^{exp\ddagger}, \dots , \mathbf{f}_{P}^{exp\ddagger}\right\}, \left\{\mathbf{e}_{1}, \dots , \mathbf{e}_{P}\right\}\right)
$$

$$
\left\{\mathbf{f}_{1}^{imp\prime}, \dots , \mathbf{f}_{P}^{imp\prime}\right\} = \operatorname{SelfAttn}\left(\left\{\mathbf{f}_{1}^{imp\ddagger}, \dots , \mathbf{f}_{P}^{imp\ddagger}\right\}, \left\{\mathbf{e}_{1}, \dots , \mathbf{e}_{P}\right\}\right)
$$

$$
\left\{\mathbf{e}_{1}, \dots , \mathbf{e}_{P}\right\} = \operatorname{PosEmbed}\left(\left\{\mathbf{m}_{1}, \dots , \mathbf{m}_{P}\right\}\right)
$$


## Gaussian Encoder--参考点
> [!NOTE]
> deformable attention 中的一个参数
>
> 建立于 cross attention 中 key / value 所在的参考系中 (归一化的 BEV 系 / image 图像系)

### xy坐标

- 固定采样点（5个）<br>
explicit 分支的固定采样点取原 Gaussian 的中心点、上方点、下方点、前方点、后方点
- 可学习采样点<br>
以中心点为基准，从 Gaussian_feature Linear生成若干个偏移量加上去

### bev_mask

- 布尔张量，位置不合理的地方为 0
- 意义是某个 Gaussian query 是否能被某个 camera / sensor view 看见
- 目的是减少部分计算量

> [!NOTE]
> 图像分支 query 是3D点，可能不在 image 视野内:<br>
> 1. 深度必须 > 0<br>
> 2. 投影后的 x,y 必须在图像范围内


## Gaussian Encoder--cross-attention
> [!NOTE]
> SpatialCrossAttention 一个类实现 'cross_attn_pts' 和 'cross_attn_img' 的复用

### Deformable Attention

- 一种不是看全局（如 image 中 H*W 个 pixel），而是只看若干采样点的注意力机制
- 输入：query，key，value，reference points
- 采样点亦可动态调整(在一个参考点基础上加若干种 offsets)
---
#### 输入
- cross_attn_pts
    - query/key = Gaussian explicit feature + positional encoding
    - value = point feature
    - reference_points = Gaussian 周围的 2D 查询点
- cross_attn_img
    - query/key = Gaussian explicit feature + positional encoding
    - value = multi-view image feature
    - reference_points = Gaussian 查询点投影到图像平面的 2D 点

### Deformable Attention 的流程
```
  Gaussian feature 作为 query(所有 query 参与计算)
→ query 预测 offsets 和 attention weights
  reference_points 提供初始空间位置
→ reference_points + offsets 得到 sampling points
→ value feature map 在 sampling points 上采样
→ 按 attention weights 加权求和
→ 得到更新后的 Gaussian feature
```

### 省略 key tensor

Deformable attention 不再显式构建完整 key tensor，而是由 query 直接预测 sampling offsets 与 attention weights，并对 sampled value 做加权聚合。

### cross-attention 的细节
> [!NOTE]
> 1. 具体实现上分了多个头，每个头处理一部分维度
> 2. backbone 输出的是特征金字塔，"Multi-scale feature map",注意力对每个层级都做处理<br>
> 每个 query 只需要 与 num_heads × num_levels × num_points 个 values 交互

### 公式

$$
\mathbf {f} ^ {e x p \dagger} = \sum_ {i = 1} ^ {n _ {q}} \operatorname {DeAttn} \left(\mathbf {f} ^ {e x p}, \mathcal {Q} [ i ], \mathcal {M} ^ {p}\right)
$$

$$
\mathbf{f}^{\text{exp}\ddagger} = \sum_{i=1}^{n_q \times n_p} \text{DeAttn}\left(\mathbf{f}^{\text{exp}\dagger}, \mathcal{Q}_{3d}[i], \mathcal{M}^I\right)
$$

### 对 points 和 image 的细节差异
1. cross_attn_img: num_cams = 多相机数量，本文取3<br>
cross_attn_pts: num_cams = 1 (num_cams 无实际意义了，全局一起看)
2. Key, Value / reference points 的具体内容不同
3. 既然处理逻辑类似，故只写一段代码，预设多个接口

### 具体实现细节

- 根据 bev_mask 找出每个 camera/point-view 能看到哪些 Gaussian
- 让这些 Gaussian 根据 reference points 找对应 sensor feature 上做 deformable attention
- 如果某个 gaussian 可以被多个 camera 看到，则取平均值（否则被多个 camera 看到的 feature magnitude 天然更大）
- cross-attention 的输出结果 Linear 后与原 query 残差连接
- 输出更新后的 gaussian feature

## Gaussian Encoder--FFN (Feed-Forward Network)

- 各级维度都保持不变
- 只是经过 Linear -> ReLU -> Dropout -> Linear -> Dropout -> Residual Add 来更新
- 增强 feature 的表达能力

## Gaussian Encoder--更新物理属性

$$
\quad (\mathbf{m}', \mathbf{s}', \mathbf{r}', \mathbf{c}') = \mathrm{MLP}(\mathbf{f}^{exp\prime})
$$


$$
\mathbf{G}' = \{\mathbf{m}' + \mathbf{m}, \mathbf{s}', \mathbf{r}', \mathbf{c}', \mathbf{f}^{exp\prime}, \mathbf{f}^{imp\prime}\}
$$

> $\mathbf{m}'$与 $\mathbf{s}'$均被限制在一定范围内，避免学习率过大，损失震荡，难以收敛

## Gaussian Decoder

### Map construction

> [!NOTE]
> 除了是一个输出项、一个可视化模块以外，也承担训练监督作用<br>
> 就是 Gaussian Splatting，但是基于 2D gaussian<br>
> 把 refined 后的稀疏 2D Gaussians 转换成稠密的 BEV semantic map
> 以便用 ground-truth BEV 语义真值来监督 Gaussian 表达（在这一步用 loss 函数收敛 refine / encoder 的参数）


### Map construction--Gaussian Splatting 细节

- 每个像素基于马氏距离 ($\exp \left(- \frac {1}{2} \left(\mathbf {x} - \mathbf {m} _ {i}\right) ^ {\mathrm {T}} \boldsymbol {\Sigma} _ {i} ^ {- 1} \left(\mathbf {x} - \mathbf {m} _ {i}\right)\right)$) 对各个 gaussian 的semantic logits 加权求和
- 通过给 semantic 乘以 opacity 的技巧，鼓励 gaussian 移至前景（否则 semantic 小，loss 大，反向传播）
- loss：包括 cross entropy loss $L_{ce}$ and the lovasz-softmax loss $L_{lov}$
> foreground（opacity 大）指需要预测的语义类别区域<br>background（opacity 小）指空白区域

### cascade planning
> [!NOTE]
> - 似乎是原创组件
> - 端到端任务，输出轨迹规划<br>
> - 用一个 decoder，把 Gaussian 转化成 ego vehicle 的未来轨迹<br>
> - 不直接一次性预测轨迹，而是从 anchor trajectories 出发，利用 Gaussian 场景表示逐级修正轨迹。
> - Anchor trajectories：预定义的候选轨迹，来自训练集轨迹分布

---

```
  Anchor trajectory
→ 对轨迹上的每个点，寻找附近 top-m 个 Gaussians
→ 得到与该轨迹相关的 Gaussian subset
→ Gaussian Spatial Attention：让 anchor query 关注附近 Gaussians
→ Gaussian Cross Attention：再与全局 Gaussians 交互
→ MLP 预测 trajectory residual
→ residual + anchor = refined trajectory
→ 把 refined trajectory 作为下一阶段 anchor，继续 refine
```
---

$$
F_A = \mathrm{CrossAttn}(F_{query}, F_{G_A}),
$$

$$
F_{query} = \mathrm{Embedding}(A),
$$

$$
F_{G_A} = \left\{ [f_i^{exp}; f_i^{imp}] \mid i = 1, \dots, mT \right\}.
$$

<->

![alt text](/assets/images/gaussianfusion/image-3.png)

---

$$
\tau = \mathrm{MLP}(F_o) + A,
$$

$$
F_o = \mathrm{CrossAttn}(F_A, F_G),
$$

$$
F_G = \left\{ [f_i^{exp}; f_i^{imp}] \mid i = 1, \dots, P \right\}.
$$

<->

![alt text](/assets/images/gaussianfusion/image-2.png)

---

> [!NOTE]
> - 基于 anchor 轨迹，关注 gaussian
> - 而非基于场景生成轨迹
> - 计算量明显减小，且输出明显更稳定
> - 但也难免对于个别复杂场景的反应不是最佳

## 实验

### 结果
- 在闭环和开环 benchmark 上都表现优异
- 开环benchmark NAVSIM 上达到/接近 SOTA
- 闭环benchmark Bench2Drive上部分指标达到 SOTA，部分指标在 learning-based 策略中领先，但逊于 rule-based 策略

### 消融实验
- Gaussian Exp. Fusion, Gaussian Imp. Fusion, Cascade Planning 能够发挥作用
- 移出了 agent prediction 模块

## 失败案例分析

### 核心缺陷
1. 驾驶策略过于保守
2. 泛化能力弱
3. 不确定性（雾天等）倾向做低风险决策
> 低风险优先

### 失败场景
1. 转弯——延迟，轨迹窄
2. 逆境（雾天等）——低速缓慢驾驶
3. 多车交互时保守——不愿超车

### 原因分析
- 这是 imitation learning 的经典问题
- 学到的是数据中的平均/普遍行为，而非最优策略

## 本研究的不足

### 作者承认的问题——鲁棒性未验证
- 没有对小目标、快速运动目标跟踪定量评估（远处小型障碍物/行人横穿）
- 未测试传感器遮挡——只能使用单一模态
- 未测试传感器噪声

### 2D Gaussian 表征
- 对强高度信息依赖场景有缺陷
- 实际上是一种取舍下的选择