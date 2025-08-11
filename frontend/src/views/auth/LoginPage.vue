<!-- src/views/LoginPage.vue -->

<template>
  <div class="login-page">
    <!-- 배경 및 레이아웃 -->
    <div class="page-container">
      <!-- 왼쪽 브랜딩 영역 -->
      <div class="branding-section">
        <div class="branding-content">
          <div class="logo-container">
            <i class="fas fa-robot brand-icon"></i>
            <h1 class="brand-title">AI 활용법 학습 튜터</h1>
          </div>
          <p class="brand-description">
            AI를 활용한 맞춤형 학습으로<br>
            당신의 AI 활용 능력을 키워보세요
          </p>
          <div class="feature-list">
            <div class="feature-item">
              <i class="fas fa-check-circle feature-icon"></i>
              <span>개인 맞춤형 학습 경로</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-check-circle feature-icon"></i>
              <span>실시간 AI 상호작용</span>
            </div>
            <div class="feature-item">
              <i class="fas fa-check-circle feature-icon"></i>
              <span>단계별 실습 프로젝트</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 오른쪽 폼 영역 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 탭 네비게이션 -->
          <div class="tab-navigation">
            <button
              type="button"
              class="tab-button"
              :class="{ active: currentTab === 'login' }"
              @click="switchTab('login')"
            >
              로그인
            </button>
            <button
              type="button"
              class="tab-button"
              :class="{ active: currentTab === 'register' }"
              @click="switchTab('register')"
            >
              회원가입
            </button>
          </div>

          <!-- 폼 컨텐츠 -->
          <div class="form-content">
            <!-- 로딩 오버레이 -->
            <div v-if="isPageLoading" class="loading-overlay">
              <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">로딩 중...</span>
                </div>
                <p class="loading-text">{{ loadingMessage }}</p>
              </div>
            </div>

            <!-- 로그인 폼 -->
            <Transition name="fade" mode="out-in">
              <LoginForm
                v-if="currentTab === 'login'"
                key="login-form"
                @login-success="handleLoginSuccess"
                @switch-to-register="switchTab('register')"
                @forgot-password="handleForgotPassword"
              />
            </Transition>

            <!-- 회원가입 폼 -->
            <Transition name="fade" mode="out-in">
              <RegisterForm
                v-if="currentTab === 'register'"
                key="register-form"
                @register-success="handleRegisterSuccess"
                @switch-to-login="switchTab('login')"
                @show-terms="handleShowTerms"
                @show-privacy="handleShowPrivacy"
              />
            </Transition>
          </div>
        </div>
      </div>
    </div>

    <!-- 성공 알림 모달 -->
    <div v-if="showSuccessModal" class="modal-overlay" @click="closeSuccessModal">
      <div class="modal-content success-modal" @click.stop>
        <div class="modal-header">
          <div class="success-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <h3 class="modal-title">{{ successModalTitle }}</h3>
        </div>
        <div class="modal-body">
          <p>{{ successModalMessage }}</p>
          <div class="user-info" v-if="successUserInfo">
            <p><strong>사용자명:</strong> {{ successUserInfo.username }}</p>
            <p><strong>유형:</strong> {{ getUserTypeText(successUserInfo.user_type) }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="proceedToNext">
            {{ proceedButtonText }}
          </button>
        </div>
      </div>
    </div>

    <!-- 약관/개인정보처리방침 모달 -->
    <div v-if="showTermsModal" class="modal-overlay" @click="closeTermsModal">
      <div class="modal-content terms-modal" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ termsModalTitle }}</h3>
          <button type="button" class="modal-close" @click="closeTermsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="terms-content">
            {{ termsContent }}
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeTermsModal">
            확인
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import LoginForm from '../../components/auth/LoginForm.vue'
import RegisterForm from '../../components/auth/RegisterForm.vue'

