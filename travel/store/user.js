import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import { token } from '../ultis/api';
/**
 * 用户全局状态管理 Store
 * 使用 Pinia Setup Store 语法
 */
export const useUserStore = defineStore('user', () => {
  // 共享的用户基础信息及评估状态
  const userInfo = reactive({
    username: '',                   // 用户名
    phone: '',                      // 手机号
    isLoggedIn: false,              // 登录状态
    avatar: '',                     // 头像链接
    hasCompletedAssessment: false,  // 标记是否已完成性格评估（首页弹窗触发条件）
    personalityScores: {            // 性格评估六维分值（1-3分：低、中、高）
      checkIn: 0,   // 打卡导向性
      depth: 0,     // 探索深度性
      planning: 0,  // 计划严谨型
      social: 0,    // 社交互动性
      comfort: 0,   // 舒适依赖性
      adventure: 0  // 冒险挑战性
    }
  });

  // 模拟持久化存储的已注册用户列表（内存存储，刷新页面后重置）
  const registeredUsers = ref([]);

  /**
   * 注册逻辑
   * @param {Object} data - 包含用户名、密码、昵称、手机号的注册信息
   */
  const register = async(data) => {
    const { username, password, phone,confirmPassword } = data;
    const response=await uni.request({
      url:'/api/auth/register',
      method:'POST',
      data:{
        username,
        password,
        phone,
        confirmPassword
      }
    })
    if(response.data.code===200){
        return { success: true, message: '注册成功' };
    }

    else return { success: false, message: response.data.message || '注册失败' };
  };

  /**
   * 登录逻辑
   * @param {string} username - 用户名
   * @param {string} password - 密码
   */
  const login = async(username, password) => {
    const response=await uni.request({
      url:'/api/auth/login',
      method:'POST',
      Header:token(),
      data:{
        username,
        password
      }
    })
    if(response.data.code===200){
        localStorage.setItem('token',response.data.data.token);
        userInfo.username = username;
        userInfo.userId=response.data.data.userId;
        userInfo.phone = response.data.data.phone;
        userInfo.hasCompletedAssessment = response.data.data.hasCompletedAssessment;
        return { success: true, message: '登录成功' };
    }
    else {
        return { success: false, message: response.data.message || '登录失败' };
    }
  };

  /**
   * 保存性格评估结果
   * @param {Object} scores - 六维评估分值对象
   */
  const savePersonalityAssessment = async(scores) => {
    
	  console.log(scores);
    // 更新当前内存状态
    userInfo.personalityScores = { ...scores };
    userInfo.hasCompletedAssessment = true;
    const response=await uni.request({
 url:'/api/assessment/submit',
 method:'POST',
 Header:token(),
 data:{
   age:scores.age,
   gender:scores.gender,
   occupation:scores.occupation,
   travelStyle:scores.travelStyle,
   destType:scores.destType,
   accommodation:scores.accommodation,
   intersts:scores.intersts,
   checkIn:scores.checkIn,
   depth:scores.depth,
   planning:scores.planning,
   scial:scores.social,
   comfort:scores.comfort,
   adventure:scores.adventure
 }
    })
    if(response.data.code===200){
        return { success: true, message: '评估完成' };
    }
    return { success: false, message: response.data.message || '评估提交失败' };
  };

  /**
   * 跳过评估：仅标记完成，不修改分值
   */
  const skipAssessment = () => {
    userInfo.hasCompletedAssessment = true;
    return { success: true, message: '已跳过评估' };
  };

  /**
   * 退出登录逻辑
   * 清除用户信息及登录/评估标记
   */
  const logout = () => {
    userInfo.username = '';
    userInfo.phone = '';
    userInfo.isLoggedIn = false;
  };

  //获取画像接口
  const getProfile = async() => {
   const response=await uni.request({
    method:'GET',
    header:token(),
    url:'api/user/profile'
   })
   console.log(response);
    if(response.data.code===200){
    userInfo.personalityScores=response.data.data.personalityScores;
    userInfo.hasCompletedAssessment=response.data.data.hasCompletedAssessment;
    return { success: true, message: '获取画像成功' };  
    }
  else {
    userInfo.personalityScores.adventure=0;
    userInfo.personalityScores.checkIn=0;
    userInfo.personalityScores.comfort=0;
    userInfo.personalityScores.depth=0;
    userInfo.personalityScores.planning=0;
    userInfo.personalityScores.social=0;
    return { success: false, message: response.data.message || '获取画像失败' };
  }
  }

  return {
    userInfo,
    registeredUsers,
    register,
    login,
    savePersonalityAssessment,
    skipAssessment,
    logout,
    getProfile
  };
});