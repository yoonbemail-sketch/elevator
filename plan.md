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

- 2층 이상 출발 → 대부분 **1층(로비)** (interfloor %만 제외)
- 1층 출발 → 대부분 **상부 주거층**
- 시간대:
  - **Morning egress**: 상부 → 로비
  - **Evening ingress**: 로비 → 상부
  - **Midday / off-peak**: 양방향
- **Interfloor %**: 주거층↔주거층 통행 비중 (기본 10%)
- 도착: 틱마다 Bernoulli(`arrivalRate`) — 이산 Poisson 근사
- 오피스형 임의 OD는 이후 building-type 변수로 분리

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
