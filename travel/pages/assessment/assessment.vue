<template>
  <view class="container">
    <!-- 标题区域 -->
    <view class="assessment-header">
      <view class="header-main">
        <text class="assessment-title">选择你的旅行偏好</text>
        <text v-if="currentIndex===0" class="skip-btn" @click="skipAssessment">跳过</text>
      </view>
      <text class="assessment-progress-text">已选 {{ currentIndex + 1 }}/{{ dimensions.length }}</text>
    </view>

    <!-- 卡片式问卷主体 -->
    <view class="assessment-card">

      <!-- 维度选择容器 -->
      <view class="dimension-container">
        <view class="dimension-item">
          <view class="dimension-header">
            <text class="dimension-name">{{ currentDimension.name }}</text>
            <view class="illustration-box">
              <image 
                class="traveler-img" 
                src="/static/png.png" 
                mode="aspectFit"
              ></image>
            </view>
          </view>
          <view v-if="currentDimension.type === 'basic_info' || currentDimension.type === 'pref_info'" class="form-list">
            <view v-for="field in currentDimension.fields" :key="field.key" class="form-item">
              <text class="field-label">{{ field.label }}</text>
              
            
              <input 
                v-if="field.type === 'text' || field.type === 'number'"
                class="field-input"
                :type="field.type"
                v-model="tempScores[field.key]"
                :placeholder="field.placeholder"
                placeholder-style="color: #A5B4FC; font-size: 24rpx;"
              />

          
              <view v-if="field.type === 'select'" class="select-grid">
                <view 
                  v-for="opt in field.options" 
                  :key="opt"
                  class="select-opt-item"
                  :class="{ 'opt-active': tempScores[field.key] === opt }"
                  @click="tempScores[field.key] = opt"
                >
                  {{ opt }}
                </view>
              </view>
            </view>
          </view>

          <!-- 2. 兴趣爱好类型 (多选网格) -->
          <view v-else-if="currentDimension.type === 'multi_select'" class="interest-grid">
            <view 
              v-for="opt in currentDimension.options" 
              :key="opt.value"
              class="interest-item"
              :class="{ 'interest-active': tempScores.interests.includes(opt.value) }"
              @click="toggleInterest(opt.value)"
            >
              <text class="interest-label">{{ opt.label }}</text>
            </view>
          </view>

          <!-- 3. 性格维度评分类型 (分段式进度条样式) -->
          <view v-else class="score-section">
            <text class="dimension-desc">{{ currentDimension.definition }}</text>
            <view class="segment-selector">
              <view 
                v-for="i in [1, 2, 3]" 
                :key="i"
                class="segment-item"
                :class="{ 'segment-active': tempScores[currentDimension.key] >= i }"
                @click="selectScore(currentDimension.key, i)"
              ></view>
            </view>
            <view class="segment-labels">
              <text class="seg-label">{{ currentDimension.options[2].level }}</text>
              <text class="seg-label">{{ currentDimension.options[0].level }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作按钮 -->
    <button class="submit-btn" @click="nextStep">
      {{ currentIndex === dimensions.length - 1 ? '选好了，开始新行程！' : '下一步' }}
    </button>

    <!-- 底部页码指示器 -->
    <view class="page-indicator">
      <view 
        v-for="(dim, index) in dimensions" 
        :key="index"
        class="dot"
        :class="{ 'dot-active': currentIndex === index }"
      ></view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useUserStore } from '@/store/user.js';

const userStore = useUserStore();

// 当前评估维度的索引
const currentIndex = ref(0);
// 临时存储用户选择的信息
const tempScores = reactive({
  // 基础信息
  age: '',
  gender: '',
  occupation: '',
  // 兴趣爱好 (数组)
  interests: [],
  // 旅游偏好
  destType: '',
  travelStyle: '',
  accommodation: '',
  // 性格维度
  checkIn: 2,
  depth: 2,
  planning: 2,
  social: 2,
  comfort: 2,
  adventure: 2
});

