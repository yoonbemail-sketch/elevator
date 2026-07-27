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

- Avg / Max Wait (ticks)
- Empty Travel (floors)
- Ticks / Completed

## 조절 가능 파라미터

Parking strategy, scenario seed, traffic period, interfloor %, door dwell, floors, elevators, capacity, arrival rate, target, sim speed

## 이후 확장

- **층별 홀 capacity** (로비 vs 상층 대기 상한)
- Building type (office), 층별 인구 가중치, 카 속도(층/틱), 묶음 도착, 에너지 지표
