<template>
  <view class="container">
    <view class="login-header">
      <view class="logo-box">
        <image class="logo-img" src="/static/logo.png" mode="aspectFit" v-if="hasLogo"></image>
        <view class="logo-placeholder" v-else>
          <text class="dog-icon">🐶</text>
        </view>
      </view>
      <view class="logo-text">Gooh!</view>
      <view class="logo-underline"></view>
    </view>

    <view class="form-container">
      <view class="input-wrapper">
        <input 
          class="custom-input" 
          type="text" 
          v-model="formData.username" 
          placeholder="请输入用户名..." 
          placeholder-style="color: #A5B4FC; font-size: 28rpx;"
        />
      </view>
      <view class="input-wrapper">
        <input 
          class="custom-input" 
          type="password" 
          v-model="formData.password" 
          placeholder="请输入密码..." 
          placeholder-style="color: #A5B4FC; font-size: 28rpx;"
        />
      </view>

      <button 
        class="login-submit-btn" 
        :loading="isLoading" 
        @click="handleLogin"
      >
        登录
      </button>

      <view class="agreement-box">
        <checkbox-group @change="handleAgreementChange">
          <label class="agreement-label">
            <checkbox value="agree" :checked="isAgreed" color="#8B5CF6" style="transform:scale(0.7)" />
            <text class="agreement-text">已阅读并同意</text>
            <text class="agreement-link" @click.stop="showPrivacy">《隐私协议》</text>
            <text class="agreement-text">和</text>
            <text class="agreement-link" @click.stop="showPrivacy">《用户协议》</text>
          </label>
        </checkbox-group>
      </view>
    </view>

    <!-- 底部弹出隐私协议 -->
    <view class="privacy-popup-mask" v-if="privacyVisible" @click="hidePrivacy">
      <view class="privacy-popup-content" @click.stop>
        <view class="privacy-header">
          <text class="privacy-title">隐私政策与用户协议说明</text>
          <text class="close-btn" @click="hidePrivacy">×</text>
        </view>
        <scroll-view scroll-y class="privacy-body">
          <view class="privacy-text-content">
            <text class="privacy-paragraph">欢迎使用 Gooh!。我们非常重视您的隐私保护和个人信息保护。在您使用我们的产品及/或服务前，请认真阅读《隐私政策》和《用户协议》。</text>
            <text class="privacy-paragraph">1. 我们会根据您使用的具体功能收集必要的个人信息。</text>
            <text class="privacy-paragraph">2. 未经您的同意，我们不会将您的个人信息共享给第三方。</text>
            <text class="privacy-paragraph">3. 您可以随时访问、更正、删除您的个人信息，并有权注销账户。</text>
            <text class="privacy-paragraph">4. 我们采用了业界领先的安全技术来保护您的信息安全。</text>
            <text class="privacy-paragraph">如果您继续使用我们的服务，即表示您已阅读并同意前述协议的全部内容。</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <view class="register-entry" @click="goToRegister">
      没有账号？<text class="entry-link">立即注册</text>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useUserStore } from '@/store/user.js';

const userStore = useUserStore();
const isLoading = ref(false);
const isAgreed = ref(false);
const hasLogo = ref(false);
const privacyVisible = ref(false);

const formData = reactive({
  username: '',
  password: ''
});

const showPrivacy = () => {
  privacyVisible.value = true;
};

const hidePrivacy = () => {
  privacyVisible.value = false;
};

const handleAgreementChange = (e) => {
  isAgreed.value = e.detail.value.includes('agree');
};

const handleLogin = () => {
  if (!isAgreed.value) {
    uni.showToast({
      title: '请阅读并同意协议',
      icon: 'none'
    });
    return;
  }

  if (!formData.username || !formData.password) {
    uni.showToast({
      title: '请填写完整信息',
      icon: 'none'
    });
    return;
  }

  isLoading.value = true;

  
  setTimeout(() => {
    // 模拟登录逻辑
    const result = userStore.login(formData.username, formData.password);
    isLoading.value = false;
    
    if (result.success) {
      uni.showToast({
        title: '登录成功',
        icon: 'success'
      });
      
      setTimeout(() => {
        // 如果未完成评估，跳转到评估页，否则跳转到首页
        if (!userStore.userInfo.hasCompletedAssessment) {
          uni.navigateTo({
            url: '/pages/assessment/assessment'
          });
        } else {
          uni.switchTab({
            url: '/pages/index/index'
          });
        }
      }, 1000);
    } else {
      uni.showToast({
        title: result.message,
        icon: 'none'
      });
    }
  }, 1000);
};

const goToRegister = () => {
  uni.navigateTo({
    url: '/pages/register/register'
  });
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background-color: #FDFCF8; /* 奶白色背景 */
  padding: 0 60rpx;
}

.login-header {
  margin-top: 120rpx;
  margin-bottom: 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-box {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 20rpx;
}

.logo-img {
  width: 100%;
  height: 100%;
}

.logo-placeholder {
  width: 100%;
  height: 100%;
  background-color: #ffffff;
  border-radius: 40rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 80rpx;
  box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.05);
}

.logo-text {
  font-size: 56rpx;
  font-weight: bold;
  color: #1E293B;
  font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
}

.logo-underline {
  width: 60rpx;
  height: 6rpx;
  background-color: #A5B4FC; /* 浅紫色 */
  border-radius: 3rpx;
  margin-top: -4rpx;
  align-self: flex-end;
  margin-right: 20rpx;
}

.form-container {
  width: 100%;
}

.input-wrapper {
  background-color: #ffffff;
  border-radius: 40rpx;
  height: 100rpx;
  margin-bottom: 30rpx;
  display: flex;
  align-items: center;
  padding: 0 40rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.03);
}

.custom-input {
  width: 100%;
  height: 100%;
  font-size: 28rpx;
  color: #1E293B;
}

.login-submit-btn {
  width: 100%;
  height: 100rpx;
  background-color: #8B5CF6; /* 紫色主色 */
  color: #ffffff;
  border-radius: 50rpx;
  font-size: 32rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 60rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 8rpx 20rpx rgba(139, 92, 246, 0.2);
}

.agreement-box {
  display: flex;
  justify-content: center;
}

.agreement-label {
  display: flex;
  align-items: center;
}

.agreement-text {
  font-size: 24rpx;
  color: #64748B;
}

.agreement-link {
  font-size: 24rpx;
  color: #8B5CF6;
  font-weight: bold;
}

.register-entry {
  margin-top: 40rpx;
  margin-bottom: 60rpx;
  font-size: 26rpx;
  color: #64748B;
}

.entry-link {
  color: #8B5CF6;
  font-weight: bold;
}

/* 隐私政策弹出框样式 */
.privacy-popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.privacy-popup-content {
  width: 100%;
  box-sizing: border-box; 
  height: 50vh; 
  background-color: #ffffff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
}

.privacy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.privacy-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1E293B;
}

.close-btn {
  font-size: 48rpx;
  color: #94A3B8;
  padding: 0 10rpx;
}

.privacy-body {
  flex: 1;
  overflow: hidden;
}

.privacy-text-content {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.privacy-paragraph {
  font-size: 26rpx;
  color: #64748B;
  line-height: 1.6;
}
</style>
