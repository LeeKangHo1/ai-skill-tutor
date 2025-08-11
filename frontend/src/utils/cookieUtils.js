// frontend/src/utils/cookieUtils.js
// 쿠키 관련 유틸리티 함수들

/**
 * 쿠키 값을 가져오는 함수
 * @param {string} name - 쿠키 이름
 * @returns {string|null} - 쿠키 값 또는 null
 */
export function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }
  return null
}

/**
 * 쿠키가 존재하는지 확인하는 함수
 * @param {string} name - 쿠키 이름
 * @returns {boolean} - 쿠키 존재 여부
 */
export function hasCookie(name) {
  return getCookie(name) !== null
}

/**
 * refresh_token 쿠키가 존재하는지 확인하는 함수
 * @returns {boolean} - refresh_token 쿠키 존재 여부
 */
export function hasRefreshToken() {
  return hasCookie('refresh_token')
}

/**
 * 쿠키를 삭제하는 함수 (클라이언트 사이드에서는 만료시킴)
 * @param {string} name - 쿠키 이름
 * @param {string} path - 쿠키 경로 (기본값: '/')
 */
export function deleteCookie(name, path = '/') {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${path};`
}

/**
 * 모든 인증 관련 쿠키를 삭제하는 함수
 */
export function clearAuthCookies() {
  deleteCookie('refresh_token')
  // 필요시 다른 인증 관련 쿠키도 추가
}