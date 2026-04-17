<template>
	<view class="page-container" :class="{'scrolled':isscrolled}">
		   <scroll-view 
      scroll-y 
      class="scroll-view" 
      @scroll="onScroll"
      :style="{ height: windowHeight + 'px' }"
      scroll-with-animation
    >
		<!-- 顶部 hero 区块 -->
		<view class="hero">
			<view class="hero-content" :style="{ paddingTop: statusBarHeight + 'px' }">
				<!-- 顶部编辑按钮 -->
				<view class="top-hero">
					<view class="edit-btn" @click="editProfile">
						<view class="edit-img"></view>
						<text>编辑资料</text>
					</view>
				</view>
				
				<!-- 用户信息 -->
				<view class="hero-top-row">
					<view class="hero-left">
						<image class="avatar" :src="userStore.userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill" />
						<view class="user-info">
							<text class="username">{{ userStore.userInfo.username || '未登录' }}</text>
							<text class="user-id">ID: {{ userStore.userInfo.userId || '—' }}</text>
						</view>
					</view>
					<view class="hero-likes">
						<text>获赞数</text>
						<text class="likes-count">{{ likes }}</text>
					</view>
				</view>
			</view>
			<!-- 渐变遮罩层 -->
			<view class="hero-gradient"></view>
		</view>

		<!-- 页面主体内容 -->
		<view class="page-body">
			<!-- 性格评估部分 -->
			<view class="characteristics">
				<view class="section-header">
					<view class="section-title">性格评估</view>
					<view class="section-subtitle">基于您的旅行偏好分析</view>
				</view>
				<!-- 当性格数据全为0时显示提示信息，否则显示Canvas组件 -->
				<view v-if="!isAssessmentComplete" class="no-assessment">
					<text class="no-assessment-text">抱歉，暂未完成偏好分析</text>
				</view>
				<Canvas v-else />
				<view class="radar-info" v-if="isAssessmentComplete">
					<view class="info-item" v-for="(score, key) in userStore.userInfo.personalityScores" :key="key">
						<!-- 简单的映射显示中文 -->
						<text class="info-label">{{ getLabel(key) }}</text>
						<text class="info-value">{{ score }}</text>
					</view>
				</view>
			</view>

			<!-- 旅行笔记部分 -->
			  <view class="tougao">
				<view class="tougao-header" :class="{ 'sticky-header': isSticky }" :style="stickyStyle">
					<view class="tougao-title">旅行笔记</view>
					<view class="search"></view>
				</view>
				
				<view class="tougao-main">
					<view class="tougao-item" v-for="note in notes" :key="note.id">
						<!-- 图片区域 -->
						<view class="note-image-box">
							<image v-if="note.image" :src="note.image" class="note-image" mode="aspectFill" />
						</view>
						<!-- 内容区域 -->
						<view class="note-content">
							<text class="note-text">{{ note.title }}</text>
							<view class="note-footer">
								<view class="author-info">
									<text class="author-name ">{{ note.date }}</text>
								</view>
								<view class="fascinating">
									<view class="fasci-img"></view>
								    <text class="note-likes">{{ note.likes }}</text>
								</view>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		   </scroll-view>
	</view>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue';
import { useUserStore } from '@/store/user.js';
import Canvas from '../../components/Canvas.vue';

// 状态栏高度
const statusBarHeight = ref(0);
const windowHeight = ref(0);
const isSticky = ref(false);
const heroHeight = ref(0);
const characteristicsHeight = ref(0);
const isscrolled = ref(false);
const somheight = ref(0); // 添加缺失的变量定义
// 模拟笔记数据
const notes = [
  { id: 1, title: "小圆的大厂前端辅导v2.0", image: "https://picsum.photos/400/600?random=1", likes: 274, date: "2024-12-13", author: "前端小圆" },
  { id: 2, title: "给零基础找前端实习的同学一个大概的参考", image: "https://picsum.photos/400/500?random=2", likes: 766, date: "2024-08-09", author: "前端小圆" },
  { id: 3, title: "27届前端中大厂暑期实习面经", image: "https://picsum.photos/400/700?random=3", likes: 59, date: "昨天", author: "前端小圆" },
  { id: 4, title: "前端面试中Harness Engineering会问些什么", image: "https://picsum.photos/400/550?random=4", likes: 108, date: "2天前", author: "前端小圆" },
  { id: 5, title: "Shopee SSC 前端实习一面", image: "https://picsum.photos/400/650?random=5", likes: 86, date: "3天前", author: "前端小圆" },
  { id: 6, title: "美团暑期二面真实面经分享", image: "https://picsum.photos/400/520?random=6", likes: 132, date: "4天前", author: "前端小圆" }
];