export default {
  name: 'LoginPage',
  components: {
    LoginForm,
    RegisterForm
  },
  
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()

    // 반응형 데이터
    const currentTab = ref('login')
    const isPageLoading = ref(false)
    const loadingMessage = ref('')
    const showSuccessModal = ref(false)
    const successModalTitle = ref('')
    const successModalMessage = ref('')
    const successUserInfo = ref(null)
    const redirectPath = ref('/dashboard')
    const showTermsModal = ref(false)
    const termsModalTitle = ref('')
    const termsContent = ref('')

    // 계산된 속성
    const proceedButtonText = computed(() => {
      if (successUserInfo.value?.diagnosis_completed) {
        return '대시보드로 이동'
      } else {
        return '진단 시작하기'
      }
    })

    // 메서드들
    const switchTab = (tab) => {
      if (tab !== currentTab.value) {
        currentTab.value = tab
      }
    }

    const getUserTypeText = (userType) => {
      const typeMap = {
        'beginner': 'AI 입문자',
        'advanced': '실무 응용형',
        'unassigned': '미설정'
      }
      return typeMap[userType] || '알 수 없음'
    }

    const handleLoginSuccess = async (data) => {
      isPageLoading.value = true
      loadingMessage.value = '로그인 처리 중...'

      try {
        // 성공 메시지 표시 후 홈으로 이동
        successModalTitle.value = '로그인 성공!'
        successModalMessage.value = '환영합니다!'
        successUserInfo.value = data.user
        redirectPath.value = '/'
        
        // 약간의 지연 후 홈으로 이동
        setTimeout(() => {
          isPageLoading.value = false
          router.push('/')
        }, 1000)
        
      } catch (error) {
        console.error('로그인 후 처리 오류:', error)
        isPageLoading.value = false
        
        // 에러가 발생해도 홈으로 이동
        router.push('/')
      }
    }

    const handleRegisterSuccess = async (data) => {
      isPageLoading.value = true
      loadingMessage.value = '회원가입 처리 중...'

      try {
        // 성공 메시지 표시 후 홈으로 이동
        successModalTitle.value = '회원가입 성공!'
        successModalMessage.value = '계정이 성공적으로 생성되었습니다!'
        successUserInfo.value = data.user
        redirectPath.value = '/'
        
        // 약간의 지연 후 홈으로 이동
        setTimeout(() => {
          isPageLoading.value = false
          router.push('/')
        }, 1500)
        
      } catch (error) {
        console.error('회원가입 후 처리 오류:', error)
        isPageLoading.value = false
        
        // 에러가 발생해도 홈으로 이동
        router.push('/')
      }
    }

    const handleForgotPassword = () => {
      // 비밀번호 찾기 기능 (향후 구현)
      alert('비밀번호 찾기 기능은 준비 중입니다.')
    }

    const handleShowTerms = () => {
      termsModalTitle.value = '이용약관'
      termsContent.value = `
        AI 활용법 학습 튜터 이용약관

        제1조 (목적)
        본 약관은 AI 활용법 학습 튜터 서비스의 이용과 관련하여 회사와 이용자 간의 권리와 의무를 규정함을 목적으로 합니다.

        제2조 (서비스의 내용)
        1. AI 기반 맞춤형 학습 서비스 제공
        2. 학습 진도 관리 및 평가 서비스
        3. 기타 관련 부가 서비스

        제3조 (이용계약의 성립)
        1. 이용신청자가 회원가입 양식에 필요사항을 기입하고 본 약관에 동의한다는 의사표시를 한 경우
        2. 회사가 이용신청을 승낙한 경우

        제4조 (개인정보보호)
        회사는 관련 법령이 정하는 바에 따라 이용자의 개인정보를 보호하기 위해 노력합니다.

        (이용약관 전문은 실제 서비스에서 법무 검토를 거쳐 작성되어야 합니다.)
      `
      showTermsModal.value = true
    }

    const handleShowPrivacy = () => {
      termsModalTitle.value = '개인정보처리방침'
      termsContent.value = `
        AI 활용법 학습 튜터 개인정보처리방침

        1. 개인정보의 처리 목적
        - 회원 가입 및 관리
        - 학습 서비스 제공
        - 학습 진도 및 성과 관리

        2. 개인정보의 처리 및 보유 기간
        - 회원탈퇴 시까지 또는 법령에서 정한 보존기간

        3. 처리하는 개인정보의 항목
        - 필수: 이메일, 로그인ID, 비밀번호, 사용자명
        - 선택: 학습 선호도, 진도 정보

        4. 개인정보의 제3자 제공
        원칙적으로 이용자의 개인정보를 제3자에게 제공하지 않습니다.

        5. 개인정보 처리 위탁
        더 나은 서비스 제공을 위해 일부 업무를 외부에 위탁할 수 있습니다.

        (개인정보처리방침 전문은 실제 서비스에서 법무 검토를 거쳐 작성되어야 합니다.)
      `
      showTermsModal.value = true
    }

    const closeSuccessModal = () => {
      showSuccessModal.value = false
    }

    const closeTermsModal = () => {
      showTermsModal.value = false
    }

    const proceedToNext = () => {
      showSuccessModal.value = false
      router.push(redirectPath.value)
    }

    // URL 쿼리 파라미터에 따른 초기 탭 설정
    const initializeFromQuery = () => {
      if (route.query.tab === 'register') {
        currentTab.value = 'register'
      } else {
        currentTab.value = 'login'
      }
    }

    // 탭 변경 시 URL 업데이트
    watch(currentTab, (newTab) => {
      if (newTab !== route.query.tab) {
        router.replace({ 
          query: { 
            ...route.query, 
            tab: newTab === 'login' ? undefined : newTab 
          } 
        })
      }
    })

    // 컴포넌트 마운트 시 초기화
    onMounted(() => {
      initializeFromQuery()
    })

    return {
      currentTab,
      isPageLoading,
      loadingMessage,
      showSuccessModal,
      successModalTitle,
      successModalMessage,
      successUserInfo,
      showTermsModal,
      termsModalTitle,
      termsContent,
      proceedButtonText,
      switchTab,
      getUserTypeText,
      handleLoginSuccess,
      handleRegisterSuccess,
      handleForgotPassword,
      handleShowTerms,
      handleShowPrivacy,
      closeSuccessModal,
      closeTermsModal,
      proceedToNext
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.page-container {
  width: 100%;
  max-width: 1200px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 600px;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.branding-section {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  position: relative;
}

.branding-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.branding-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.logo-container {
  margin-bottom: 2rem;
}

.brand-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.9);
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0;
  line-height: 1.2;
}

.brand-description {
  font-size: 1.25rem;
  margin: 1.5rem 0 2.5rem;
  opacity: 0.9;
  line-height: 1.6;
}

.feature-list {
  text-align: left;
  max-width: 300px;
  margin: 0 auto;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.feature-icon {
  margin-right: 0.75rem;
  color: #10b981;
  font-size: 1.25rem;
}

.form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
}

.form-container {
  width: 100%;
  max-width: 450px;
}

.tab-navigation {
  display: flex;
  margin-bottom: 2rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 0.25rem;
}

.tab-button {
  flex: 1;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.tab-button.active {
  background: white;
  color: #0d6efd;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-button:hover:not(.active) {
  color: #495057;
  background: rgba(255, 255, 255, 0.5);
}

.form-content {
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 0.5rem;
}

.loading-spinner {
  text-align: center;
}

.loading-text {
  margin-top: 1rem;
  color: #6c757d;
  font-weight: 500;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

/* 전환 애니메이션 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
}

.success-modal .modal-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
}

.success-icon {
  font-size: 4rem;
  color: #10b981;
  margin-bottom: 1rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0;
  color: #333;
}

.modal-body {
  padding: 1rem 2rem;
}

.user-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.user-info p {
  margin-bottom: 0.5rem;
}

.user-info p:last-child {
  margin-bottom: 0;
}

.modal-footer {
  padding: 1rem 2rem 2rem;
  text-align: center;
}

.terms-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem 1rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.modal-close:hover {
  color: #333;
}

.terms-content {
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-line;
  line-height: 1.6;
  color: #555;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  border-radius: 0.375rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.btn-primary {
  color: #fff;
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover {
  background-color: #0b5ed7;
  border-color: #0a58ca;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #5c636a;
  border-color: #565e64;
}

.visually-hidden {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .page-container {
    grid-template-columns: 1fr;
    max-width: 100%;
    margin: 0;
    border-radius: 0;
  }

  .branding-section {
    padding: 2rem 1rem;
  }

  .brand-title {
    font-size: 2rem;
  }

  .brand-description {
    font-size: 1.1rem;
  }

  .form-section {
    padding: 1.5rem 1rem;
  }
}

@media (max-width: 576px) {
  .login-page {
    padding: 0;
  }

  .branding-section {
    padding: 1.5rem 1rem;
  }

  .brand-title {
    font-size: 1.75rem;
  }

  .feature-item {
    font-size: 1rem;
  }

  .modal-content {
    margin: 1rem;
    max-width: calc(100% - 2rem);
  }
}
</style>