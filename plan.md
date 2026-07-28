# Elevator Parking Simulator

boarding-sim 인터페이스를 따르는 틱 기반 엘리베이터 **대기 배치(파킹)** 시뮬레이터.

기본 건물은 **아파트**다. UI는 영문.

## 목표

유휴 엘리베이터를 **어느 층에 보내 대기시킬지**에 따라 운용 효율이 어떻게 달라지는지 시각적으로 비교한다.

## 공정 비교

- **Scenario seed**로 승객 스트림을 고정한 뒤, 파킹 전략만 바꿔 비교한다.
- **Replay** = 같은 스트림 재실행
- **Compare all** = 브라우저에서 headless로 전 전략 일괄 실행 (서버 없음)

## 아파트 트래픽 (기본)

OD는 **아파트** 가정: 로비↔주거층이 기본, 주거층↔주거층은 interfloor만.

### Traffic period (출발층 믹스)

| 시간대 | 출발 분포 (대략) | 이야기 |
| --- | --- | --- |
| **Morning egress** | 상부 ~90% / 로비 ~10% | 출근·외출 |
| **Evening ingress** | 로비 ~90% / 상부 ~10% | 귀가 |
| **Midday / off-peak** | 로비 ~45% / 상부 ~55% | 주간 혼재 |

목적지는 아래 규칙으로 뽑는다 (period와 독립).

### Arrival rate (도착률)

틱마다 **최대 1명**이 `p = arrivalRate`로 등장하는 Bernoulli 시행. 기본 **15%** → 평균 약 6.7틱에 1명. 연속시간 Poisson의 이산 근사(지수 간격 샘플링은 아님).

시나리오 길이·혼잡도에 직접 영향. seed와 함께 시나리오 키에 포함.

### Interfloor trips (층간 통행)

**상부 출발**일 때 목적지가 로비가 아니라 **다른 상부층**일 확률. 기본 **10%**.

- 로비 출발 → 항상 상부
- 상부 출발 → `(1 − interfloor%)` 로비, `interfloor%` 다른 주거층

낮추면 상하행(로비) 위주, 높이면 중간층 정차가 늘어난다.

오피스형 임의 OD는 이후 building-type 변수로 분리.

## 배차 / 탑승

Collective **SCAN**: 진행 방향과 같은 홀콜만 정차·탑승. 턴어라운드 층에서만 반대 방향 탑승 허용  
→ 하행 호출 3/4/6/7이면 **7→6→4→3→1**.

## 건물 뷰

`Out | Fl | E1…En | Hall` — 내린 승객 / 대기 승객, 호버 툴팁

## 핵심 지표

- Avg / Max Wait (ticks) — 서비스 품질 / 랭킹 1차 목표
- Empty Travel (floors)
- **IdleFrac** — IDLE|PARKING car-ticks / (ticks × elevators). 포화도 진단. ≥25% parking-sensitive, &lt;10% saturated, 그 사이 mixed
- Ticks / Completed

컨트롤은 **Policy**(파킹; 이후 zoning) / **Environment**(건물·트래픽·seed) / **Playback**(속도)로 나뉜다.

## Insights (wrap-up)

원본: [`INSIGHTS.md`](INSIGHTS.md) · [`INSIGHTS.ko.md`](INSIGHTS.ko.md) — 포트폴리오용 **스코프 동결**.

1. 만능 파킹 없음 — 레짐별 Batch / Rank-by
2. IdleFrac로 parking-sensitive vs saturated (포화 시 zoning)
3. 파킹 ≠ 홀 배정 — sticky 고아 콜 vs reassign이 Mid mean wait를 악화(근시안 idle steal)
4. Policy 하나 바꿀 때마다 Batch N=100 before/after

idle-steal 등 dispatch 추가 변형은 하지 않음.

## Insight: 파킹이 먹히는 때

유휴가 있을 때만 파킹이 갈라진다. Arrival↑ → Compare 차이↓·IdleFrac↓ → 포화면 존이 다음 레버. 데모는 파킹만 비교.

## Insight: sticky vs reassign

Sticky 고정 / Reassign 매 틱 재스코어. seed 42 Stay: E1이 `#76@16`, E3/E4 IDLE@20. Evening N=100: Stay max↓, Mid mean↑. 표·스냅샷은 INSIGHTS.

## 전략 카탈로그

비행기 boarding(WilMA, back-to-front 등)처럼 **만능 1등 전략은 없다**. 트래픽 레짐에 따라 순위가 바뀐다.

| 전략 | 유휴 차 | 전형적 적합 |
| --- | --- | --- |
| Stay | 마지막 정차층 | 반응형 베이스라인 |
| Lobby | 1층 | 상행 피크(귀가) |
| Mid | 중간층 | 절충 |
| Spread | 축을 따라 균등 홈 | 하행 피크(출근) |
| Demand | call-heat 쪽 | 적응 휴리스틱 |

**Batch N**: seed N개 mean/win-rate·CSV. CLI: `npm run batch:sticky` / `batch:reassign`.

## 조절 가능 파라미터

**Policy**: Parking strategy, Hall dispatch (sticky | reassign)  
**Environment**: scenario seed, traffic period, interfloor %, door dwell, floors, elevators, capacity, arrival rate, target  
**Playback**: sim speed; batch N

## 이후 확장 (보류)

포트폴리오 스토리가 필요할 때만: 서비스 존, arrival-probability parking, MDP 로비 대수, 층별 홀 capacity, office OD.