// 问卷维度定义数据
const dimensions = [
  {
    key: 'basic',
    name: '1. 基础信息',
    definition: '让我们更了解您的背景',
    type: 'basic_info',
    fields: [
      { key: 'age', label: '您的年龄', placeholder: '请输入年龄', type: 'number' },
      { key: 'gender', label: '您的性别', options: ['男', '女', '保密'], type: 'select' },
      { key: 'occupation', label: '您的职业', placeholder: '请输入职业', type: 'text' }
    ]
  },
  {
    key: 'interests',
    name: '2. 兴趣爱好',
    definition: '兴趣爱好是性格的直接体现 (可多选)',
    type: 'multi_select',
    options: [
      { value: 'sports', label: '运动', desc: '外向、敢于挑战' },
      { value: 'music', label: '音乐', desc: '感性、热爱生活' },
      { value: 'movie', label: '电影', desc: '追求共鸣、审美力强' },
      { value: 'reading', label: '阅读', desc: '内向、善于思考' },
      { value: 'painting', label: '绘画', desc: '细腻、专注力强' },
      { value: 'gaming', label: '游戏', desc: '反应快、团队协作' },
      { value: 'other', label: '其他', desc: '未列出的兴趣爱好' }
    ]
  },
  {
    key: 'travel_pref',
    name: '3. 旅游偏好',
    definition: '您理想中的旅行是什么样的？',
    type: 'pref_info',
    fields: [
      { key: 'destType', label: '目的地类型', options: ['海滨', '山地', '城市', '古镇', '乡村','未知'], type: 'select' },
      { key: 'travelStyle', label: '旅行方式', options: ['随性漫游', '特种兵打卡', '深度体验', '休闲度假', '未知'], type: 'select' },
      { key: 'accommodation', label: '住宿偏好', options: ['星级酒店', '特色民宿', '青年旅舍', '度假村','未知'], type: 'select' }]
  },
  {
    key: 'checkIn',
    name: '4. 打卡导向性',
    definition: '追求网红景点、标志性地标打卡，重视社交分享价值',
    type: 'score',
    options: [
      { score: 3, level: '高分', tags: '网红追随者、景点控、热门打卡爱好者' },
      { score: 2, level: '中分', tags: '偶尔打卡、选择性热门景点、拍照记录者' },
      { score: 1, level: '低分', tags: '自然漫游者、宁静体验者、不追热点' }
    ]
  },
  {
    key: 'depth',
    name: '5. 探索深度性',
    definition: '偏好文化沉浸、本地生活体验、非大众化目的地',
    type: 'score',
    options: [
      { score: 3, level: '高分', tags: '文化沉浸者、本地生活爱好者、历史探索者' },
      { score: 2, level: '中分', tags: '偶尔深入、轻度探索、局部体验者' },
      { score: 1, level: '低分', tags: '表面游览、走马观花、主要停留热门景点' }
    ]
  },
  {
    key: 'planning',
    name: '6. 计划严谨型',
    definition: '行前准备充分程度，行程安排的细致与灵活性',
    type: 'score',
    options: [
      { score: 3, level: '高分', tags: '旅行攻略达人、行程安排细致、时间管理高手' },
      { score: 2, level: '中分', tags: '基本规划、部分行程安排、灵活调整' },
      { score: 1, level: '低分', tags: '随性派、即兴安排、行程松散' }
    ]
  },
  {
    key: 'social',
    name: '7. 社交互动性',
    definition: '旅行中与他人互动、结伴、分享的意愿强度',
    type: 'score',
    options: [
      { score: 3, level: '高分', tags: '外向合群者、喜欢结伴旅行、社交达人' },
      { score: 2, level: '中分', tags: '偶尔交流、选择性互动、与熟人结伴' },
      { score: 1, level: '低分', tags: '独行者、偏向个人空间、沉浸自我体验' }
    ]
  },
  {
    key: 'comfort',
    name: '8. 舒适依赖性',
    definition: '对住宿、交通、服务品质的敏感度与要求',
    type: 'score',
    options: [
      { score: 3, level: '高分', tags: '高端住宿偏好、交通便利追求者、讲究品质' },
      { score: 2, level: '中分', tags: '性价比导向、基本舒适即可、偶尔追求高品质' },
      { score: 1, level: '低分', tags: '背包客、简约住宿、对环境要求低' }
    ]
  },
  {
    key: 'adventure',
    name: '9. 冒险挑战性',
    definition: '尝试新奇、刺激、非常规体验的意愿',
    type: 'score',
    options: [
      { score: 3, level: '高分', tags: '极限体验爱好者、刺激项目尝试者、勇于尝鲜' },
      { score: 2, level: '中分', tags: '偶尔尝试新活动、温和挑战者' },
      { score: 1, level: '低分', tags: '安全优先、保守稳健、偏好熟悉活动' }
    ]
  }
];

