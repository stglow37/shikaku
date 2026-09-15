# 시카쿠 직사각형 분할 연구

정수 n에 대해 n×n 격자의 직사각형 분할에서 서로 다른 넓이의 최대 개수 k(n)을 계산한다.
Python 3.10 이상, 표준 라이브러리만 사용한다. 아래 명령은 프로젝트 루트에서 실행한다.

## 실행

```powershell
python -m shikaku 5
python -m shikaku 6 --time-limit 10 --output result_n6.json
python -m shikaku 4 --config experiments/configs/exhaustive.json
python -m unittest discover -s tests -v
python -m experiments.run
python -m experiments.run --config experiments/configs/exhaustive.json --sizes 1 2 3 4
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
- `shikaku/config.py`, `__main__.py`: 설정 검증과 공통 실행 명령.
- `tests/`: 독립 완전탐색과 회귀 검증.
- `experiments/configs/`: 기준 설정 및 전체 열거 설정.
- `experiments/run.py`: 설정별 실험 실행 및 소스 스냅샷 보관.
- `results/`: 실행별 결과. 기존 결과는 `legacy-baseline/`에 보존했다.
- `outdated/`: 이전 연구 버전. 현재 코드에서 가져오지 않는다.

별도의 CP-SAT/Exact Cover 구현이나 개선 옵션은 구현할 때 추가한다.
기준 알고리즘을 복사한 v2/v3 파일을 만들지 않고, 명시된 설정과 테스트로 기준 동작을 유지한다.

## 기존 파일의 새 위치

`baseline_solver.py`는 `shikaku/` 패키지로 분리했다. 실행은 `python -m shikaku`를 사용한다.
`baseline_algorithm.md`는 `docs/baseline.md`, 연구 노트는 `docs/research_notes.md`로 옮겼다.
`test_baseline_solver.py`는 `tests/`, `run_baseline_experiments.py`는 `experiments/run.py`로 정리했다.
