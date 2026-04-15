# 퀀트 코인 트레이딩 마스터 스터디 가이드

이 문서는 네가 요청한 자료를 **하나도 빠짐없이** 실전 적용 중심으로 정리한 통합 학습 문서다.  
목표는 다음 두 가지다.

1. 공부를 빠르게 끝내고
2. 네 현재 자동매매 코드(daemon/supervisor/override 구조)에 바로 반영하는 것

---

## 0) 이 문서 사용법

- 이 문서는 `지식 정리 + 실습 과제 + 코드 반영 체크리스트`를 한 번에 담는다.
- 각 섹션에서 `학습`, `실습`, `완료 기준` 3가지를 모두 체크한다.
- “읽기만” 하지 말고 반드시 `실습 산출물`을 남긴다.
- 실전 적용 전에는 반드시 `검증 게이트`를 통과한다.

---

## 1) 필수 원문 링크 (요청한 링크 전체)

### 1-1. 엔진/실행 이해 (코드와 직접 연결)
- Freqtrade 홈/기본: https://www.freqtrade.io/en/stable/
- Backtesting: https://www.freqtrade.io/en/stable/backtesting/
- Hyperopt: https://www.freqtrade.io/en/stable/hyperopt/
- Lookahead analysis: https://www.freqtrade.io/en/stable/lookahead-analysis/
- Recursive analysis: https://www.freqtrade.io/en/stable/recursive-analysis/
- CCXT Manual: https://github.com/ccxt/ccxt/wiki/Manual
- Bitget Futures API 개요: https://www.bitget.com/api-doc/contract/intro
- Bitget 주문 API (격리/교차, TP/SL 파라미터): https://www.bitget.com/api-doc/contract/trade/Place-Order

### 1-2. 데이터/통계 기초 (퀀트 검증 필수)
- pandas docs: https://pandas.pydata.org/docs/index.html
- NumPy docs: https://numpy.org/doc/stable/
- statsmodels docs: https://www.statsmodels.org/stable/
- scikit-learn docs: https://scikit-learn.org/stable/
- ISL (무료 교재): https://www.statlearning.com/

### 1-3. 과최적화 방지 핵심 논문
- PBO (Probability of Backtest Overfitting): https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- DSR (Deflated Sharpe Ratio): https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

---

## 2) 학습 전체 로드맵 (요약)

1. 실행 엔진 이해: 주문이 어떻게 나가고 실패하는지 완전 이해
2. 데이터 파이프라인 고정: 재현 가능한 전처리/피처 생성
3. 백테스트 신뢰성 확보: lookahead/recursive/walk-forward
4. 과최적화 차단: PBO/DSR
5. 운영 안정화: supervisor/monitor/kill-switch
6. 소액 canary 실거래: 검증된 전략만 단계 확대

---

## 3) 엔진/실행 계층: 문서별 학습 포인트와 실제 적용

## 3-1. Freqtrade (홈/기본)

### 학습
- 전략 클래스 구조
- 데이터 타임프레임 처리
- 주문 상태 전이
- 리스크 파라미터의 위치와 책임 분리

### 실습
- 네 전략 로직을 Freqtrade 스타일로 “개념 매핑표” 작성
- 예: `entry gate`, `exit gate`, `position sizing`, `risk guard`를 분리

### 완료 기준
- “어떤 파라미터가 어디서 적용되는지” 1페이지로 설명 가능

---

## 3-2. Backtesting

### 학습
- 체결 가정(시장가/지정가), 수수료, 슬리피지
- 포지션 진입/청산 순서와 중복 주문 처리
- 결과 지표(PnL, DD, winrate, expectancy)

### 실습
- 백테스트 엔진에서 `gross PnL`과 `net PnL` 분리 출력
- 수수료/슬리피지 민감도 테스트 3단계 생성
  - base
  - stress(+50%)
  - worst(+100%)

### 완료 기준
- 수수료 가정 변경 시 성과가 얼마나 무너지는지 표로 제시

---

## 3-3. Hyperopt

### 학습
- 탐색 공간 설계
- 목적함수 정의
- 탐색 횟수 증가가 과최적화로 연결되는 이유

### 실습
- 목적함수를 `수익 단일`에서 아래 형태로 변경

```text
objective = net_return
            - dd_penalty
            - turnover_penalty
            + dsr_bonus
```

### 완료 기준
- “고수익인데 불안정한 파라미터”를 자동으로 탈락시키는 룰 포함

---

## 3-4. Lookahead Analysis

### 학습
- 미래 데이터 참조(leakage) 패턴
- 흔한 실수: shift 방향 오류, rolling window 종료시점 오류

### 실습
- 전략별 lookahead 검사 스크립트를 CI/로컬 검증에 추가

### 완료 기준
- 위반 1건이라도 있으면 배포 차단

---

## 3-5. Recursive Analysis

### 학습
- 지표 초기값(warmup) 민감도
- 시뮬레이션마다 신호가 달라지는 비결정성 문제

### 실습
- warmup 길이를 여러 값으로 바꿔 신호 일관성 체크

### 완료 기준
- 일치율 임계치(예: 95%) 미달 전략 자동 제외

---

## 3-6. CCXT Manual

### 학습
- 공통 API와 거래소별 파라미터 차이
- rate limit, retry, nonce, precision 처리
- idempotency(`clientOrderId`) 중요성

### 실습
- 주문 어댑터 체크리스트 만들기
  - precision 정규화
  - min notional/lot size 검증
  - 재시도 정책(backoff)
  - 중복 주문 방지 키

### 완료 기준
- “실패해도 돈 잃지 않는 주문 함수” 설계 문서 보유

---

## 3-7. Bitget Futures API

### 학습
- 교차/격리 마진 모드 차이
- 주문 생성 시 TP/SL 전달 필드
- 포지션 필드 vs plan order 필드 차이

### 실습
- 주문 직후 다음 3단계 검증 자동화
  1. 포지션 조회
  2. plan order 조회
  3. SL/TP 존재 여부 로그

### 완료 기준
- “진입했는데 보호주문이 없다” 상황을 30초 내 감지 가능

---

## 4) 데이터/통계 계층: 문서별 학습 포인트와 실제 적용

## 4-1. pandas

### 학습
- 시계열 인덱스 관리
- 결측치 처리 정책
- 멀티 타임프레임 병합 방식

### 실습
- 피처 생성 파이프라인 함수화
- 입력/출력 schema 고정

### 완료 기준
- 같은 원본 데이터로 항상 같은 피처 결과

---

## 4-2. NumPy

### 학습
- 벡터화 계산
- 브로드캐스팅/shape 안정성
- 수치 안정성(eps, overflow)

### 실습
- 느린 루프 기반 피처를 벡터화로 전환

### 완료 기준
- 성능 개선 + 결과 동일성 테스트 통과

---

## 4-3. statsmodels

### 학습
- 자기상관, 레짐 변화, 잔차 진단
- 회귀계수/유의성 해석

### 실습
- 전략 수익률 시계열에 대해 ACF/PACF/잔차진단 수행

### 완료 기준
- 통계적으로 불안정한 전략을 명시적으로 제외

---

## 4-4. scikit-learn

### 학습
- TimeSeriesSplit
- 파이프라인 기반 누수 방지
- 정규화/스케일링의 시점 일관성

### 실습
- 랜덤 split 금지, 시계열 split만 허용
- 학습/검증 분리 후 피처 변환 시점 통제

### 완료 기준
- 학습 데이터 누수 0

---

## 4-5. ISL

### 학습
- 편향-분산 트레이드오프
- 모델 복잡도 관리
- 해석 가능한 모델 우선 원칙

### 실습
- 단순 모델(선형/트리)과 복잡 모델 성능 비교표 작성

### 완료 기준
- 복잡 모델이 OOS 개선 없으면 채택 금지

---

## 5) 과최적화 방지: PBO/DSR 실전 적용

## 5-1. PBO (Backtest Overfitting 확률)

### 핵심 아이디어
- 과거 구간/파라미터를 많이 탐색할수록 “우연히 잘 나온 전략”이 늘어난다.
- PBO는 그 위험을 수치화한다.

### 실전 절차
1. 여러 구간으로 데이터 분할
2. 각 구간에서 다수 파라미터 조합 성능 산출
3. in-sample 상위 전략이 out-of-sample에서도 상위인지 확인
4. 무너지는 비율로 PBO 추정

### 채택 기준 예시
- PBO 높음: 실거래 금지
- PBO 낮음 + DSR 양수: 후보 유지

---

## 5-2. DSR (Deflated Sharpe Ratio)

### 핵심 아이디어
- Sharpe Ratio는 탐색 횟수와 표본길이의 착시를 반영하지 못한다.
- DSR은 “진짜 유의한 샤프인가?”를 보정한다.

### 실전 절차
1. 후보 전략별 샤프 계산
2. 탐색한 전략 수, 표본 수, 왜도/첨도 반영
3. DSR 산출

### 채택 기준 예시
- DSR <= 0: 폐기
- DSR > 0 and PBO 낮음: 통과

---

