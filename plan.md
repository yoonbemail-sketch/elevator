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

## Insights (요약)

운영 인사이트 **업데이트 트리 + 예시**는 [`INSIGHTS.md`](INSIGHTS.md)가 원본이다.

```text
Environment → IdleFrac → Parking | Zoning(미래)
                └─ sticky 홀콜 배정 → 재배정(미래)
Batch N / Rank-by 로 레짐별 베이스라인 측정
```

## Insight: 파킹이 먹히는 때

유휴 구간이 있을 때 파킹 전략이 의미 있다. 한산·중간 부하에서는 Stay/Lobby/Mid/Spread/Demand가 avg wait·empty travel을 가른다. IdleFrac가 높을수록 파킹이 레짐을 가른다.

**항상 풀가동**에 가까우면 차는 거의 파킹하지 않으므로 파킹 효과가 작아진다. 이때는 **서비스 존 분할**(홀수/짝수층, 저층/고층 뱅크)로 정차 수·도어 시간·왕복 거리를 줄이는 편이 낫다.

**예시.** 같은 seed에서 arrival rate를 올리고 Compare all → 전략 간 차이↓, IdleFrac↓.

이 데모는 고정 시나리오에서 **파킹만** 비교한다.

## Insight: sticky vs reassign 홀콜 배정

배정은 승객이 생긴 **그 순간의** nearest-car cost다. **Sticky**는 한 번 붙이면 고정, **Reassign**(Policy → Hall dispatch)은 매 틱 대기 홀콜을 다시 스코어한다.

**예시** (seed 42, Stay, evening, sticky, tick ~650, IdleFrac 62%): E1이 `#76 @16→L1`을 들고 있는데 **E3/E4는 20층 IDLE**. 전체 스냅샷 + Batch N=100 sticky↔reassign 표는 [`INSIGHTS.md` §3](INSIGHTS.md#3-sticky-vs-reassign-hall-call-dispatch).

**방법.** Policy를 바꾸기 전에 Batch N=100을 `benchmarks/`에 저장한 뒤 한 가지만 바꾸고 다시 돌린다. 기본 evening에서는 reassign이 Stay max wait는 줄였지만 mean wait “공짜 개선”은 아님(Mid는 악화).

파킹(유휴 배치)과 **콜 배정**은 다른 레버다.

## 전략 카탈로그

비행기 boarding(WilMA, back-to-front 등)처럼 **만능 1등 전략은 없다**. 트래픽 레짐에 따라 순위가 바뀐다.

| 전략 | 유휴 차 | 전형적 적합 |
| --- | --- | --- |
| Stay | 마지막 정차층 | 반응형 베이스라인 |
| Lobby | 1층 | 상행 피크(귀가) |
| Mid | 중간층 | 절충 |
| Spread | 축을 따라 균등 홈 | 하행 피크(출근) |
| Demand | call-heat 쪽 | 적응 휴리스틱 |

연구/산업 쪽: arrival-probability parking, up-peak MDP 로비 대수, proactive standby, **zoning**(포화 시).

**Batch N**: 현재 노브로 seed N개를 돌려 전략 mean/win-rate·CSV 로그를 만든다.

## 조절 가능 파라미터

**Policy**: Parking strategy, Hall dispatch (sticky | reassign); future: zoning  
**Environment**: scenario seed, traffic period, interfloor %, door dwell, floors, elevators, capacity, arrival rate, target  
**Playback**: sim speed; batch N

## 이후 확장

- **서비스 존** (홀수/짝수·저/고층) — 고부하 건물의 파킹 보완 레버
- **Arrival-probability parking** / **dynamic lobby count** (MDP)
- **층별 홀 capacity** (로비 vs 상층 대기 상한)
- Building type (office), 층별 인구 가중치, 카 속도(층/틱), 묶음 도착, 에너지 지표
