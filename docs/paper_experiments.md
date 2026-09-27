# 정보학 논문용 비교·제거 실험 프로토콜

이 문서는 결과를 본 뒤 조건을 바꾸는 일을 피하기 위해 본 실험 전에 고정한
프로토콜이다. 기존 `results/20260920T...` 자료는 수학적 증거와 탐색 이력으로
보존하고, 새 benchmark 결과와 섞거나 덮어쓰지 않는다.

## 연구 질문

1. 같은 CP-SAT solve-call 예산에서 일반 정확 모형은 기준 skyline 탐색과 비교해
   얼마나 많은 사례를 인증하고 얼마나 작은 상·하한 간격을 남기는가?
2. skyline의 상한 기반 가지치기와 조기 종료를 합친 기존 `prune` 모드는 완전
   열거와 비교해 방문 상태와 시간을 얼마나 줄이는가?
3. CP-SAT에서 초기 구성의 품질과 변수 힌트가 탐색 결과에 어떤 영향을 주는가?
4. 어려운 사례에서 일반 CP-SAT과 제한된 띠 구성은 제한 시간 안에 어떤 하한을
   제공하는가?

띠 모형의 최적값은 일반 문제의 상한이 아니다. 따라서 4번은 정확 풀이기의 속도
대결이 아니라 검증된 하한 생성 방법의 비교로만 해석한다.

## 고정 조건

- 주 실험은 `experiments/configs/paper_benchmark.json`을 사용한다.
- 반복 횟수는 3회다. 시간은 완료된 반복의 중앙값을 사용한다.
- CP-SAT과 띠 모형은 worker 1개, seed 0으로 고정한다.
- solver 호출 제한은 정확 비교에서 10초, 어려운 구성 비교에서 30초다.
- 프로세스 제한은 solver 제한보다 60초 길다. 이는 import와 모형 생성의 비정상적
  정지를 막는 안전장치이며 solver 시간으로 해석하지 않는다.
- 모든 trial은 별도 프로세스에서 실행한다. 반환된 좌표는 부모 프로세스가
  `validate_partition`으로 다시 검사한다.
- `k`는 검증된 하한과 독립 상한이 일치할 때만 기록한다.
- timeout은 불가능성이나 반례의 증거가 아니다.

CP-SAT의 기존 `time_limit`은 solve call에만 적용된다. 따라서 논문에는
`model_build_seconds`, `solve_call_seconds`, `process_elapsed_seconds`를 분리해서
보고한다. 서로 다른 solver의 `nodes`는 의미가 다르므로 직접 비교하지 않는다.

## 실험군

### 일반 정확 풀이

- skyline, 상한 기반 탐색 제어 사용
- CP-SAT, 기존 초기 구성과 힌트 사용
- 크기: 4, 5, 6, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20

기존 초기 구성만으로 상한에 도달하는 크기는 탐색 성능 사례에서 분리해
“초기화 단계 인증”으로 표시한다.

### 제거 실험

- skyline `prune=true/false`: 4, 5, 6
- CP-SAT 기존 구성, 힌트 없음: 16, 17, 18, 19
- CP-SAT 순수 11/8 구성, 힌트 사용/미사용: 16, 17, 18, 19

skyline의 `prune=false`는 상태 가지치기와 전역 상한 도달 조기 종료를 함께 끈다.
따라서 이를 순수 가지치기 하나의 효과라고 표현하지 않는다.

`eleven_eighths`는 `best_known`과 다르다. 후자는 외부 20×20 증거도 포함하므로
11/8 정리의 효과를 측정하는 제거 실험에는 사용하지 않는다.

### 어려운 구성 비교

- CP-SAT, 사용 가능한 최선의 명시적 초기 구성: 24, 27, 30, 33
- 높이 6 이하, 띠당 최대 네 조각인 띠 최적화
- 띠 최적화 크기: 24, 27, 30, 33, 36, 40

여기서는 정확 해결률 외에 최선 하한, 독립 상한, 남은 간격과 모델 생성비용을
함께 보고한다.

일반 CP-SAT의 셀-직사각형 incidence는 24에서 이미 6,760,000개다. 증가율을
외삽하면 36과 40은 공유 데스크톱에서 메모리와 모델 생성시간 위험이 크므로 본
실험에서 제외하고 후속 고성능 환경 실험으로 남긴다. 이는 pilot 이후 결과를 보고
선택한 것이 아니라, 기존 n=24 실행의 모델 크기와 자원 안전성에 근거한 사전 변경이다.

## 실행과 재현

먼저 OR-Tools를 지원하는 공식 CPython 환경에서 pilot을 실행한다.

```powershell
python -m pip install -r requirements-cpsat.txt
python -m experiments.benchmark --config experiments/configs/paper_benchmark_pilot.json
python -m experiments.analyze_benchmarks results/<pilot-directory>
```

pilot이 모든 suite에서 유효한 증거를 만들면 본 실험을 실행한다.

```powershell
python -m experiments.benchmark --config experiments/configs/paper_benchmark.json
python -m experiments.analyze_benchmarks results/<benchmark-directory>
```

중단된 실행은 새 결과를 만들지 않고 이어서 실행한다.

```powershell
python -m experiments.benchmark --resume results/<benchmark-directory>
```

각 benchmark 폴더에는 설정, solver별 설정, 원시 trial 결과, 실행 당시 소스와
SHA-256이 저장된다. 집계기는 모든 성공 trial의 좌표를 다시 검사한 후 JSON, CSV,
Markdown 표를 생성한다.

## 해석 기준

- 정확 해결률이 같을 때만 중앙 실행시간을 주된 속도 비교로 사용한다.
- timeout이 섞인 경우 시간 평균 대신 해결률과 최종 간격을 우선한다.
- 3회 반복은 큰 통계적 일반화를 위한 표본이 아니라 실행시간 잡음을 줄이기 위한
  최소 반복이다.
- pilot 이후에는 명백한 구현 오류가 아닌 한 크기·시간·반복 횟수를 변경하지 않는다.
  오류로 변경했다면 커밋과 보고서에 이유를 남긴다.
