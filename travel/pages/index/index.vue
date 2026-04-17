<template>

    <!-- 自适应顶部导航栏 -->
    <view class="nav-wrapper" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-bar">
        <view class="nav-left" @click="onLeftClick"></view>
        <view class="nav-title">首页</view>
        <view class="nav-right"></view>
      </view>
    </view>

    <view class="container" :style="{ marginTop: topHeight + 'px' }">
    <!-- 首页主内容区域 -->
    <view class="home-content">
      <view class="welcome-section">
        <text class="greeting">你好, {{ userInfo.username || '旅行者' }}</text>
        <text class="subtitle">在这里，每一段旅程都有它的灵魂。</text>
      </view>
      
      <!-- 个性化推荐占位卡片 -->
      <view class="placeholder-card">
        <text class="placeholder-text">正在为您编织专属的旅行记忆...</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onMounted, watch, ref, computed } from 'vue';
import { useUserStore } from '@/store/user.js';
import { storeToRefs } from 'pinia';

/**
 * 首页逻辑实现
 */
const userStore = useUserStore();
const { userInfo } = storeToRefs(userStore);

// 顶部状态栏适配
const statusBarHeight = ref(0); // px
const navBarHeight = ref(44); // px，导航栏自身高度，可按需调整
const topHeight = computed(() => statusBarHeight.value + navBarHeight.value);

const onLeftClick = () => {
  // 左侧按钮点击回调（可自定义：返回、打开侧边栏等）
};

/**
 * 检查是否需要进行性格评估
 * 如果已登录且未完成评估，跳转到评估页面
 */
const checkAssessment = () => {
  if (userInfo.value.isLoggedIn && !userInfo.value.hasCompletedAssessment) {
    uni.navigateTo({
      url: '/pages/assessment/assessment'
    });
  }
};

// 生命周期：挂载时检查
onMounted(() => {
  checkAssessment();

  // 获取系统信息以适配状态栏高度（uni-app 返回的是 px）
  try {
    const sys = uni.getSystemInfoSync();
    if (sys) {
      // 优先使用 statusBarHeight
      statusBarHeight.value = sys.statusBarHeight || (sys.safeArea && sys.safeArea.top) || 0;
      // iOS 刘海机型可能需要额外处理，如 navBarHeight 可保持 44px
    }
  } catch (e) {
    // ignore
  }
});

// 监听登录状态变化
watch(() => userInfo.value.isLoggedIn, () => {
  checkAssessment();
});
</script>

<style scoped>
body {
  background-color: rgb(250, 250, 250);
}

/* 容器及基础色值应用 */
.container {
  min-height: 100vh;
  background-color: rgb(250,250,250);
  padding: 40rpx;
}

.welcome-section {
  margin-bottom: 40rpx;
}

.greeting {
  font-size: 44rpx;
  font-weight: bold;
  color: #1E293B;
  display: block;
}

.subtitle {
  font-size: 28rpx;
  color: #64748B;
  margin-top: 16rpx;
  display: block;
}

.placeholder-card {
  background-color: #ffffff;
  padding: 80rpx 40rpx;
  border-radius: 32rpx;
  text-align: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.placeholder-text {
  color: #94a3b8;
  font-size: 28rpx;
  font-style: italic;
}

/* 顶部导航样式 */
.nav-wrapper {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  z-index: 1000;
  background: #ffffff;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.nav-bar {
  height: 44px; /* 与 navBarHeight 对应，单位 px */
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.nav-title {
  font-size: 34rpx;
  color: #111827;
  font-weight: 600;
}
.nav-left,
.nav-right {
  width: 88rpx;
  height: 100%;
  position: absolute;
  top: 0;
}
.nav-left { left: 0; }
.nav-right { right: 0; }
</style>