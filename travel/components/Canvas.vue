<template>
	<view class="canvas-container">
		<canvas 
			canvas-id="radarCanvas" 
			class="radar-canvas" 
			@tap="handleClick"
		></canvas>
		<view 
			v-if="showTooltip" 
			class="tooltip" 
			:style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
		>
			<text class="tooltip-label">{{ tooltipLabel }}</text>
			<text class="tooltip-value">{{ tooltipValue }}</text>
		</view>
	</view>
</template>

<script setup>
import { ref, onMounted, watch ,onUnmounted, getCurrentInstance} from 'vue';
import { useUserStore } from '@/store/user.js';

// 获取用户store
let userStore;
try {
	userStore = useUserStore();
} catch (error) {
	console.error('Failed to get userStore:', error);
	userStore = null;
}

// 确保userStore存在
if (!userStore) {
	userStore = {
		userInfo: {
			personalityScores: {
				checkIn: 0,
				depth: 0,
				planning: 0,
				social: 0,
				comfort: 0,
				adventure: 0
			}
		}
	};
} else {
	// 确保userInfo存在
	if (!userStore.userInfo) {
		userStore.userInfo = {
			personalityScores: {
				checkIn: 0,
				depth: 0,
				planning: 0,
				social: 0,
				comfort: 0,
				adventure: 0
			}
		};
	} else {
		// 确保personalityScores存在
		if (!userStore.userInfo.personalityScores) {
			userStore.userInfo.personalityScores = {
				checkIn: 0,
				depth: 0,
				planning: 0,
				social: 0,
				comfort: 0,
				adventure: 0
			};
		}
	}
}

// 性格评估六维数据
const personalityScores = ref(userStore.userInfo.personalityScores);

// 获取当前实例
const instance = getCurrentInstance();

// 雷达图配置
const labels = [
	{ key: 'checkIn', name: '打卡导向性' },
	{ key: 'depth', name: '探索深度性' },
	{ key: 'planning', name: '计划严谨型' },
	{ key: 'social', name: '社交互动性' },
	{ key: 'comfort', name: '舒适依赖性' },
	{ key: 'adventure', name: '冒险挑战性' }
];

// 工具提示相关
const showTooltip = ref(false);
const tooltipX = ref(0);
const tooltipY = ref(0);
const tooltipLabel = ref('');
const tooltipValue = ref('');

// 点击效果相关
const selectedPoint = ref(null);
const animationScale = ref(1);
const animationOpacity = ref(1);