## 6) 전략 연구 프레임워크 (반드시 이 순서)

1. 가설 작성  
2. 데이터 정의  
3. 피처 정의  
4. 백테스트  
5. lookahead 검사  
6. recursive 검사  
7. walk-forward OOS  
8. PBO/DSR  
9. paper trade  
10. 소액 canary  
11. 단계적 확장

---

## 7) 전략 카테고리 지도 (무엇을 공부해야 하는가)

## 7-1. Trend Following
- EMA/ADX/돌파 기반
- 장점: 큰 추세 먹기
- 단점: 횡보장에서 손실 반복
- 검증 포인트: 레짐 필터 유무

## 7-2. Mean Reversion
- 밴드 이탈 복귀, RSI 과매수/과매도
- 장점: 높은 승률 가능
- 단점: 강한 추세에서 연속 손실
- 검증 포인트: 추세 필터 결합

## 7-3. Breakout/Volatility Expansion
- 변동성 수축 후 확장 진입
- 장점: 짧고 강한 움직임 포착
- 단점: 가짜 돌파
- 검증 포인트: 거래량/체결강도 동반 여부

## 7-4. Funding/Basis 구조
- 선물 펀딩/현선 괴리 기반
- 장점: 구조적 엣지 가능
- 단점: 거래소별 제약/수수료 민감
- 검증 포인트: 비용/슬리피지 반영 후 순엣지

## 7-5. Event/Regime Filter
- 변동성 레짐, 매크로 이벤트 시간대 회피
- 장점: 손실 구간 회피
- 단점: 진입 기회 감소
- 검증 포인트: 필터 전후 expectancy 비교

---

## 8) 실행/운영 계층 (네 현재 구조에 직접 매핑)

아래는 네가 써온 구조(daemon/supervisor/monitor/override) 기준이다.

1. `strategy_override.approved.json`  
- 실행 파라미터 저장소  
- 원칙: 검증 통과 값만 반영

2. `daemon.py`  
- 진입/청산 의사결정  
- 원칙: 검증 게이트 통과 전략만 활성

3. `live_order_adapter.py`  
- 거래소 주문 어댑터  
- 원칙: precision/min notional/retry/idempotency 필수

4. `daemon_supervisor.py`  
- 데몬 다운 자동 복구  
- 원칙: 장애 복구와 전략 로직 분리

5. `monitor_daemon_health.py`  
- 상태/오류/보호주문 모니터  
- 원칙: position 필드 + plan order 둘 다 조회

---

## 9) 필수 리스크 관리 규칙 (공부 + 운영 공통)

1. 거래소 하드 SL 없는 포지션 금지
2. 수동 포지션과 자동전략 혼합 금지(검증 기간)
3. 동일 시점 다중 데몬 금지
4. 전략 변경 후 즉시 실거래 확대 금지
5. single-run 로그/리포트 저장 필수

---

## 10) “수익 극대화”를 위한 현실적 규칙

- 수익 극대화는 “진입 빈도 증가”가 아니라 “검증된 진입의 품질 증가”다.
- 기대값이 음수면 레버리지를 올릴수록 파산 속도만 빨라진다.
- 네 목표가 공격적이어도, 최소한 다음은 지켜야 한다.
  - 비용 반영 후 양(+) 기대값
  - 손실 꼬리 관리(DD 제한)
  - 전략 변경시 재검증

---

## 11) 실습 과제 세트 (바로 수행 가능)

## 과제 A: 실행 정합성
- 주문 직후 SL/TP 존재 여부 자동 검증 스크립트 작성
- 실패 케이스 알림/자동 재시도

## 과제 B: 검증 파이프라인
- lookahead + recursive + walk-forward 일괄 실행 스크립트 작성

## 과제 C: 통계 품질 게이트
- PBO/DSR 계산 모듈 추가
- 결과가 기준 미달이면 배포 차단

## 과제 D: 운영 안정화
- supervisor 단일 런처로 통일
- 중복 데몬 감지 및 기동 차단

---

## 12) 실전 체크리스트 (배포 전)

1. 데이터 누수 검사 통과
2. 지표 재귀 안정성 통과
3. OOS 성능 기준 통과
4. 비용 스트레스 테스트 통과
5. PBO/DSR 기준 통과
6. 주문 실패/재시도 로직 테스트 통과
7. 보호주문 미부착 케이스 테스트 통과
8. 모니터 경보 테스트 통과
9. 소액 canary 결과 확인
10. 단계적 증액 계획 수립

---

## 13) 지표/수식 빠른 참조

### 기대값
```text
Expectancy = WinRate * AvgWin - (1 - WinRate) * AvgLoss
```

### 손익비(R)
```text
R = AvgWin / AvgLoss
```

### 샤프(기본형)
```text
Sharpe = (E[R] - Rf) / Std[R]
```

### 최대낙폭(MDD)
```text
MDD = max(peak_to_trough_drawdown)
```

### 회전율
```text
Turnover = traded_notional / average_equity
```

---

## 14) 흔한 함정 (실제로 계좌를 깎는 패턴)

1. “백테스트 수익률”만 보고 배포
2. 수수료/슬리피지 누락
3. 레버리지만 올려서 수익률 착시 만들기
4. 수동 개입으로 전략 평가 데이터 오염
5. 여러 디렉터리/여러 데몬 동시 실행
6. 보호주문 확인 없이 포지션 유지
7. 작은 표본 성과를 일반화

---

## 15) 12주 커리큘럼 (방대하게 공부할 때)

## 1-2주: 엔진/주문
- Freqtrade 기본 + Backtesting
- CCXT 주문/정밀도/오류처리
- Bitget 주문 필드 완전 이해

## 3-4주: 데이터/통계
- pandas/NumPy 파이프라인 구축
- statsmodels 기초 진단
- sklearn 시계열 검증

## 5-6주: 검증 고도화
- lookahead/recursive 자동화
- walk-forward 템플릿 확립

## 7-8주: 과최적화 방지
- PBO 구현
- DSR 구현
- 목적함수 재설계

## 9-10주: 운영/안정성
- supervisor/monitor/alert 강화
- 실패 복구 runbook 완성

## 11-12주: 실전
- 소액 canary
- 성과 리뷰 + 포스트모템
- 단계적 증액 여부 판단

---

## 16) 리포트 템플릿 (복붙용)

```markdown
# Strategy Experiment Report

## 1. Hypothesis
- 

## 2. Data Scope
- Symbol:
- Timeframe:
- Period:

## 3. Entry/Exit Logic
- Entry:
- Exit:
- Risk:

## 4. Validation
- Lookahead:
- Recursive:
- Walk-forward:
- PBO:
- DSR:

## 5. Cost Model
- Fee:
- Slippage:
- Funding:

## 6. Results
- Net Return:
- Max DD:
- Sharpe:
- DSR:
- Expectancy:

## 7. Decision
- Promote / Hold / Reject
- Reason:
```

---

## 17) 운영 포스트모템 템플릿 (복붙용)

```markdown
# Live Incident Postmortem

## Summary
- Incident:
- Start/End:
- Impact:

## Timeline
- 

## Root Cause
- 

## Detection Gaps
- 

## Corrective Actions
- Short-term:
- Long-term:

## Prevention Checklist
- [ ] 
```

---

## 18) 추천 추가 읽기 (심화)

- Marcos Lopez de Prado, *Advances in Financial Machine Learning*
- Ernest P. Chan, *Algorithmic Trading*
- Robert Carver, *Systematic Trading*
- Grinold & Kahn, *Active Portfolio Management*
- Aldridge, *High-Frequency Trading* (마이크로구조 이해용)

---

## 19) 최종 운영 원칙

1. 좋은 전략은 “화려한 수익률”이 아니라 “재현 가능한 검증”에서 나온다.
2. 한 번의 대박보다 장기 기대값이 우선이다.
3. 자동매매는 전략 개발보다 운영 안정성이 더 중요할 때가 많다.
4. 문서화되지 않은 전략은 없는 전략과 같다.

---

## 20) 네가 바로 시작할 최소 액션 5개

1. 이 문서 기준으로 `검증 파이프라인` 체크리스트 파일 생성
2. 현재 전략에 lookahead/recursive 자동 검사 연결
3. 백테스트 출력에 비용 스트레스 시나리오 추가
4. PBO/DSR 계산 노트북(또는 스크립트) 작성
5. 다음 배포부터는 “검증 통과 전략만 override 반영” 규칙 고정

---

## 21) 링크별 상세 개념 해설 (요청사항 보강)

아래는 네가 준 링크 각각에 대해 “무엇을 의미하는지, 왜 중요한지, 네 코드에서 어디에 연결되는지”를 상세화한 섹션이다.

## 21-1. Freqtrade 홈/기본 (`/stable/`)

### 핵심 개념
- Strategy Lifecycle: 데이터 수집 -> 지표 계산 -> 엔트리/익시트 판단 -> 주문 -> 포지션 관리
- Bot Mode: backtest / dry-run / live를 분리해서 동일 전략의 단계별 검증
- Pairlist/Whitelist: 어떤 종목을 거래 우주(universe)로 인정할지 정의
- Protections: 연속 손실 구간, 쿨다운, drawdown 방어 등 시스템 차단장치
- ROI/Stoploss 구조: “언제 익절/손절을 실행할지”를 전략과 리스크 레이어로 분리

