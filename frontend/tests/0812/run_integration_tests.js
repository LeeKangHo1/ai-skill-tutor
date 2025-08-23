// frontend/tests/0812/run_integration_tests.js
// 통합 테스트 실행 스크립트
// Vitest를 사용하여 전체 워크플로우 통합 테스트를 실행

import { execSync } from 'child_process'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

/**
 * 통합 테스트 실행 함수
 */
async function runIntegrationTests() {
  console.log('🚀 프론트엔드 학습 API 연동 통합 테스트 시작\n')
  
  const testFiles = [
    'integration_workflow_test.js'
  ]
  
  let totalTests = 0
  let passedTests = 0
  let failedTests = 0
  
  for (const testFile of testFiles) {
    console.log(`📋 실행 중: ${testFile}`)
    console.log('=' .repeat(50))
    
    try {
      const testPath = join(__dirname, testFile)
      const result = execSync(`npx vitest run ${testPath} --reporter=verbose`, {
        encoding: 'utf8',
        cwd: join(__dirname, '../../'),
        stdio: 'pipe'
      })
      
      console.log(result)
      
      // 결과 파싱 (간단한 방식)
      const lines = result.split('\n')
      const summaryLine = lines.find(line => line.includes('Test Files'))
      
      if (summaryLine) {
        const matches = summaryLine.match(/(\d+) passed/)
        if (matches) {
          const passed = parseInt(matches[1])
          passedTests += passed
          totalTests += passed
          console.log(`✅ ${testFile}: ${passed}개 테스트 통과\n`)
        }
      }
      
    } catch (error) {
      console.error(`❌ ${testFile} 실행 실패:`)
      console.error(error.stdout || error.message)
      failedTests++
      console.log('')
    }
  }
  
  // 최종 결과 출력
  console.log('=' .repeat(60))
  console.log('📊 통합 테스트 결과 요약')
  console.log('=' .repeat(60))
  console.log(`총 테스트 파일: ${testFiles.length}개`)
  console.log(`통과한 테스트: ${passedTests}개`)
  console.log(`실패한 테스트: ${failedTests}개`)
  console.log(`성공률: ${totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0}%`)
  
  if (failedTests === 0) {
    console.log('\n🎉 모든 통합 테스트가 성공적으로 완료되었습니다!')
  } else {
    console.log('\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.')
  }
  
  return {
    total: totalTests,
    passed: passedTests,
    failed: failedTests,
    success: failedTests === 0
  }
}

/**
 * 테스트 환경 검증
 */
function validateTestEnvironment() {
  console.log('🔍 테스트 환경 검증 중...')
  
  try {
    // Node.js 버전 확인
    const nodeVersion = process.version
    console.log(`Node.js 버전: ${nodeVersion}`)
    
    // Vitest 설치 확인
    execSync('npx vitest --version', { stdio: 'pipe' })
    console.log('✅ Vitest 설치 확인됨')
    
    // Vue Test Utils 확인
    try {
      execSync('npm list @vue/test-utils', { stdio: 'pipe' })
      console.log('✅ Vue Test Utils 설치 확인됨')
    } catch {
      console.warn('⚠️ Vue Test Utils가 설치되지 않았을 수 있습니다')
    }
    
    console.log('✅ 테스트 환경 검증 완료\n')
    return true
    
  } catch (error) {
    console.error('❌ 테스트 환경 검증 실패:')
    console.error(error.message)
    return false
  }
}

/**
 * 메인 실행 함수
 */
async function main() {
  console.log('🧪 프론트엔드 학습 API 연동 통합 테스트 러너')
  console.log('=' .repeat(60))
  
  // 환경 검증
  if (!validateTestEnvironment()) {
    process.exit(1)
  }
  
  // 통합 테스트 실행
  const results = await runIntegrationTests()
  
  // 종료 코드 설정
  process.exit(results.success ? 0 : 1)
}

// 스크립트가 직접 실행될 때만 main 함수 호출
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('❌ 테스트 러너 실행 중 오류 발생:')
    console.error(error)
    process.exit(1)
  })
}

export { runIntegrationTests, validateTestEnvironment }