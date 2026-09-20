# 시카쿠 직사각형 분할 연구

정수 n에 대해 n×n 격자의 직사각형 분할에서 서로 다른 넓이의 최대 개수 k(n)을 계산한다.
Python 3.10 이상. 기준 탐색과 명시적 구성은 표준 라이브러리만 사용한다.
추가한 CP-SAT 및 띠 최적화는 선택 의존성 OR-Tools를 사용한다.
아래 명령은 프로젝트 루트에서 실행한다.

## 2026-09-20 연구 진행

- 일반 하한을 `k(16t) >= 22t-1`로 개선했다. 점근 계수는 **11/8=1.375**이며,
  기존 4/3보다 크다. [구성과 증명](docs/theory_progress.md).
- 독립적인 CP-SAT 정확 탐색과 가로 띠 구성 최적화를 구현했다.
- 가능한 넓이의 상한 U(n)을 소수 체로 계산하고, 이 상한만으로는 점근 계수
  √2를 낮출 수 없음을 분석했다. [상한 분석](docs/area_upper.md).
- [이번 연구 보고서](docs/research_progress.md)에 계산 결과, 검증과 남은 문제를 정리했다.
- n=1,…,26 및 n=33의 정확값과 n≤40의 검증된 범위는
  [최종 결과표](results/research-20260920/table.md)에서 확인할 수 있다.

## 실행

```powershell
python -m shikaku 5
python -m shikaku 6 --time-limit 10 --output result_n6.json
python -m shikaku 4 --config experiments/configs/exhaustive.json
python -m unittest discover -s tests -v
python -m experiments.run
python -m experiments.run --config experiments/configs/exhaustive.json --sizes 1 2 3 4

# 선택 풀이기
python -m pip install -r requirements-cpsat.txt
python -m shikaku 14 --config experiments/configs/cpsat.json --time-limit 10
python -m shikaku 20 --config experiments/configs/strips4.json --time-limit 15
python -m experiments.theory_strip
```

기본 설정은 높이 배열 탐색과 면적 상한이다. `--no-prune`은 설정 파일보다 우선하며
부분 가지치기와 상한 도달 조기 종료를 모두 끈다.
시간 제한으로 정확값이 결정되지 않으면 k는 null이고 증거 분할과 상·하한을 반환한다.

## 파일 배치

- `docs/research_notes.md`: 전체 연구 노트.
- `docs/baseline.md`: 기준 알고리즘, 완전성 및 가지치기 근거.
- `shikaku/model.py`: 공통 자료형.
- `shikaku/validation.py`: 증거 분할 검사.
- `shikaku/constructions.py`, `bounds.py`: 초기 구성 및 면적 상한.
- `shikaku/solvers/skyline.py`: 높이 배열 탐색. 같은 탐색기의 개선은 선택 옵션으로 추가한다.
- `shikaku/solvers/cpsat.py`: 모든 직사각형을 변수로 사용하는 독립 정확 풀이기.
- `shikaku/solvers/strips.py`: 가로 띠의 높이와 폭 분할을 최적화하는 구성 탐색.
- `shikaku/improved_constructions.py`: 11/8 하한 구성, 남는 2행 개선, 기존 20×20 구성의 활용.
- `shikaku/config.py`, `__main__.py`: 설정 검증과 공통 실행 명령.
- `tests/`: 독립 완전탐색과 회귀 검증.
- `experiments/configs/`: 기준 설정 및 전체 열거 설정.
- `experiments/run.py`: 설정별 실험 실행 및 소스 스냅샷 보관.
- `results/`: 실행별 결과. 기존 결과는 `legacy-baseline/`에 보존했다.
- `outdated/`: 이전 연구 버전. 현재 코드에서 가져오지 않는다.

CP-SAT의 모델과 종료 상태는 [설명](docs/cpsat.md), 띠 최적화의 범위는
[설명](docs/strips.md)을 참고한다. 띠 최적화의 최적값은 일반 문제의 상한이 아니다.
검증된 분할이 독립적인 일반 상한을 달성했을 때만 일반 문제의 정확값으로 보고한다.
DLX, 대칭 제거, 메모이제이션은 아직 구현하지 않았다.
기준 알고리즘을 복사한 v2/v3 파일을 만들지 않고, 명시된 설정과 테스트로 기준 동작을 유지한다.

## 기존 파일의 새 위치

`baseline_solver.py`는 `shikaku/` 패키지로 분리했다. 실행은 `python -m shikaku`를 사용한다.
`baseline_algorithm.md`는 `docs/baseline.md`, 연구 노트는 `docs/research_notes.md`로 옮겼다.
`test_baseline_solver.py`는 `tests/`, `run_baseline_experiments.py`는 `experiments/run.py`로 정리했다.