### 실무에서 중요한 이유
- 네 시스템도 `daemon(판단)`과 `adapter(실행)`가 분리되어 있어 구조가 비슷하다.
- 실패 사례 대부분이 “전략 문제”가 아니라 “실행/보호주문/운영 모드 문제”에서 발생한다.

### 네 코드에 직접 적용
- `strategy_override.approved.json` -> Freqtrade의 config 역할
- `daemon.py` -> strategy lifecycle의 판단부
- `live_order_adapter.py` -> 실제 주문/체결/보호주문 책임
- `monitor/supervisor` -> protections + 운영 안정화 레이어

---

## 21-2. Backtesting (`/stable/backtesting/`)

### 핵심 개념
- Backtest Assumption: 체결가/수수료/슬리피지/펀딩비 가정이 결과를 크게 바꾼다.
- Trade Accounting: 진입/청산 순서, 포지션 중첩 허용 여부, 부분청산 반영이 정확해야 한다.
- Result Interpretation: 수익률 하나만 보지 않고 DD, expectancy, trade count, exposure를 같이 본다.

### 네가 특히 놓치면 안 되는 포인트
- 소액/고레버리지에서는 fee와 slippage가 전략 엣지를 먹어버릴 수 있다.
- 거래 횟수가 너무 적은 전략은 “좋아 보이는 착시”가 자주 나온다.
- “한 번 크게 먹는 전략”은 tail-risk(연속 손실) 검증이 필수다.

### 적용 체크리스트
- 백테스트 결과에 `gross`, `fee`, `slippage`, `funding`, `net` 분리 출력
- 기본 가정 + 스트레스 가정(비용 1.5배/2배) 동시 출력
- 최소 샘플 트레이드 수 기준(예: OOS 50건 미만은 보류)

---

## 21-3. Hyperopt (`/stable/hyperopt/`)

### 핵심 개념
- Parameter Space: buy/sell/protection 파라미터 탐색 범위
- Objective Function: 무엇을 최적화할지(수익만? DD 반영?)
- Over-search Risk: 탐색을 많이 돌릴수록 우연한 승자 발생 확률 증가

### 실무 해석
- Hyperopt는 전략 “발견기”가 아니라 “후보 정렬기”에 가깝다.
- 목적함수를 잘못 잡으면 실거래에서 가장 먼저 무너진다.

### 네 코드 적용
- 목적함수 권장:
```text
objective = net_return - max_drawdown_penalty - turnover_penalty + dsr_bonus
```
- 단일 기간 최적화 금지, multi-period와 walk-forward를 세트로 사용

---

## 21-4. Lookahead Analysis (`/stable/lookahead-analysis/`)

### 핵심 개념
- Lookahead Bias: 의도치 않게 미래 캔들/미래 지표를 현재 의사결정에 사용한 오류
- Signal Integrity: 엔트리/익시트가 오직 시점 t 데이터만으로 계산되는지 검증

### 흔한 누수 패턴
- `shift(-1)` 오남용
- rolling window 종결 시점 처리 오류
- label 생성 후 feature 분리 순서 실수

### 네 코드 적용
- 신규 전략 추가시 lookahead 테스트 통과를 머지 조건으로 강제
- 실패하면 전략 성능이 높아도 즉시 폐기

---

## 21-5. Recursive Analysis (`/stable/recursive-analysis/`)

### 핵심 개념
- Warmup Sensitivity: 초기 캔들 수에 따라 지표/시그널이 달라지는 현상
- Recursive Stability: 실행 경로가 달라도 동일 신호가 재현되는지 확인

### 실무 의미
- 라이브에서는 데이터가 “한 캔들씩” 들어오므로, 백테스트와 계산 경로가 달라질 수 있다.
- 이 차이가 크면 실거래 성능이 급락한다.

### 네 코드 적용
- warmup 길이를 여러 값으로 바꿔 시그널 일치율 측정
- 일치율 기준 미달 전략은 운영에서 제외

---

## 21-6. CCXT Manual

### 핵심 개념
- Unified API: 거래소별 API 차이를 공통 인터페이스로 흡수
- Market Metadata: precision, min amount, min cost, lot size 등 주문 가능 조건
- Rate Limit/Retry: API 한도 초과/일시 장애 대응
- Order Semantics: market/limit/stop/reduceOnly 등 주문 의미 통일

### 실무 포인트
- 실제 손실은 신호보다 “주문 실패 처리”에서 더 크게 발생한다.
- 같은 전략이라도 거래소별 파라미터 차이 때문에 결과가 달라진다.

### 네 코드 적용
- 주문 전 `precision + min notional + leverage + margin mode` 선검증
- 실패시 idempotent 재시도(client order key) 적용
- transient error와 fatal error를 분리하여 처리

---

## 21-7. Bitget Futures API Intro

### 핵심 개념
- Account/Position Model: 선물 계좌, 종목 단위 포지션, 마진 모드
- Margin Mode: isolated(격리) / crossed(교차)
- Leverage Scope: 심볼별 레버리지 세팅과 적용 타이밍
- Plan Orders: TP/SL이 포지션 필드가 아니라 별도 plan 주문으로 관리될 수 있음

### 실무 포인트
- `position.stopLoss`만 보고 보호주문 존재를 판단하면 오판할 수 있다.
- 일부 거래소 구현은 TP/SL이 `plan order` 엔드포인트에서만 보인다.

### 네 코드 적용
- 포지션 조회 + plan order 조회를 동시 모니터링
- 모니터 경보는 “둘 다 없음”일 때만 발생하도록 조건 강화

---

## 21-8. Bitget Place-Order

### 핵심 개념
- 필수 주문 파라미터: symbol, side, size, orderType 등
- 파생 파라미터: marginMode, leverage, reduceOnly
- 보호주문 파라미터: presetStopLossPrice, presetTakeProfitPrice(또는 동등 필드)

### 실무 포인트
- 주문 accepted만으로 안전하지 않다.
- 반드시 “보호주문이 실제로 생겼는지” 후검증해야 한다.

### 네 코드 적용
- 주문 후 즉시 검증 플로우
  1. 포지션 확인
  2. pending plan 주문 확인
  3. 없으면 보정 주문
  4. 실패하면 경보 + 신규 진입 일시 차단

---

## 21-9. pandas docs

### 핵심 개념
- Index Alignment: 시계열 결합시 인덱스 정렬 규칙
- Resample/Rolling: 타임프레임 변환과 윈도우 계산
- Missing Data: 결측 처리 방법이 전략 결과에 영향

### 실무 포인트
- 멀티타임프레임 전략은 인덱스 미스매치로 누수가 발생하기 쉽다.
- fillna를 습관적으로 쓰면 미래 정보가 암묵적으로 섞일 수 있다.

### 네 코드 적용
- 데이터셋 생성 단계에서 schema/인덱스 검증 함수 고정
- 피처 컬럼별 결측 처리 정책 문서화

---

## 21-10. NumPy docs

### 핵심 개념
- ndarray/broadcasting: 빠른 벡터 연산 기반
- Numerical Stability: overflow/underflow, floating error 관리
- Memory Layout: 연산 성능과 복사 비용

### 실무 포인트
- 루프 기반 구현은 느리고 버그가 많다.
- 벡터화는 속도뿐 아니라 코드 일관성에도 이점이 있다.

### 네 코드 적용
- 핵심 지표 계산 루프를 벡터화
- 계산 결과 동일성 테스트를 같이 작성

---

## 21-11. statsmodels docs

### 핵심 개념
- Time-series diagnostics: 자기상관, 잔차 분석
- Regime/Stationarity 관점: 시장 상태 변화 인지
- Statistical significance: 우연성과 구조적 엣지 구분

### 실무 포인트
- 전략 수익률이 특정 구간에만 의존하는지 통계적으로 확인 가능하다.
- “작동해 보임”과 “유의미함”을 분리해야 한다.

### 네 코드 적용
- 월간 수익률 시계열에 진단 리포트 추가
- 자기상관 과대/불안정 전략은 리스크 가중치 하향

---

## 21-12. scikit-learn docs

### 핵심 개념
- Pipeline: 전처리+모델+검증 일관화
- TimeSeriesSplit: 시계열 순서를 보존한 검증
- Leakage Prevention: fit/transform 시점 분리

### 실무 포인트
- 랜덤 KFold는 시계열 트레이딩에서 대부분 부적절하다.
- 파이프라인 없이 개별 전처리하면 누수 가능성이 커진다.

### 네 코드 적용
- 모델 실험 기본 템플릿을 TimeSeriesSplit 기반으로 고정
- 학습/검증 분리 이전에 스케일링 금지

---

## 21-13. ISL (An Introduction to Statistical Learning)

### 핵심 개념
- Bias-Variance Tradeoff
- Model Assessment and Selection
- Regularization, Tree/Ensemble, Classification/Regression 해석

