# Elevator Parking Simulator

boarding-sim 인터페이스를 따르는 틱 기반 엘리베이터 **대기 배치(파킹)** 시뮬레이터.

기본 건물은 **아파트**다.

## 목표

유휴 엘리베이터를 **어느 층에 보내 대기시킬지**에 따라 운용 효율이 어떻게 달라지는지 시각적으로 비교한다.

## 아파트 트래픽 (기본)

- 2층 이상 출발 → 대부분 **1층(로비)** (interfloor %만 제외)
- 1층 출발 → 대부분 **상부 주거층**
- 시간대:
  - **Morning egress**: 상부 → 로비
  - **Evening ingress**: 로비 → 상부
  - **Midday / off-peak**: 양방향
- **Interfloor %**: 주거층↔주거층 통행 비중 (기본 10%)
- 오피스형 임의 OD는 이후 building-type 변수로 분리

## 핵심 지표

- Avg / Max Wait
- Completed
- Empty Travel

## 조절 가능 파라미터

Parking strategy, traffic period, interfloor %, door dwell, floors, elevators, capacity, arrival rate, target, sim speed

## 이후 확장

Building type (office), 층별 인구 가중치, 카 속도(층/틱), 묶음 도착, 에너지 지표