// 简单的字段映射辅助函数
const getLabel = (key) => {
	const map = {
		checkIn: '打卡导向型',
		depth: '探索深度型',
		planning: '计划严谨型',
		social: '社交互动型',
		comfort: '舒适依赖型',
		adventure: '冒险挑战型'
	};
	return map[key] || key;
};

// 计算属性：判断性格数据是否全为0
const isAssessmentComplete = computed(() => {
	if (!userStore.userInfo || !userStore.userInfo.personalityScores) {
		return false;
	}
	const scores = Object.values(userStore.userInfo.personalityScores);
	return scores.some(score => score > 0);
});

onMounted(() => {

	try {
		const sys = uni.getSystemInfoSync();
		windowHeight.value = sys.windowHeight;
		statusBarHeight.value = sys.statusBarHeight || 44;

		nextTick(()=>{
			const query=uni.createSelectorQuery();
			query.select('.hero').boundingClientRect()
			query.exec((res)=>{
				if(res&&res[0]){
					heroHeight.value=res[0].height;
					somheight.value=heroHeight.value+characteristicsHeight.value;
				}
			})
			query.select('.characteristics').boundingClientRect()
			query.exec((res)=>{
				if(res&&res[0]){
					characteristicsHeight.value=res[0].height;
					somheight.value=heroHeight.value+characteristicsHeight.value;
				}
			})
		})
	} catch (e) {}
});
const onScroll = (e) => {
  const scrollTop = e.detail.scrollTop;
  // 直接使用两个高度的和，Vue 会自动监听响应式变化
  const threshold = heroHeight.value + characteristicsHeight.value;
  
  // 只有当滚动到足够远时才触发吸顶
  if (threshold > 0 && scrollTop >= threshold - 100) {
    isSticky.value = true;
    // 当滚动到笔记部分时，设置状态栏背景为白色
    isscrolled.value=true;
  } else {
    isSticky.value = false;
    // 当滚动到其他部分时，设置状态栏背景为与body相同的颜色
    isscrolled.value=false;
  }
};
const userStore = useUserStore();
const likes = ref(1024); // 模拟一个获赞数

const editProfile = () => {
	uni.showToast({ title: '编辑资料', icon: 'none' });
};
const stickyStyle = computed(()=>{
	if(isSticky.value){
		return {
			position: 'sticky',
			top: statusBarHeight.value + 'px',
			width: '100%',
			maxWidth: '1200rpx',
			marginLeft: 'auto',
			marginRight: 'auto',
			zIndex: 1000,
			backgroundColor:'rgb(250, 250, 250)',
		    boxShadow: '0 4rpx 20rpx rgba(0, 0, 0, 0.05)', // 吸顶时加个阴影更有层次感
			paddingTop: '20rpx',
			paddingBottom: '20rpx'
		}
	}
	 return {};
});
</script>

<style scoped>
.page-container {
  background-color: #ffffff; /* 👈 强制整个页面白底 */
  min-height: 100vh;
  /* 不要设 transparent！ */
}

.page-container.scrolled {
  background-color: #ffffff; /* 滚动后变为白色 */
}
body {
	background-color: rgb(250, 250, 250);
}
.scroll-view {
	width: 100%;
	overflow: hidden;
	-webkit-overflow-scrolling: touch; /* 启用惯性滚动 */
}

/* --- Hero 区域样式 --- */
.hero {
  width: 100%;
  min-height: 33.33vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-image: url('/static/背景.png'); /* 请确保图片存在 */
  background-size: cover;
  background-position: center;
  position: relative;
}

.hero-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 250rpx;
  background: linear-gradient(to bottom, transparent 0%, rgba(255, 255, 255, 0.3) 50%, rgba(255, 255, 255, 0.95) 100%);
  z-index: 1;
}

.hero-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 0 30rpx;
  box-sizing: border-box;
  gap: 20rpx;
}

.top-hero {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  box-sizing: border-box;
}

.edit-btn {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(4px);
  color: #fff;
  padding: 10rpx 20rpx;
  border-radius: 18rpx;
  font-size: 24rpx;
}