### 실무 포인트
- 복잡한 모델이 항상 이기는 것이 아니다.
- 트레이딩에서는 해석 가능성과 안정성이 더 중요할 때가 많다.

### 네 코드 적용
- 단순 모델을 baseline으로 고정하고 복잡 모델은 “추가 이익”이 있을 때만 채택
- 모델 선택 기준에 OOS 안정성과 거래비용 민감도 포함

---

## 21-14. PBO 논문 (Backtest Overfitting)

### 핵심 개념
- 과거 데이터에서 좋아 보이는 전략이 미래에서는 무너질 확률을 정량화
- 탐색 횟수 증가에 따른 선택 편향 문제를 다룸

### 실무 포인트
- 여러 전략/파라미터를 동시에 시험했다면, 최고 성능 전략은 과대평가 가능성이 높다.

### 네 코드 적용
- 후보 전략 선정 후 PBO 계산을 통과한 전략만 live 후보군으로 승격

---

## 21-15. DSR 논문 (Deflated Sharpe Ratio)

### 핵심 개념
- 단순 Sharpe Ratio의 과대평가를 보정
- 표본 수/다중 테스트/분포 특성(왜도, 첨도) 반영

### 실무 포인트
- “샤프가 높다”는 문장만으로는 전략 채택 근거가 약하다.
- DSR은 전략 우위의 신뢰도를 더 현실적으로 보여준다.

### 네 코드 적용
- 리포트 기본 성과표에 Sharpe와 DSR를 둘 다 표시
- DSR 임계치 미달 전략 자동 탈락

---

## 22) 네 시스템 기준 실전 매핑 테이블 (핵심 요약)

| 문서 | 네 코드/운영에서 대응되는 위치 | 반드시 남길 산출물 |
|---|---|---|
| Freqtrade 기본 | daemon/override 구조 | 전략 책임 분리도 |
| Backtesting | 백테스트 스크립트 | 비용반영 성과표 |
| Hyperopt | 파라미터 탐색 | 목적함수 명세서 |
| Lookahead | 검증 파이프라인 | 누수 검사 리포트 |
| Recursive | 지표 안정성 검사 | warmup 민감도 리포트 |
| CCXT Manual | 주문 어댑터 | 주문 실패 처리표 |
| Bitget Intro | 계정/포지션 모델 | 포지션-플랜 정합 체크 |
| Bitget Place-Order | 주문 생성 | 보호주문 확인 로그 |
| pandas/NumPy | 피처 파이프라인 | 재현성 테스트 |
| statsmodels/sklearn | 통계/모델 검증 | OOS/진단 리포트 |
| PBO/DSR | 전략 채택 게이트 | 채택/탈락 근거표 |

---

## 23) 자주 묻는 오해 정리 (실전형)

### Q1. “진입이 많으면 수익 극대화 아닌가?”
- 아니다. 기대값이 음수면 진입이 많을수록 손실이 빨라진다.

### Q2. “레버리지 올리면 같은 전략도 더 빨리 불어나지 않나?”
- 기대값 양수일 때만 의미가 있다. 음수 전략에 레버리지는 파산 가속기다.

### Q3. “백테스트 수익률이 높으면 라이브도 되지 않나?”
- lookahead/recursive/PBO/DSR 미통과면 높은 확률로 착시다.

### Q4. “SL/TP 붙였는데 왜 손실이 커지지?”
- 거래소 저장 모델(position vs plan), 실행 지연, 수동 개입, 사이징 과다가 겹치면 발생한다.

---

## 24) 다음 단계 (문서 이후 실제 액션)

1. 이 문서 기반으로 `VALIDATION_PIPELINE.md`를 별도 생성
2. 현재 전략 후보에 lookahead/recursive 자동 실행 붙이기
3. 월 1회 PBO/DSR 리포트 생성 자동화
4. 실거래는 canary 계정으로만 먼저 검증
5. 본계정 확대는 “검증 지표 통과 + 운영 사고 0건” 조건으로만 수행

---

## 25) 개념 확장 사전 (의미/언제 사용/연관 개념/실수 포인트)

아래는 네가 실제로 전략 만들고 운영할 때 자주 부딪히는 핵심 개념들을 확장 정리한 섹션이다.

## 25-1. 시장/체결(Market Microstructure)

### Spread (호가 스프레드)
- 의미: 매수호가와 매도호가의 차이, 즉 즉시 체결 비용의 핵심.
- 언제 사용: 진입 후보를 고를 때 비용 필터로 사용.
- 연관 개념: slippage, maker/taker fee, order book depth.
- 실수 포인트: “신호가 좋아서” 진입했는데 spread 때문에 기대값이 바로 음수로 변함.

### Slippage (슬리피지)
- 의미: 기대한 가격과 실제 체결 가격의 차이.
- 언제 사용: 백테스트의 비용 모델, 라이브 성과 해석.
- 연관 개념: volatility, liquidity, order type.
- 실수 포인트: 백테스트에서 0으로 두면 거의 모든 전략이 과대평가됨.

### Order Book Depth (호가 잔량 깊이)
- 의미: 각 가격 구간에 실제로 체결 가능한 물량.
- 언제 사용: 주문 사이즈 결정, 급변동 구간 진입 회피.
- 연관 개념: market impact, partial fill.
- 실수 포인트: 소액은 괜찮아 보여도 레버리지로 notional이 커지면 체결 품질 급락.

### Maker/Taker
- 의미: 유동성을 제공하면 maker, 즉시 가져가면 taker 수수료 적용.
- 언제 사용: 비용 최소화 전략 설계, 주문 타입 선택.
- 연관 개념: spread capture, queue risk.
- 실수 포인트: maker 수수료 절약만 보다가 미체결/기회손실이 커짐.

### Market Impact
- 의미: 내 주문 자체가 가격을 움직여 불리한 체결을 유발하는 효과.
- 언제 사용: 대형 주문 또는 저유동성 코인 거래 시.
- 연관 개념: slippage, depth, sweep.
- 실수 포인트: 테스트는 체결되는데 실거래는 점점 나빠지는 이유를 못 찾음.

### Adverse Selection
- 의미: 내가 체결될 때는 대체로 불리한 정보가 이미 시장에 반영된 상태인 현상.
- 언제 사용: 지정가 전략, 고빈도 진입 전략 분석.
- 연관 개념: latency, maker execution.
- 실수 포인트: 체결률을 올릴수록 손익이 악화되는 역설 발생.

### Liquidation Cascade
- 의미: 강제청산이 연쇄적으로 발생하며 가격이 급변하는 현상.
- 언제 사용: 고레버리지 구간, 알트 급등락 구간 리스크 관리.
- 연관 개념: funding skew, open interest.
- 실수 포인트: 손절을 늦추면 반등할 것이라는 가정이 연쇄청산 국면에서 무너짐.

---

## 25-2. 파생/레버리지/거래소 구조

### Isolated Margin
- 의미: 포지션별로 증거금을 분리해 해당 포지션만 청산 리스크를 가짐.
- 언제 사용: 고위험 전략, 계좌 전체 보호가 필요할 때.
- 연관 개념: cross margin, liquidation price.
- 실수 포인트: isolate로 바꿨다고 손실이 줄어드는 게 아니라 “손실 범위”가 제한되는 것.

### Cross Margin
- 의미: 계좌 전체 증거금을 공유해 포지션 유지력을 늘리지만 계좌 전체 위험 증가.
- 언제 사용: 저레버리지/다중헤지 구조.
- 연관 개념: margin ratio, account-level risk.
- 실수 포인트: 단기 버팀목으로 보이지만 한 번 꼬이면 계좌 전체 손실 확대.

### Leverage
- 의미: 적은 증거금으로 큰 포지션을 운용하는 배수.
- 언제 사용: 자본 효율을 높이고 싶을 때.
- 연관 개념: liquidation, volatility drag.
- 실수 포인트: 엣지 검증 전 레버리지를 올리면 파산 속도만 빨라짐.

### Funding Rate
- 의미: 선물-현물 가격괴리를 조정하기 위해 롱/숏 간 주기적 비용 이전.
- 언제 사용: 포지션 장기 보유 판단, 펀딩 기반 전략.
- 연관 개념: basis, carry.
- 실수 포인트: 높은 미실현수익에 취해 펀딩 누적 비용을 무시.

### Basis
- 의미: 선물 가격과 현물 가격 차이.
- 언제 사용: 시장 과열/과매도 판별, 구조적 전략.
- 연관 개념: funding, carry trade.
- 실수 포인트: basis 신호만으로 방향 베팅하면 체결/비용에 밀림.

---

## 25-3. 신호/전략 설계

### Signal
- 의미: 진입 또는 청산을 유발하는 규칙 결과.
- 언제 사용: 전략의 의사결정 핵심.
- 연관 개념: feature, threshold, regime filter.
- 실수 포인트: 신호 정의가 모호하면 검증 재현성이 깨짐.