// 计算属性：当前显示的维度对象
const currentDimension = computed(() => dimensions[currentIndex.value]);

/**
 * 选择评估分值
 */
const selectScore = (key, score) => {
  tempScores[key] = score;
};

/**
 * 切换兴趣爱好选择
 */
const toggleInterest = (val) => {
  const index = tempScores.interests.indexOf(val);
  if (index > -1) {
    tempScores.interests.splice(index, 1);
  } else {
    tempScores.interests.push(val);
  }
};

/**
 * 下一步或提交评估
 */
const nextStep = async () => {
  // 基础信息验证
  if (currentDimension.value.type === 'basic_info') {
    if (!tempScores.age || !tempScores.gender || !tempScores.occupation) {
      uni.showToast({ title: '请填写完整信息', icon: 'none' });
      return;
    }
  }

  // 旅游偏好验证
  if (currentDimension.value.type === 'pref_info') {
    if (!tempScores.destType || !tempScores.travelStyle || !tempScores.accommodation) {
      uni.showToast({ title: '请填写完整偏好', icon: 'none' });
      return;
    }
  }

  // 兴趣爱好验证
  if (currentDimension.value.type === 'multi_select' && tempScores.interests.length === 0) {
    uni.showToast({ title: '请至少选择一个兴趣', icon: 'none' });
    return;
  }

  if (currentIndex.value < dimensions.length - 1) {
    currentIndex.value++;
  } else {
    // 提交保存至 Store
   const res = await userStore.savePersonalityAssessment(tempScores);
   if(res.success) {
    uni.showToast({
      title: '评估完成，已开启定制旅程',
      icon: 'success'
    });
        setTimeout(() => {
      uni.switchTab({
        url: '/pages/index/index'
      });
    }, 1000);
  } else {
    uni.showToast({
      title: res.message,
      icon: 'none'
    });

  }

  }
};

/**
 * 跳过评估
 */
const skipAssessment = () => {
  userStore.skipAssessment && userStore.skipAssessment();
  uni.showToast({ title: '已跳过评估', icon: 'none' });
  setTimeout(() => {
    uni.switchTab({
      url: '/pages/index/index'
    });
  }, 1000);
};
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: #FDFCF8;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
}

