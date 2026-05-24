---
title: "Flow Matching Lecture 1"
date: 2026-04-07
permalink: /posts/2026/05/flow-matching-lecture1./
tags:
  - flow matching
---

# Generative AI with Stochastic Differential Equations

## 1 Formalize Generating Something

我们将我们要生成的对象表示为向量

$$
\mathcal{z} \in \mathbb{R}^d
$$

某个生成对象的好坏很多时候是主观的，因此我们将生成问题建模为生成对象符合数据分布的可能性。 

在概率论的语言下，我们想要得到的是一个数据分布，即我们想要生成的对象的分布。我们记作

$$
p_{data}
$$

从而，进行一次生成就是在分布中做一次采样。

我们用于训练的数据集可以理解为有限数量符合分布 $p_{data}$ 的样本

$$
z_1,\dots,z_N \sim p_{data}
$$

往往有用的是条件生成，即支持用户输入一个 prompt 作为 condition（记作 $y$），这样一来我们需要建模的就是一个条件分布，基于条件的生成就是在这样一个条件分布采样

$$
z \sim p_{data}(\cdot | y)
$$

我们将从无条件的生成出发。

生成模型的一个非常重要的思路就是，我们从一个容易采样的 initial distribution 出发，采样一个样本，通过神经网络，转换为符合 data distribution 的样本。

![image-20260521224621154](/images/flow-matching-lecture1/image-20260521224621154.png)

往往我们的 initial distribution 是一个 $d$ 维的标准正态分布。这里的 $d$ 正好是我们数据的维度。

$$
p_{init} = \mathcal{N}(0,I_d)
$$

## 2 Flow Models

这里开始上强度了。

我们先 formalize 几个概念

**Trajectory**:

$$
X:[0,1]\to \mathbb{R}^d,\,t\mapsto X_t
$$

**Vector Field**

$$
u:\mathbb{R}^d \times [0,1]\to \mathbb{R} ^d ,\,     (x,t)\mapsto u_t(x)
$$

**Ordinary differential equation(ODE)**

$$
\begin{aligned}
X_0 &= x_0 \quad (initial \, condition)\\
\frac{d}{dt}X_t &= u_t(X_t)
\end{aligned}
$$

**Flow**

$$
\begin{aligned}
\psi &: \mathbb{R}^d\times [0,1]\to \mathbb{R}^d ,\, (x_0,t)\mapsto \psi_t(x_0)\\
\psi_0(x_0) &= x_0\\
\frac{d}{dt}\psi_t(x_0) &= u_t(\psi_t(x_0))
\end{aligned}
$$

> [!NOTE]
> 某个变量有 $_t$ 下标意味该变量（可能）和时间 $t$ 有关。

> [!NOTE]
> 如果 vector filed $u_t(x)$ 是连续可微且导数有界的，式 （8）存在唯一解。这件事在 ML 和 DL 里一般都是成立的。

> [!NOTE]
>
> **ODE**简要介绍
>
> 含有未知函数的导数或者微分的，联系着自变量、未知函数及其导数或微分的方程就做微分方程。如果有求偏导就是**偏微分方程（PDE）**，没有偏导就**是常微分方程（ODE）**
>
> 微分方程中出现的未知函数的导数的最高阶数称为微分方程的**阶**。
>
> n 阶 ODE 的一般形式可以写成
> $$
> F(x,y,y\prime,\cdots,y^{(n)})=0
> $$
> 满足微分方程的函数称为微分方程的解。对 n 阶微分方程，含有 n 个彼此独立的任意常数的解称为该微分方程的**通解**。不含任意常数的解称为**特解**。我们可以给定一些**初始条件**，从而将通解转化为特解。
>
> 几何上，微分方程的特解对应一条曲线，而通解对应一个曲线族。

> [!NOTE]
>
> 这里（8）是一个 ODE，其自变量是时间 $t$，因变量 $X$ 虽然不是一个标量，但是因为自变量是标量，所以这个还是属于 ODE 而非 PDE。

这里提到的几个概念的关系如图所示：

![flow_model_concept](/images/flow-matching-lecture1/flow_model_concept.png)

也就是说，这些概念的核心是 Vector Filed(VF)，一个 VF 就定义了所有。

我们给系统一个几何的图景。一个 VF 可以想象为一个速度场，并且这个速度场是时变的。 $X$ 可以想象为空间中的点（比如想象一个一维或者二维或者三维的空间）。给定一个时刻和一个点，VF 给出了这个点在该时刻的速度矢量。在这个 VF 的任意初始位置（比如 $x_0$）放置一个粒子，该粒子会因为场的作用而运动。运动的轨迹就是一条 Trajectory. 这个放置粒子的操作数学上就是给 ODE 指定了初始条件。Trajectory 本质上就是 ODE 的解。Flow $\psi$ 的作用是输入一个粒子的初始位置以及一个时刻 $t$，输出该粒子在时刻 $t$ 的位置。可以想象为所有 Trajectory 的共同演化构成了 Flow.