### Regime Filter
- 의미: 시장 상태(추세/횡보/고변동/저변동)에 따라 신호를 허용/차단.
- 언제 사용: 전략이 특정 환경에서만 유효할 때.
- 연관 개념: volatility regime, trend filter.
- 실수 포인트: 필터가 너무 빡세면 진입이 사라지고, 너무 느슨하면 손실 구간 과진입.

### Trend Following
- 의미: 방향이 나온 구간을 따라가며 큰 움직임을 노리는 전략.
- 언제 사용: 명확한 추세장.
- 연관 개념: breakout, moving average.
- 실수 포인트: 횡보장에서 연속 손절.

### Mean Reversion
- 의미: 과도한 이탈이 평균으로 복귀한다는 가정 기반 전략.
- 언제 사용: 범위장/과매수 과매도 구간.
- 연관 개념: z-score, bands.
- 실수 포인트: 추세장 역추세 진입으로 대손실.

### Breakout
- 의미: 가격이 특정 범위를 돌파할 때 추세 확장을 추종.
- 언제 사용: 변동성 수축 후 확장 구간.
- 연관 개념: volume confirmation.
- 실수 포인트: 가짜 돌파 필터 부재.

### Expected Value (기대값)
- 의미: 장기적으로 거래 1회당 기대되는 평균 손익.
- 언제 사용: 전략 채택 여부의 최우선 기준.
- 연관 개념: winrate, payoff ratio.
- 실수 포인트: 승률만 보고 기대값을 무시.

### Payoff Ratio
- 의미: 평균 이익/평균 손실 비율.
- 언제 사용: 전략 프로파일 파악.
- 연관 개념: expectancy, stop/take design.
- 실수 포인트: 손익비가 높아도 승률이 너무 낮으면 기대값 음수 가능.

---

## 25-4. 리스크 관리

### Position Sizing
- 의미: 한 거래에 얼마를 배팅할지 결정하는 규칙.
- 언제 사용: 전략 동일해도 성과를 크게 좌우하는 핵심 레버.
- 연관 개념: Kelly, risk of ruin, max drawdown.
- 실수 포인트: 신호 검증보다 사이징으로 성과를 “가짜로” 좋게 만듦.

### Stop Loss (하드/소프트)
- 의미: 손실 제한을 위한 청산 규칙.
- 언제 사용: 모든 레버리지 전략.
- 연관 개념: hard exchange stop, software stop.
- 실수 포인트: 코드상 stop은 있는데 거래소 plan order에 실제 등록되지 않는 경우.

### Take Profit (고정/트레일링/부분익절)
- 의미: 이익 실현 규칙.
- 언제 사용: 수익 보호, 감정 개입 차단.
- 연관 개념: trailing stop, scale-out.
- 실수 포인트: TP를 너무 멀리 두면 익절 없이 되돌림에 수익 반납.

### Trailing Stop
- 의미: 가격이 유리하게 갈 때 손절선을 따라 올려 이익을 잠그는 방식.
- 언제 사용: 추세 지속 기대 구간.
- 연관 개념: arm threshold, retrace threshold.
- 실수 포인트: 너무 촘촘하면 노이즈에 반복 청산.

### Max Drawdown (MDD)
- 의미: 고점 대비 최대 손실 폭.
- 언제 사용: 전략 생존성 평가.
- 연관 개념: ruin probability, recovery factor.
- 실수 포인트: 수익률이 높아도 DD가 과도하면 장기 운영 불가.

### Risk of Ruin
- 의미: 전략/사이징 조합에서 계좌가 사실상 회복 불능에 도달할 확률.
- 언제 사용: 고레버리지 전략의 필수 지표.
- 연관 개념: edge, variance, position size.
- 실수 포인트: 단기 수익 경험으로 파산확률을 과소평가.

---

## 25-5. 검증 방법론

### In-Sample / Out-of-Sample
- 의미: 학습/튜닝 구간과 검증 구간을 분리해 일반화 성능 확인.
- 언제 사용: 모든 전략 연구 단계.
- 연관 개념: overfitting, walk-forward.
- 실수 포인트: OOS가 너무 짧으면 의미 없는 합격.

### Walk-Forward Validation
- 의미: 시간 순서를 유지해 반복적으로 학습-검증을 롤링 수행.
- 언제 사용: 시계열 전략의 표준 검증.
- 연관 개념: rolling window, expanding window.
- 실수 포인트: 한 구간 성과만 크게 보고 일반화.

### Lookahead Bias
- 의미: 미래 정보를 현재 의사결정에 누출한 오류.
- 언제 사용: 전략 신뢰성 점검.
- 연관 개념: leakage, label contamination.
- 실수 포인트: 지표 구현 사소한 버그가 성과를 비현실적으로 증폭.

### Data Leakage
- 의미: 학습/검증 분리가 깨져 검증이 오염되는 현상.
- 언제 사용: 피처 전처리/스케일링/모델 검증 단계.
- 연관 개념: pipeline, fit/transform separation.
- 실수 포인트: 전체 데이터로 normalize 후 split.

### Multiple Testing Problem
- 의미: 많이 시도할수록 우연한 승자 전략이 나오는 문제.
- 언제 사용: hyperopt/다전략 탐색 단계.
- 연관 개념: PBO, DSR.
- 실수 포인트: “최고 성능 1개”만 보고 채택.

### PBO
- 의미: 백테스트 과최적화 확률.
- 언제 사용: 후보 전략 최종 심사.
- 연관 개념: CSCV, rank stability.
- 실수 포인트: PBO 계산 없이 라이브 전환.

### DSR
- 의미: 다중 테스트 편향을 보정한 샤프 유의성 지표.
- 언제 사용: 전략 품질 최종 점검.
- 연관 개념: Sharpe, skew/kurtosis.
- 실수 포인트: Sharpe만 보고 전략 우수성 단정.

---

## 25-6. 성과 지표 해석

### CAGR
- 의미: 연복리 성장률.
- 언제 사용: 장기 성장률 비교.
- 연관 개념: volatility drag.
- 실수 포인트: 짧은 기간 CAGR 과대해석.

### Sharpe Ratio
- 의미: 변동성 대비 초과수익.
- 언제 사용: 전략 효율 비교.
- 연관 개념: DSR, Sortino.
- 실수 포인트: 비정규 분포/꼬리위험 구간에서 과신.

### Sortino Ratio
- 의미: 하방 변동성만 반영한 효율 지표.
- 언제 사용: 하락 위험 민감 전략 평가.
- 연관 개념: downside deviation.
- 실수 포인트: 데이터 포인트가 적으면 불안정.

### Calmar Ratio
- 의미: 수익률 대비 최대낙폭 비율.
- 언제 사용: DD 중심 평가.
- 연관 개념: MDD.
- 실수 포인트: DD가 한 번 크게 튀면 지표 왜곡.

### Turnover
- 의미: 자산 대비 거래량 회전율.
- 언제 사용: 비용 민감도 확인.
- 연관 개념: fee drag, slippage drag.
- 실수 포인트: 고회전 전략 비용을 과소추정.

---

## 25-7. 운영/신뢰성 엔지니어링

### Supervisor
- 의미: 데몬 비정상 종료 시 자동 재기동하는 프로세스 관리자.
- 언제 사용: 24/7 자동매매 필수.
- 연관 개념: heartbeat, crash loop.
- 실수 포인트: 원인 미해결 상태에서 무한 재기동만 반복.

### Heartbeat
- 의미: 프로세스가 정상 루프를 수행 중임을 나타내는 신호.
- 언제 사용: stall 탐지, 알림 시스템.
- 연관 개념: watchdog, health check.
- 실수 포인트: 살아있음(alive)과 정상작동(healthy)을 혼동.

### Idempotency
- 의미: 같은 요청을 여러 번 보내도 결과가 한 번 실행된 것처럼 유지되는 성질.
- 언제 사용: 네트워크 재시도 주문 처리.
- 연관 개념: client order id.
- 실수 포인트: 중복 주문 발생으로 과노출.

### Circuit Breaker / Kill Switch
- 의미: 비정상 상태에서 신규 진입을 중단하는 안전 장치.
- 언제 사용: API 장애, 데이터 오염, 연속 오류 발생 시.
- 연관 개념: error budget.
- 실수 포인트: kill switch 조건이 없어 사고가 커짐.

### Observability
- 의미: 로그/메트릭/트레이스로 시스템 상태를 진단할 수 있는 능력.
- 언제 사용: 라이브 운영 전체.
- 연관 개념: monitoring, alerting, postmortem.
- 실수 포인트: 포지션/plan order/에러를 분리 관측하지 않아 원인 파악 실패.

---

## 25-8. 데이터 품질/피처 엔지니어링

### OHLCV Integrity
- 의미: 캔들 데이터의 시간 순서/결측/중복/역전 여부의 정확성.
- 언제 사용: 연구 시작 전 항상.
- 연관 개념: timezone normalization.
- 실수 포인트: 잘못된 캔들 1개가 지표 전체를 왜곡.

### Feature Drift
- 의미: 피처 분포가 시간에 따라 변해 모델 성능이 저하되는 현상.
- 언제 사용: 장기 운영 전략.
- 연관 개념: concept drift, retraining cadence.
- 실수 포인트: 과거 유효 피처를 현재도 그대로 신뢰.

