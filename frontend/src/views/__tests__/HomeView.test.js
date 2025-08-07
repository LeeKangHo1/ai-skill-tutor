// frontend/src/views/__tests__/HomeView.test.js
// HomeView.vue 컴포넌트 테스트

import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import HomeView from '../HomeView.vue'

describe('HomeView.vue', () => {
  it('홈 뷰 컴포넌트가 존재한다', () => {
    const wrapper = shallowMount(HomeView)
    expect(wrapper.exists()).toBe(true)
  })

  it('홈 뷰에 필요한 클래스들이 존재한다', () => {
    const wrapper = shallowMount(HomeView)
    expect(wrapper.find('.home-view').exists()).toBe(true)
  })
})