.assessment-header {
  padding: 40rpx 20rpx;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.assessment-title {
  font-size: 44rpx;
  font-weight: bold;
  color: #1E293B;
}

.skip-btn {
  font-size: 28rpx;
  color: #94A3B8;
}

.assessment-progress-text {
  font-size: 24rpx;
  color: #A5B4FC;
}

.assessment-card {
  background-color: #ffffff;
  border-radius: 48rpx;
  padding: 40rpx;
  box-shadow: 0 20rpx 50rpx rgba(0, 0, 0, 0.05);
  /* 卡片不再撑满整个屏幕，呈弹窗样式 */
  max-height: 75vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 40rpx;
}

.illustration-box {
	margin-right: 100rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: 16rpx;
  /* 在标题右侧显示的小插画容器 */
  width: 180rpx;
  height: 140rpx;
}

.traveler-img {
  max-width: 100%;
  height: 100%;
  width: 100%;
}

.dimension-container {
  /* 内部区域可以滚动，但卡片整体高度受限，避免页面出现整体滚动条 */
  overflow-y: auto;
  max-height: calc(75vh - 220rpx);
}

.dimension-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.dimension-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #1E293B;
  display: block;
  margin-bottom: 30rpx;
}

.dimension-desc {
  font-size: 26rpx;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 40rpx;
  display: block;
}

.form-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.field-label {
  font-size: 26rpx;
  color: #94A3B8;
  margin-bottom: 16rpx;
  display: block;
}

.field-input {
  background-color: #F8FAFC;
  height: 90rpx;
  border-radius: 24rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
}

.select-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.select-opt-item {
  padding: 16rpx 36rpx;
  background-color: #ffffff;
  border-radius: 16rpx;
  font-size: 26rpx;
  color: #94A3B8;
  border: 2rpx solid #F1F5F9;
}

.select-opt-item.opt-active {
  background-color: #ffffff;
  border-color: #8B5CF6;
  color: #8B5CF6;
}

.interest-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24rpx;
}

.interest-item {
  height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  border-radius: 16rpx;
  border: 2rpx solid #F1F5F9;
  font-size: 28rpx;
  color: #94A3B8;
}

.interest-active {
  border-color: #8B5CF6;
  color: #8B5CF6;
}

.score-section {
  padding-top: 20rpx;
}

.segment-selector {
  display: flex;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.segment-item {
  flex: 1;
  height: 12rpx;
  background-color: #F1F5F9;
  border-radius: 6rpx;
}

.segment-active {
  background-color: #8B5CF6;
}

.segment-labels {
  display: flex;
  justify-content: space-between;
}

.seg-label {
  font-size: 24rpx;
  color: #CBD5E1;
}

.submit-btn {
  width: 100%;
  height: 100rpx;
  background-color: #1E293B;
  color: #ffffff;
  border-radius: 50rpx;
  font-size: 32rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30rpx;
}

.page-indicator {
  display: flex;
  justify-content: center;
  gap: 12rpx;
  padding-bottom: 40rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background-color: #E2E8F0;
}

.dot-active {
  background-color: #8B5CF6;
  width: 24rpx;
  border-radius: 6rpx;
}

/* 响应式媒体查询：小屏优化 */
@media (max-width: 420px) {
  .container { padding: 24rpx; }
  .assessment-header { padding: 24rpx 12rpx; }
  .assessment-card { padding: 24rpx; border-radius: 24rpx; box-shadow: 0 12rpx 30rpx rgba(0,0,0,0.04); box-sizing: border-box;}
  .assessment-title { font-size: 36rpx; }
  .skip-btn { font-size: 24rpx; }
  .illustration-box { justify-content: center; margin-bottom: 12rpx; width: 180rpx; }
  .traveler-img { max-width: 100%; width: 100%; }
  .dimension-name { font-size: 32rpx; margin-bottom: 20rpx; }
  .field-input { height: 80rpx; font-size: 26rpx; }
  .interest-item { height: 72rpx; font-size: 26rpx; }
  .submit-btn { height: 88rpx; font-size: 30rpx; }
  .dimension-container { max-height: calc(100vh - 320rpx); }
}

/* 中等屏幕优化 */
@media (min-width: 421px) and (max-width: 768px) {
  .container { padding: 30rpx; }
  .assessment-card { padding: 32rpx; }
  .illustration-box { width: 120rpx; }
  .traveler-img { max-width: 100%; width: 100%; }
  .dimension-container { max-height: calc(100vh - 360rpx); }
}
</style>