### Label Definition
- 의미: 모델 학습에서 정답을 어떻게 정의하는지.
- 언제 사용: ML 기반 전략.
- 연관 개념: horizon, stop/take labeling.
- 실수 포인트: 라벨 정의와 실제 주문 실행 규칙이 불일치.

---

## 26) 상황별 “어떤 개념을 꺼내야 하는가” 매뉴얼

### 상황 A: 진입이 너무 안 나온다
- 먼저 볼 개념: regime filter, threshold calibration, universe liquidity, signal sparsity.
- 왜: 신호 품질 필터가 과도하거나 우주 선정이 좁을 수 있다.
- 체크 항목: score 분포, gate별 탈락률, 심볼별 eligible 시간 비율.

### 상황 B: 진입은 많은데 계속 까먹는다
- 먼저 볼 개념: expected value, fee/slippage drag, adverse selection, turnover.
- 왜: 빈도는 높지만 비용이 엣지를 먹는 구조일 수 있다.
- 체크 항목: gross vs net 괴리, 시간대별 체결 품질.

### 상황 C: 백테스트는 좋고 라이브는 나쁘다
- 먼저 볼 개념: lookahead bias, recursive instability, execution mismatch.
- 왜: 검증 누수 또는 체결 가정 불일치 가능성 큼.
- 체크 항목: lookahead/recursive 리포트, live fill 품질 비교.

### 상황 D: 수익이 나도 계좌 변동이 너무 크다
- 먼저 볼 개념: position sizing, MDD, risk of ruin, leverage path dependency.
- 왜: 전략보다 배팅 크기가 문제일 수 있다.
- 체크 항목: 손실 꼬리 분포, 연속손실 길이.

### 상황 E: SL/TP가 가끔 사라진다
- 먼저 볼 개념: exchange plan order model, adapter idempotency, monitor coverage.
- 왜: 포지션 필드와 플랜필드 불일치 또는 갱신 로직 충돌 가능성.
- 체크 항목: 주문 직후 plan 조회, 수정 이력 로그.

---

## 27) 개념 간 관계 지도 (텍스트 그래프)

- 신호 품질 = feature quality + regime alignment + threshold design
- 실전 성과 = 신호 품질 + 실행 품질 - (fee + slippage + funding)
- 생존성 = 기대값 + 사이징 규율 + tail risk 통제
- 검증 신뢰도 = walk-forward + lookahead/recursive + PBO/DSR
- 운영 신뢰도 = supervisor + monitoring + idempotent execution + kill switch

---

## 28) 이 문서로 공부할 때 권장 진행 순서

1. 21번 링크별 해설 읽기
2. 25번 개념 사전에서 모르는 용어 체크
3. 26번 상황별 매뉴얼로 네 현재 문제에 매핑
4. 12번 체크리스트로 검증 루틴 실행
5. 16/17 템플릿으로 결과 기록

---

## 29) 마지막 확인: “공부가 끝났는지” 셀프 테스트

아래 질문에 답할 수 있으면 실전 투입 준비가 상당히 된 상태다.

1. 네 전략의 기대값은 비용 반영 후에도 양수인가?
2. lookahead/recursive 검사를 자동으로 통과시키는가?
3. OOS 성과가 IS 성과를 어느 정도 유지하는가?
4. PBO/DSR로 과최적화 가능성을 수치로 말할 수 있는가?
5. 주문 실패/재시도/중복 주문 방지 로직을 설명할 수 있는가?
6. SL/TP가 거래소에 실제 등록됐는지 어떻게 검증하는가?
7. 데몬이 멈췄을 때 몇 분 안에 복구되는가?
8. 수동 개입이 결과를 오염시키는 이유를 설명할 수 있는가?
9. 현재 사이징 기준에서 파산확률을 대략 추정할 수 있는가?
10. 전략을 폐기해야 할 조건을 사전에 정의했는가?

---

## 30) 정밀도 보강: 핵심 개념을 “확실히” 이해하기 위한 수식/판정 기준

아래는 기존 설명을 더 단단하게 만드는 최소 정량 기준이다.

### 30-1. Sharpe/Sortino/Calmar 해석 기준 (실무형)
- Sharpe:
```text
Sharpe = (mean(Rp - Rf)) / std(Rp - Rf)
Annualized Sharpe ~= Sharpe * sqrt(periods_per_year)
```
- Sortino:
```text
Sortino = (mean(Rp - Rf)) / downside_deviation
```
- Calmar:
```text
Calmar = CAGR / |Max Drawdown|
```

실무 판정 가이드(절대기준 아님):
- Sharpe < 0.5: 약함
- 0.5~1.0: 보통
- 1.0~1.5: 양호
- 1.5+: 우수 (단, 표본/비용/누수 검증 전제)

### 30-2. 기대값/손익비/승률 관계
- 기대값:
```text
E = WinRate * AvgWin - (1 - WinRate) * AvgLoss
```
- 손익비(R):
```text
R = AvgWin / AvgLoss
```
- 기대값 양수 조건:
```text
WinRate > 1 / (1 + R)
```
예시:
- R=2.0이면 승률 33.4%만 넘어도 기대값 양수 가능
- R=1.0이면 승률 50% 초과 필요

### 30-3. Risk of Ruin 직관식
- 엄밀 계산은 분포 가정이 필요하지만, 실무에선 아래 신호를 먼저 본다.
  - 기대값이 음수
  - 포지션 사이징 과대
  - 연속 손실에서 회복 필요 수익률이 급증
- 회복 필요 수익률:
```text
손실 10% -> 회복 +11.1%
손실 30% -> 회복 +42.9%
손실 50% -> 회복 +100%
```

### 30-4. PBO/DSR 실무 임계 운영
- PBO:
  - 낮을수록 좋음
  - 높게 나오면 최적화 탐색 횟수/자유도 축소 필요
- DSR:
  - DSR <= 0: 실거래 채택 금지
  - DSR > 0: 후보 유지 가능
  - DSR만으로 채택 금지, 반드시 OOS와 비용 스트레스 동반

---

## 31) 정밀도 보강: Lookahead/Recursive를 실제로 잡는 체크 패턴

### 31-1. Lookahead 의심 패턴
- `shift(-1)` 또는 미래 인덱스 참조
- 타깃(라벨) 계산 후 피처와 섞이는 전처리
- 전체 데이터 기준 normalize 후 분할

### 31-2. Recursive 불안정 패턴
- warmup 길이에 따라 신호가 크게 바뀜
- 지표 초기값이 전략 진입 방향에 직접 영향
- 타임프레임 변환시 경계 캔들 처리 불일치

### 31-3. 통과 기준 예시
- lookahead 위반: 0건
- recursive 일치율: 95%+ (전략 특성에 따라 조정)
- 실패 시: 파라미터 튜닝 금지, 구현 수정 우선

---

## 32) 정밀도 보강: Hyperopt/PBO/DSR 연결 규칙

### 32-1. 잘못된 흐름
- Hyperopt 최고 수익 파라미터 바로 실거래

### 32-2. 올바른 흐름
1. Hyperopt로 후보 다수 생성
2. 후보별 lookahead/recursive 통과 확인
3. walk-forward OOS 성능 비교
4. PBO로 과최적화 위험 측정
5. DSR로 성과 유의성 보정
6. 통과 후보만 canary 실거래

### 32-3. 운영 룰
- “최고 수익”보다 “검증 통과 수”가 더 중요한 지표
- 탐색 공간을 넓혔다면 기준을 더 엄격하게 적용

---

## 33) 정밀도 보강: 실전 의사결정 기준표 (채택/보류/폐기)

### 채택 (Promote)
- lookahead/recursive 통과
- OOS 성과 유지
- 비용 스트레스에서도 순수익 유지
- DSR > 0 and PBO 수용 범위
- 운영 안정성 이슈 없음(주문/보호주문/모니터링)

### 보류 (Hold)
- 성과는 괜찮으나 표본 부족
- OOS 편차 과대
- 운영 이슈(체결/재시도/SL 등록 누락) 남아 있음

### 폐기 (Reject)
- lookahead 또는 recursive 실패
- DSR <= 0
- 비용 반영 후 기대값 음수
- 실거래에서 구조적 실행 문제 반복

---

## 34) 고급 포트폴리오 이론 (전략 1개 -> 전략 묶음 운용)

### 34-1. Risk Parity
- 의미: 각 자산/전략이 전체 변동성에 기여하는 비중을 비슷하게 맞추는 방식.
- 언제 사용: 단일 코인 몰빵을 넘어 다중 심볼/다중 전략으로 확장할 때.
- 핵심: 수익률보다 “리스크 기여도”를 먼저 맞춘다.

### 34-2. Equal Weight vs Volatility Targeting
- Equal Weight: 단순하지만 변동성 높은 자산이 리스크를 과점할 수 있음.
- Volatility Targeting: 목표 변동성(예: 연 20%)에 맞춰 레버리지/비중을 조절.
- 실무: 소액 고레버리지 계정일수록 변동성 타게팅이 생존성에 중요.