---

课件给了一个 example

![image-20260523173824406](/images/flow-matching-lecture1/image-20260523173824406.png)

本质上来讲，给定一个 $u_t(x)$，我们就可以去求解一个 Flow，然后通过验证 initial condition 和 ODE 被满足确认这个 Flow 是正确的。

在闭式解不容易求出的情况下，可以用 Euler method 数值求解。

![image-20260523174205588](/images/flow-matching-lecture1/image-20260523174205588.png)

---

回到我们对生成模型的建模，我们需要找到一个方法，将 $p_{init}$ 转化为 $p_{data}$ .

我们的做法是对于 $X_0\sim p_{init}$，我们通过一个 ODE 将其演化为 $X_1\sim p_{data}$：

$$
\frac{d}{dt}X_t=u_t^\theta(X_t)
$$

这里的 VF 由 neural network 定义，网络参数为 $\theta$

从而，可以用之前提到的 Euler method 从 Flow Model 中那采样。

![image-20260523222323160](/images/flow-matching-lecture1/image-20260523222323160.png)

## 3 Diffusion Model

ODE 的解是一个 trajectory, SDE 的解则是一个 stochastic process，或者说 random trajectory.

此外，在 Flow model 的基础上，我们会额外定义一个 diffusion coefficient $\sigma$, 最通用的方案是将 $\sigma$ 定义为时间的函数，即

$$
\sigma:[0,1]\to \mathbb{R}_{\ge 0},\,t\mapsto \sigma_t
$$

并且 $\sigma$ 是非负的。当 $\sigma=0$ 的时候 Diffusion model 退化回 Flow model. (13) 可以看到 $\sigma$ 控制注入的噪声 (或者说随机性) 的强度。

为了注入随机性，Flow Model 中的 ODE 在这里改写成的 **Stochastic Differential Equation(SDE)**:

$$
\begin{aligned}
X_0 &= x_0 \quad (initial \, condition)\\
dX_t &= u_t(X_t)dt + \sigma_t dW_t
\end{aligned}
$$

这里的 $W_t$ 是一个**布朗运动（Brownian Motion）**

> [!NOTE]
>
> 一个随机过程如果满足如下四个性质则称为布朗运动:
>
> 1. 初值为 $\mathbf{0}$
>    $$
>    P(W_0=\mathbf{0})=1
>    $$
>
> 2. 独立增量. 对于任意的时间点$0\le t_1\le t_2\le\dots\le t_n$, 其增量 $W_{t_2}-W_{t_1},W_{t_3}-W_{t_2},\dots$ 相互独立
>
> 3. 高斯增量. 对于任意的时间点 $0\le s<t$, 其增量 $W_t-W_s$ 服从均值为 0 方差为时间差 $t-s$ 的正态分布:
>    $$
>    W_t-W_s\sim N(\mathbf{0},(t-s)I)
>    $$
>
> 4. 路径连续. $W_t$ 关于时间 t 的函数图像是连续的

> [!NOTE]
>
> 1. 这里我们用微分的形式而非求导的形式定义 (13) 是因为无法定义 $\frac{dW_t}{dt}$, $W_t$ 处处不可导. 
> 2. 这里需要一些数学背景才能把所有事情定义和理解清楚. 不过直观上只需要将布朗运动看做一个正态分布的 “随机过程版” 就可以了, $\sigma dW_t$ 可以看做注入了一个高斯噪声
> 3. 聪明的数学家们告诉我们在深度学习的论域里这一切拥有良好的性质, 我们的 SDE 有唯一解. 

除此之外, 我们的其他组件和 ODE 是一样的. 我们同样会有一个 VF.

Sample 的算法:

![image-20260524150459459](/images/flow-matching-lecture1/image-20260524150459459.png)

1. 这里除了 $\sigma_t \sqrt{h}\epsilon$ 之外, 其他部分都和模拟 ODE 的 Euler method 是一样的.
2. 这里用了一种叫**重参数化**的技术将 (13) 中的 $dW_t$ 分布采样变换为了从 $\epsilon\sim \mathcal{N}(0,I_d)$ 中采样再乘以时间步长 $h$ 的根.

---

将之前 ODE 的例子改写为 SDE 版本:

![image-20260524151046804](/images/flow-matching-lecture1/image-20260524151046804.png)

---

与 ODE 一样, 我们可以定义一个神经网络 $u^\theta_t$ 来表示 VF, 从而定义一个 Diffusion Model

![image-20260524151236843](/images/flow-matching-lecture1/image-20260524151236843.png)