// 绘制雷达图
const drawRadar = () => {
	// 获取canvas元素的实际尺寸
	const query = uni.createSelectorQuery().in(instance);
	query.select('.radar-canvas').boundingClientRect(data => {
		if (data) {
			const ctx = uni.createCanvasContext('radarCanvas');
			const canvasWidth = data.width;
			const canvasHeight = data.height;
			const centerX = canvasWidth / 2;
			const centerY = canvasHeight / 2;
			const radius = Math.min(centerX, centerY) * 0.8;
			const angle = (2 * Math.PI) / 6;
			
			// 清除画布
			ctx.clearRect(0, 0, canvasWidth, canvasHeight);
			
			// 绘制网格（紫色主题）
			ctx.setStrokeStyle('#e0cfff');
			ctx.setLineWidth(1);
			for (let i = 1; i <= 3; i++) {
				const r = (radius / 3) * i;
				ctx.beginPath();
				for (let j = 0; j < 6; j++) {
					const x = centerX + r * Math.cos(angle * j - Math.PI / 2);
					const y = centerY + r * Math.sin(angle * j - Math.PI / 2);
					if (j === 0) {
						ctx.moveTo(x, y);
					} else {
						ctx.lineTo(x, y);
					}
				}
				ctx.closePath();
				ctx.stroke();
			}
			
			// 绘制轴线（紫色主题）
			ctx.setStrokeStyle('#c099ff');
			ctx.setLineWidth(1);
			for (let i = 0; i < 6; i++) {
				const x = centerX + radius * Math.cos(angle * i - Math.PI / 2);
				const y = centerY + radius * Math.sin(angle * i - Math.PI / 2);
				ctx.beginPath();
				ctx.moveTo(centerX, centerY);
				ctx.lineTo(x, y);
				ctx.stroke();
			}
			
			// 绘制数据区域（紫色主题）
			ctx.setFillStyle('rgba(147, 51, 234, 0.4)'); // 紫色填充
			ctx.setStrokeStyle('#9333ea'); // 紫色边框
			ctx.setLineWidth(2);
			ctx.beginPath();
			for (let i = 0; i < 6; i++) {
				const score = personalityScores.value[labels[i].key] || 0;
				const r = (radius / 3) * score;
				const x = centerX + r * Math.cos(angle * i - Math.PI / 2);
				const y = centerY + r * Math.sin(angle * i - Math.PI / 2);
				if (i === 0) {
					ctx.moveTo(x, y);
				} else {
					ctx.lineTo(x, y);
				}
			}
			ctx.closePath();
			ctx.fill();
			ctx.stroke();
			
			// 绘制数据点（紫色主题）
			for (let i = 0; i < 6; i++) {
				const score = personalityScores.value[labels[i].key] || 0;
				const r = (radius / 3) * score;
				const x = centerX + r * Math.cos(angle * i - Math.PI / 2);
				const y = centerY + r * Math.sin(angle * i - Math.PI / 2);
				
				// 检查是否是选中的点
				if (selectedPoint.value === i) {
					// 选中的点：使用动画效果
					ctx.setFillStyle('#9333ea');
					ctx.globalAlpha = animationOpacity.value;
					const pointSize = 4 * animationScale.value;
					ctx.beginPath();
					ctx.arc(x, y, pointSize, 0, 2 * Math.PI);
					ctx.fill();
					
					// 绘制外圈光环
					ctx.setStrokeStyle('#9333ea');
					ctx.setLineWidth(2);
					ctx.beginPath();
					ctx.arc(x, y, pointSize + 3, 0, 2 * Math.PI);
					ctx.stroke();
					
					// 重置透明度
					ctx.globalAlpha = 1;
				} else {
					// 普通点
					ctx.setFillStyle('#9333ea');
					ctx.beginPath();
					ctx.arc(x, y, 4, 0, 2 * Math.PI);
					ctx.fill();
				}
			}
			
			// 添加立体效果 - 绘制阴影
			ctx.setFillStyle('rgba(147, 51, 234, 0.1)');
			ctx.beginPath();
			for (let i = 0; i < 6; i++) {
				const score = personalityScores.value[labels[i].key] || 0;
				const r = (radius / 3) * score;
				const x = centerX + r * Math.cos(angle * i - Math.PI / 2) + 5;
				const y = centerY + r * Math.sin(angle * i - Math.PI / 2) + 5;
				if (i === 0) {
					ctx.moveTo(x, y);
				} else {
					ctx.lineTo(x, y);
				}
			}
			ctx.closePath();
			ctx.fill();
			
			ctx.draw();
		}
	}).exec();
};

// 处理点击事件
const handleClick = (e) => {
	// 先隐藏之前的工具提示和重置选中状态
	showTooltip.value = false;
	selectedPoint.value = null;
	drawRadar();
	
	// 获取canvas元素的位置信息
	const query = uni.createSelectorQuery().in(instance);
	query.select('.radar-canvas').boundingClientRect(data => {
		if (data) {
			const touch = e.detail;
			// 计算相对于canvas的坐标
			const x = touch.x - data.left;
			const y = touch.y - data.top;
			
			// 检查是否点击到数据点
			checkTouchPoint(x, y);
		}
	}).exec();
};