### 34-3. Correlation Breakdown (상관 붕괴)
- 의미: 평소엔 분산되던 자산이 위기 때 같이 움직이는 현상.
- 대응: 정상장 상관행렬만 믿지 말고 스트레스 상관 시나리오 별도 계산.

### 34-4. Tail Hedging 사고방식
- 의미: 평소 비용이 들더라도 급락 구간의 계좌 파괴를 줄이는 보호 구조.
- 실무: “수익 극대화” 전략이라도 tail 이벤트 한 번에 종료되면 장기 기대값이 무의미.

---

## 35) 고급 통계/계량 (중급에서 상급으로 가는 핵심)

### 35-1. Bootstrap (부트스트랩)
- 의미: 표본 재추출로 성과 지표의 불확실성 구간을 추정.
- 언제 사용: 트레이드 수가 적은 전략의 과신 방지.
- 산출물: Sharpe/Expectancy의 신뢰구간(CI).

### 35-2. Bayesian Updating
- 의미: 새로운 데이터가 들어올 때 사전확률(prior)을 사후확률(posterior)로 갱신.
- 언제 사용: 전략 성능이 시간에 따라 변하는 환경.
- 실무: “최근 성과가 나쁘다”를 감정이 아니라 확률적으로 해석.

### 35-3. Regime Shift / Structural Break
- 의미: 시장 생성 메커니즘이 바뀌어 과거 관계가 깨지는 현상.
- 언제 사용: 갑자기 전략이 장기간 무력화될 때.
- 체크: rolling 통계, 변화점 탐지, 구간별 파라미터 안정성.

### 35-4. Heavy Tail / Non-Normality
- 의미: 금융수익률은 정규분포보다 꼬리가 두꺼운 경우가 많음.
- 실무 영향: 평균/분산 기반 지표만으로 위험을 과소평가.
- 대응: CVaR, tail loss, worst-decile 분석 병행.

### 35-5. Monte Carlo Simulation (몬테카를로 시뮬레이션)
- 의미: 수익률/트레이드 순서를 다수 시나리오로 재샘플링해 전략의 분포적 리스크를 추정하는 방법.
- 언제 사용:
  - “이 전략이 운 좋게 좋았던 건지” 확인할 때
  - 최대낙폭/파산확률/복구기간 분포를 보고 싶을 때
  - 포지션 사이징 변경 전 안정성 점검할 때
- 자주 쓰는 방식:
  - Trade shuffle: 트레이드 순서를 랜덤 섞어 경로 의존성 확인
  - Bootstrap with replacement: 트레이드 샘플 재추출
  - Block bootstrap: 자기상관 구조를 일부 보존하며 재샘플링
- 해석 포인트:
  - 평균 수익보다 `최악 5% 시나리오`, `MDD 상위 분위수`, `ruin 확률`을 우선 본다.
  - 본 시뮬레이션에서 생존이 불안정하면 라이브 배팅 규모를 줄여야 한다.
- 실수 포인트:
  - 정규분포 가정만으로 시뮬레이션해 tail risk를 과소평가
  - 거래비용/슬리피지를 생략해 결과를 과대평가

---

## 36) 체결 비용 모델 심화 (슬리피지 -> 임팩트 모델)

### 36-1. Transaction Cost Decomposition
- 총비용 = 수수료 + 스프레드 + 슬리피지 + 시장충격 + 펀딩.
- 실무: 백테스트에서 최소 5개 항목 분리 추적.

### 36-2. Implementation Shortfall
- 의미: 의사결정 시점의 이상 가격 대비 실제 체결 성과 손실.
- 언제 사용: “신호는 맞았는데 돈이 안 벌리는” 문제 진단.

### 36-3. Market Impact 모델
- 직관 모델 예시:
```text
impact ~ k * (order_size / ADV)^alpha
```
- `ADV`: 평균 거래량, `alpha`는 보통 0~1 사이 추정.
- 의미: 주문이 클수록 비선형적으로 체결 품질 악화 가능.

### 36-4. 체결 전략 (Execution Policy)
- TWAP: 시간 분할 체결, 단순하고 안정적.
- VWAP: 거래량 비중 반영 체결.
- Sniping/Immediate: 빠르지만 비용 상승 가능.
- 실무: 전략 우위보다 체결 정책이 PnL을 더 크게 좌우하기도 함.

---

## 37) 멀티전략 결합 (단일 알파 -> 알파 포트폴리오)

### 37-1. Strategy Ensemble
- 의미: 상이한 전략(추세/역추세/브레이크아웃 등)을 동시에 운용.
- 장점: 단일 전략 실패 구간 완화.
- 리스크: 전략 간 상관이 높으면 분산효과가 사라짐.

### 37-2. Meta-Allocation
- 의미: 전략별 가중치를 동적으로 조절하는 상위 레이어.
- 방법: 성과 모멘텀, 변동성 가중, drawdown 페널티 기반.

### 37-3. Kill/Throttle Rules
- Kill: 전략 비활성화 (예: 기준 DD 초과, DSR 붕괴).
- Throttle: 비중 축소 (예: 성과 저하 시 50% 감축).
- 실무: 전략을 “온/오프”로만 관리하지 말고 연속적으로 조절.

### 37-4. 공통 실패모드 관리
- 여러 전략이 같은 데이터/같은 체결 경로를 공유하면 동시 실패 가능.
- 대응: 데이터 소스 다변화, 실행 경로 분리, 장애 격리.

---

## 38) 실전 트랙레코드/검증 거버넌스 (진짜 상위권으로 가는 마지막 단계)

### 38-1. OOS Track Record 기준
- 최소 수개월 이상 OOS + 라이브 소액 실적 축적.
- 단기 고수익보다 “안정성/재현성”을 우선 판단.

### 38-2. Change Management
- 전략/파라미터 변경 시 버전 태깅 + 변경이유 + 검증결과 필수 기록.
- 무기록 변경은 성과 해석 불가능.

### 38-3. Deployment Gate
- 배포 전 필수 통과:
  - lookahead/recursive OK
  - 비용 스트레스 OK
  - PBO/DSR OK
  - 운영 안정성 테스트 OK

### 38-4. Post-Trade Analytics
- 체결 후 반드시 남길 것:
  - 예상 체결가 vs 실제 체결가
  - 주문 거절/재시도 히스토리
  - 신호 품질 점수와 실제 성과의 대응

### 38-5. 투자자/운용자 관점 분리
- 연구자 관점: 모델 품질/통계 유의성
- 운용자 관점: 생존성/운영상 안전/오류 회복력
- 둘 중 하나라도 약하면 장기성과가 무너짐.

---

## 39) “일반 퀀트 투자자 상회” 자기진단 확장

아래를 만족하면 “평균 상회”에 가깝다.

1. 단일 전략이 아니라 최소 2~3 전략의 상관 기반 결합을 설명할 수 있다.
2. Sharpe 외 DSR/PBO/CVaR를 함께 보고 의사결정한다.
3. 비용모델에 시장충격(impact)까지 포함해 백테스트한다.
4. 실거래 변경관리(버전/검증/릴리즈 노트)를 운영한다.
5. 전략 폐기 기준과 재활성화 기준이 문서화되어 있다.
6. 라이브 장애(데몬 다운/WS flap/주문 거절) 대응 시나리오가 자동화되어 있다.
7. OOS/라이브 성과를 월간 리스크 리포트로 관리한다.

---

## 40) 기존 개념 점검 결과와 보강 항목 (핵심 누락 보완)

이 섹션은 “기존에 이미 있던 개념” 중 실전에서 특히 오해가 잦은 부분을 보강한 항목이다.

### 40-1. Purged K-Fold / Embargo (데이터 누수 고급 방어)
- 의미: 시계열에서 인접 표본 간 정보 누수를 막기 위해 학습/검증 경계 주변 데이터를 비우는 방식.
- 언제 사용: ML 기반 신호, 라벨이 미래 구간을 포함하는 경우.
- 왜 중요한가: 일반 K-Fold/TimeSeriesSplit만으로도 미세 누수가 남을 수 있음.
- 실수 포인트: purge/embargo 없이 높은 검증 점수를 신뢰.

### 40-2. Survivorship Bias / Selection Bias / Data Snooping
- Survivorship Bias: 살아남은 종목만 보면 성과 과대평가.
- Selection Bias: 연구자가 유리한 구간/자산만 선택해 결과 왜곡.
- Data Snooping: 같은 데이터로 반복 실험해 우연 승자를 “진짜”로 착각.
- 실무 대응: 후보군 고정, 구간 사전정의, 실험 로그 강제 저장.

### 40-3. Kelly Criterion / Fractional Kelly
- Kelly 의미: 기대값과 승률 기반 최적 배팅비율 이론.
- 왜 주의해야 하나: 추정 오차에 매우 민감하여 실전 과배팅 유발.
- 실무 권장: Full Kelly 대신 Fractional Kelly(예: 0.25~0.5 Kelly) 사용.
- 연결 개념: risk of ruin, drawdown tolerance.