.edit-img {
  width: 33rpx;
  height: 33rpx;
  background-image: url('/static/bianji.png'); /* 请确保图片存在 */
  background-size: cover;
  margin-right: 10rpx;
}

.hero-top-row {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10rpx;
}

.hero-left {
  display: flex;
  align-items: center;
}

.avatar {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #eee;
  border: 2rpx solid rgba(255,255,255,0.5);
}

.user-info {
  display: flex;
  flex-direction: column;
  margin-left: 20rpx;
}

.username {
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.2);
}

.user-id {
  color: rgba(255, 255, 255, 0.9);
  font-size: 24rpx;
  margin-top: 6rpx;
}

.hero-likes {
  display: flex;
  align-items: center;
  color: #fff;
  font-size: 26rpx;
  background: rgba(0,0,0,0.1);
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  width: fit-content;
}

.likes-count {
  color: #ffd54f;
  font-weight: 700;
  margin-left: 10rpx;
  font-size: 28rpx;
}

/* --- 页面主体 --- */
.page-body {
  padding: 20rpx 0 0 0;
  /* background-color: rgb(250, 250, 250); */
  padding-bottom: 100rpx; /* 底部留白 */
}

/* --- 性格评估卡片 --- */
.characteristics {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  padding: 10rpx 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.section-header {
  margin-bottom: 25rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1E293B;
}

.section-subtitle {
  font-size: 24rpx;
  color: #64748B;
  margin-top: 5rpx;
}

.radar-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 20rpx;
  background-color: #F9FAFB;
  border-radius: 12rpx;
  border: 1rpx solid #f0f0f0;
}

.info-label {
  font-size: 24rpx;
  color: #64748B;
}

.info-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #8B5CF6;
}

/* 未评估提示样式 */
.no-assessment {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100rpx;
  background-color: #F9FAFB;
  border-radius: 12rpx;
}

.no-assessment-text {
  font-size: 28rpx;
  color: #64748B;
  text-align: center;
}

/* --- 旅行笔记 (瀑布流风格) --- */
.tougao {
  width: 100%;
  display: flex;
  padding: 10rpx 0rpx 10rpx 0;
  flex-direction: column;
  box-sizing: border-box;
}

.tougao-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx 20rpx;
  background-color: rgb(250, 250, 250);
  border-bottom: 1rpx solid #eee;
  margin-bottom: 10rpx;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 1200rpx;
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}

.tougao-header.sticky-header {
  padding: 20rpx 10rpx;
  margin-bottom: 0;
  width: 100%;
  max-width: 1200rpx;
  margin-left: auto;
  margin-right: auto;
  position: sticky;
}

.tougao-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.search {
  width: 40rpx;
  height: 40rpx;
  background-image: url('/static/sousuo.png'); /* 请确保图片存在 */
  background-size: cover;
  background-position: center;
}

/* 网格布局核心 */
.tougao-main {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 默认两列 */
  gap: 20rpx;
  padding: 0 20rpx 0 20rpx;
  box-sizing: border-box;
  padding-bottom: 20rpx;
}

/* 单个笔记卡片 */
.tougao-item {
  background-color: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  transition: transform 0.2s;
  display: flex;
  flex-direction: column;
}

.tougao-item:active {
  transform: scale(0.98);
}

.note-image-box {
  width: 100%;
  height: 300rpx; /* 固定高度，或者使用 aspect-ratio */
  background-color: #f0f0f0;
}

.note-image {
  width: 100%;
  height: 100%;
  display: block;
}

.note-content {
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: space-between;
}

.note-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.5;
  /* 多行文本省略 */
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  margin-bottom: 15rpx;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.author-info {
  display: flex;
  align-items: center;
  overflow: hidden;
}

.mini-avatar {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  margin-right: 10rpx;
  background-color: #eee;
}

.author-name {
  font-size: 22rpx;
  color: #999;
  max-width: 150rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-likes {
  font-size: 22rpx;
  color: #999;
}

.fascinating {
  display: flex;
  align-items: center;
  gap:5rpx;

}

.fasci-img {
   height:30rpx ;
   width: 30rpx;
   background-image: url('/static/cpxihuan.png');
   background-position: center;
   background-size: contain;
   background-repeat: no-repeat;
}
/* --- 响应式适配 --- */
@media screen and (min-width: 768px) {
  .tougao-main {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media screen and (min-width: 1024px) {
  .tougao-main {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>