// 检查是否触摸到数据点
const checkTouchPoint = (x, y) => {
	// 获取canvas元素的实际尺寸
	const query = uni.createSelectorQuery().in(instance);
	query.select('.radar-canvas').boundingClientRect(data => {
		if (data) {
			const canvasWidth = data.width;
			const canvasHeight = data.height;
			const centerX = canvasWidth / 2;
			const centerY = canvasHeight / 2;
			const radius = Math.min(centerX, centerY) * 0.8;
			const angle = (2 * Math.PI) / 6;
			const pointRadius = 15; // 增大触摸检测半径
			
			for (let i = 0; i < 6; i++) {
				const score = personalityScores.value[labels[i].key] || 0;
				const r = (radius / 3) * score;
				const pointX = centerX + r * Math.cos(angle * i - Math.PI / 2);
				const pointY = centerY + r * Math.sin(angle * i - Math.PI / 2);
				
				// 计算距离
				const distance = Math.sqrt(Math.pow(x - pointX, 2) + Math.pow(y - pointY, 2));
				
				if (distance <= pointRadius) {
					// 显示工具提示
					showTooltip.value = true;
					// 调整工具提示位置，确保在画布内
					tooltipX.value = x > centerX ? x - 120 : x + 10;
					tooltipY.value = y > centerY ? y - 60 : y - 40;
					tooltipLabel.value = `${labels[i].name}: ${score}`;
					tooltipValue.value = getScoreLevel(score);
					
					// 记录选中的点
					selectedPoint.value = i;
					
					// 执行点击动画
					runClickAnimation();
					
					// 3秒后自动隐藏工具提示和重置选中状态
					setTimeout(() => {
						showTooltip.value = false;
						selectedPoint.value = null;
						drawRadar();
					}, 3000);
					
					return;
				}
			}
			
			// 没有触摸到任何点
			showTooltip.value = false;
			selectedPoint.value = null;
		}
	}).exec();
};

// 执行点击动画
const runClickAnimation = () => {
	// 重置动画参数
	animationScale.value = 1;
	animationOpacity.value = 1;
	
	// 动画帧
	let frame = 0;
	const totalFrames = 20;
	
	const animate = () => {
		frame++;
		if (frame <= totalFrames) {
			// 计算动画进度
			const progress = frame / totalFrames;
			
			// 缩放动画：先放大后缩小
			if (progress < 0.5) {
				animationScale.value = 1 + progress * 0.6; // 放大到1.3
			} else {
				animationScale.value = 1.3 - (progress - 0.5) * 0.6; // 缩小回1
			}
			
			// 透明度动画：先变亮后恢复
			if (progress < 0.3) {
				animationOpacity.value = 1 + progress * 0.5; // 增加透明度
			} else {
				animationOpacity.value = 1.5 - (progress - 0.3) * 0.5; // 恢复正常
			}
			
			// 重新绘制
			drawRadar();
			
			// 继续动画
			requestAnimationFrame(animate);
		}
	};
	
	animate();
};

// 获取分数等级
const getScoreLevel = (score) => {
	switch (score) {
		case 1:
			return '等级：低';
		case 2:
			return '等级：中';
		case 3:
			return '等级：高';
		default:
			return '未知';
	}
};

// 监听store中数据变化，重新绘制
watch(() => userStore.userInfo.personalityScores, (newScores) => {
	personalityScores.value = newScores;
	drawRadar();
}, { deep: true });
let timer = null;

const resizeHandler = () => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    drawRadar();
  }, 100);
};
onMounted(() => {
  uni.onWindowResize(resizeHandler);
  // 初始化绘制雷达图
  drawRadar();
});

</script>

<style scoped>
.canvas-container {
	position: relative;
	width: 80%;
	max-width: 500rpx;
	height: 20vh; /* 屏幕高度的五分之二 */
	margin: 0 auto;
	display: flex;
	justify-content: center;
	align-items: center;
}

.radar-canvas {
	position: absolute;
	width: 100%;
	height: 100%;
}

.tooltip {
	position: absolute;
	background-color: rgba(0, 0, 0, 0.8);
	color: #fff;
	padding: 12rpx 16rpx;
	border-radius: 8rpx;
	font-size: 24rpx;
	z-index: 10;
	pointer-events: none;
	white-space: nowrap;
}

.tooltip-label {
	display: block;
	font-weight: 600;
	text-align: center;
}

.tooltip-value {
	display: block;
	font-size: 20rpx;
	margin-top: 8rpx;
	opacity: 0.9;
	text-align: center;
}
</style>