### 40-4. Drawdown Duration (낙폭 기간)
- 의미: 손실폭(깊이)뿐 아니라 회복까지 걸린 시간(길이).
- 왜 중요한가: MDD가 같아도 장기간 회복 지연 전략은 운영 난이도 급증.
- 실무 기준: MDD와 함께 Max DD Duration을 동시 모니터링.

### 40-5. CVaR (Conditional Value at Risk)
- 의미: 최악의 손실 구간(꼬리)에서 평균적으로 얼마나 잃는지 측정.
- 언제 사용: 꼬리위험이 큰 고레버리지/알트 전략.
- 실수 포인트: VaR만 보고 “그 이후 손실 크기”를 무시.

### 40-6. Capacity (전략 수용량)
- 의미: 전략이 성능 저하 없이 소화 가능한 자본 규모.
- 측정 직관: 주문 규모 / 시장 유동성(ADV, depth) 비율.
- 왜 중요한가: 소액에서 잘 되던 전략이 증액 후 망가지는 대표 원인.

### 40-7. Turnover-Adjusted Alpha
- 의미: 회전율과 비용을 반영한 후에도 남는 알파인지 평가.
- 실무: “신호 정확도”보다 “순알파 지속성”이 더 중요.
- 실수 포인트: 고빈도 신호를 비용 반영 없이 우수 전략으로 착각.

### 40-8. Parameter Stability Map
- 의미: 최적점 하나가 아니라 “근처 파라미터 영역”에서도 성과가 유지되는지 보는 지도.
- 왜 중요한가: 뾰족한 단일 최적점은 과최적화 가능성이 큼.
- 실무 기준: 주변 값에서도 성과/리스크가 완만해야 실전 적합.

### 40-9. Trade Attribution
- 의미: 손익을 신호 품질/체결 품질/비용/슬리피지/운영오류로 분해하는 분석.
- 언제 사용: “왜 돈을 잃었는지” 정확히 진단할 때.
- 실수 포인트: 전략 탓인지 실행 탓인지 분리하지 않고 파라미터만 조정.

### 40-10. Reality Check for Paper Trading
- 의미: 페이퍼 성과를 라이브 성과로 과신하지 않기 위한 검증 절차.
- 체크 1: 체결 지연 반영
- 체크 2: 주문 거절/부분체결 반영
- 체크 3: 실제 수수료/펀딩 반영
- 결론: 페이퍼는 “기능 검증”이고, 수익성 검증은 소액 라이브가 최종.

---

## 41) 검증법 풀카탈로그 (누락 없이 정리)

이 섹션은 전략 검증법을 연구-백테스트-운영 단계까지 통합한 목록이다.

### 41-1. Data Quality Validation
- 의미: 입력 데이터가 신뢰 가능한지 먼저 검증.
- 항목: 결측/중복/역순 타임스탬프/비정상 스파이크/거래정지 구간.
- 언제 사용: 모든 실험의 첫 단계.
- 실수 포인트: 신호 검증 전에 데이터 오류를 방치.

### 41-2. Reproducibility Validation
- 의미: 같은 코드+같은 데이터면 결과가 항상 동일해야 함.
- 항목: random seed 고정, 데이터 버전 해시, 실행환경 기록.
- 언제 사용: 백테스트 리포트 승인 전.
- 실수 포인트: 재현 안 되는 성과를 전략 우위로 오해.

### 41-3. Backtest-Engine Integrity Test
- 의미: 백테스트 엔진 자체가 주문/수수료/체결을 올바르게 계산하는지 검증.
- 항목: 단위 테스트, 경계 테스트, 수동 계산 대조 케이스.
- 언제 사용: 엔진 수정 후 항상.
- 실수 포인트: 전략보다 엔진 버그가 성과를 왜곡.

### 41-4. Walk-Forward (Rolling/Anchored/Nested)
- Rolling WF: 학습/검증 윈도우를 함께 이동.
- Anchored WF: 학습 구간은 누적 확대, 검증 구간만 전진.
- Nested WF: 내부 튜닝과 외부 검증을 분리해 leakage 최소화.
- 언제 사용: 시계열 전략의 기본 검증 프레임.

### 41-5. CPCV (Combinatorial Purged Cross-Validation)
- 의미: 시계열 누수 제거 + 다중 분할 조합으로 일반화 성능을 더 엄격히 평가.
- 언제 사용: ML 전략/파라미터 탐색이 큰 경우.
- 실수 포인트: 단일 split 결과를 과신.

### 41-6. White’s Reality Check / Hansen SPA
- White RC: 다중 전략 탐색 후 “최고 성과”의 유의성 검정.
- Hansen SPA: 성능 열세 후보 영향 줄여 RC의 검정력 보완.
- 언제 사용: 전략 후보가 많을 때.
- 실수 포인트: p-value 검정 없이 최고 전략만 채택.

### 41-7. Diebold-Mariano Test
- 의미: 두 예측/전략의 out-of-sample 예측오차 차이가 유의한지 검정.
- 언제 사용: 전략 A/B 우열 비교.
- 실수 포인트: 평균 성과 차이만 보고 통계 유의성 미확인.

### 41-8. PSR (Probabilistic Sharpe Ratio)
- 의미: 관측 Sharpe가 기준 Sharpe를 초과할 확률 추정.
- 언제 사용: 표본 수가 제한된 전략의 샤프 해석 보강.
- 연관 개념: DSR, skew, kurtosis.

### 41-9. Parameter Perturbation / Sensitivity Test
- 의미: 최적 파라미터 주변을 흔들어도 성과가 유지되는지 확인.
- 언제 사용: Hyperopt 이후 채택 전.
- 기준: 주변 영역에서 성과가 급락하면 과최적화 의심.

### 41-10. Scenario Stress Test
- 의미: 악조건 시나리오에서 전략 생존성을 확인.
- 시나리오: 수수료 증가, 슬리피지 증가, 지연 체결, 급변동, 유동성 감소.
- 언제 사용: 실거래 배포 직전.

### 41-11. Monte Carlo Path Test
- 의미: 트레이드 순서/수익률 경로 재샘플링으로 DD/ruin 분포를 추정.
- 언제 사용: 사이징/레버리지 변경 전 필수.
- 판독: 평균보다 하위 분위수(5%, 1%) 리스크를 우선 확인.

### 41-12. Execution Validation (Replay/Shadow)
- Replay: 과거 체결 이벤트 재생으로 주문 로직 검증.
- Shadow: 라이브 시장에서 주문은 내지 않고 의사결정만 동시 추적.
- 언제 사용: 실거래 투입 직전/투입 초기.

### 41-13. Live Canary Validation
- 의미: 극소 자본으로 실제 시장 검증.
- 핵심: 전략 검증 + 운영 검증(에러 복구/SL 등록/중복주문 방지) 동시 수행.
- 실수 포인트: canary 없이 본계정 확대.

### 41-14. Post-Deployment Drift Validation
- 의미: 배포 후 성능 저하 원인이 시장 변화인지 시스템 이상인지 검증.
- 항목: feature drift, execution drift, cost drift, regime drift.
- 언제 사용: 주간/월간 운영 리포트.

---

## 42) 검증 단계별 필수 통과 기준 (게이트 설계)

### 42-1. 연구 게이트
- 데이터 품질 체크 통과.
- lookahead/recursive 통과.
- OOS 성과 최소 기준 충족.

### 42-2. 통계 게이트
- PBO/DSR/PSR 등 유의성 기준 충족.
- 다중검정 보정 결과가 유의.
- 파라미터 민감도 테스트에서 급락 구간 제한.

### 42-3. 실행 게이트
- 주문 어댑터 단위테스트 통과.
- 수수료/슬리피지/지연 스트레스에서 생존.
- 보호주문(SL/TP) 등록 검증 자동화 완료.

### 42-4. 운영 게이트
- supervisor/monitoring/alert 정상.
- 중복 데몬/중복 주문 방지 로직 검증 완료.
- 장애 복구 시나리오 리허설 완료.

### 42-5. 배포 게이트
- canary 기간 사고 0건 또는 허용 범위 이내.
- 성과 드리프트가 허용 범위 이내.
- 변경관리 문서(버전/변경이유/검증결과) 완료.

---

## 43) 검증 누락 방지 체크리스트 (실전 사용용)

1. 데이터 무결성 검증 했는가.
2. 재현성(동일 결과) 검증 했는가.
3. lookahead/recursive 결과를 보관했는가.
4. walk-forward OOS 결과를 구간별로 봤는가.
5. PBO/DSR/PSR를 함께 확인했는가.
6. 파라미터 민감도 지도를 만들었는가.
7. 비용 스트레스 테스트를 했는가.
8. Monte Carlo 경로 리스크를 계산했는가.
9. 주문 실행 품질(거절/지연/슬리피지)을 측정했는가.
10. 보호주문 등록 검증 자동화가 있는가.
11. canary 실거래 기록이 있는가.
12. 배포 후 드리프트 모니터링이 있는가.

---

문서 끝.
