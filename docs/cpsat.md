# CP-SAT 독립 정확 계산

연구 노트 3.10절의 모든 직사각형 모형을 `shikaku/solvers/cpsat.py`에 구현했다.
높이 배열 탐색과 다른 표현을 사용하며, 모든 격자 직사각형 분할을 허용한다.
OR-Tools는 선택 의존성이다. 기존 표준 라이브러리 풀이기는 설치 없이 실행된다.

## 모형과 완전성

각 위치의 직사각형 R에 이진 선택 변수 x_R를 둔다.
각 칸 c에 대해 `sum(x_R for R containing c) = 1`을 요구한다.
따라서 해의 선택 직사각형은 겹침이나 빈칸 없이 전체 격자를 덮는다.
반대로 모든 직사각형 분할은 이 제약의 해이다.

각 가능한 넓이 a에 이진 변수 y_a를 두고
`y_a = max(x_R for area(R) = a)`를 추가한다.
따라서 최적해뿐 아니라 중간 실행 가능 해에서도 `sum(y_a)`는 실제 넓이 종류 수이다.
이 합을 최대화한다. 동일 넓이 조각의 반복은 허용된다.

독립 검사한 기존 구성의 점수를 B, 가능한 넓이 합으로 얻은 상한을 U라 두고
`B <= sum(y_a) <= U`와 `sum(a*y_a) <= n*n`도 추가한다.
초기 구성은 전체 변수의 힌트로 전달한다. 힌트와 하한 제약은 최적해를 제거하지 않는다.

직사각형 변수는 `[n(n+1)/2]^2`개다. 각 칸 덮개 제약에 들어가는 항의 총수는
`[n(n+1)(n+2)/6]^2`개로 O(n^6)이다. 모델 생성 비용과 메모리는 이 항수에
영향을 받으므로 O(n^4)개 변수만으로 자원 요구를 설명할 수 없다.

## 상태와 보증

- OR-Tools의 `OPTIMAL`: 해를 별도 칸 단위 검사한 뒤 정확값으로 반환한다.
- `FEASIBLE`: 해를 검사하여 하한을 갱신하고 solver의 목적함수 상한을 사용한다.
  상·하한이 일치하지 않으면 `k`는 `null`이다.
- `UNKNOWN`: solver의 해와 목적값을 읽지 않는다. 독립 검증한 초기 분할과
  이론적 면적 상한을 보존한다. solver의 기본 상한 필드도 증명에 사용하지 않는다.
- 초기 구성이나 발견한 해가 인증된 상한에 도달하면 solver 상태와 관계없이 정확하다.
  `termination=certified_bounds_meet`와 원래 `solver_status`로 구별한다.
- 이 문제는 초기 구성이 항상 있으므로 `INFEASIBLE`이나 `MODEL_INVALID`는 오류다.

`status`는 기존 풀이기와 동일하게 인증된 정확값에는 `OPTIMAL`, 시간 제한으로
상·하한이 남은 실행에는 `TIME_LIMIT`을 사용한다. `solver_status`는 OR-Tools의
실제 상태다. `solver_upper_bound`는 부동소수점 상한을 보수적으로 올림한 정수다.
실행 가능 증거는 쉽게 별도 검사할 수 있으나, solver의 상한 및 최적 판정은
OR-Tools의 정확성에 의존한다. 별도의 UNSAT 증명 파일을 생성하는 구현은 아니다.

## 시간 제한과 재현성

`time_limit`은 CP-SAT `solve` 호출에 전달하는 제한이다. Python의 모델 구성,
의존성 import, 해 추출과 검증을 중단하지 않으므로 전체 실행 시간 제한과 다르다.
출력에 `dependency_import_seconds`, `model_build_seconds`, `solve_call_seconds`,
`solver_wall_seconds`, `elapsed_seconds`를 분리해 기록한다.

기본은 worker 1개와 random seed 0이다. worker 수를 늘리면 탐색 결과와 실행 시간이
달라질 수 있다. OR-Tools 버전, worker 수, seed를 결과에 저장한다.
`nodes`는 CP-SAT의 분기 수를 뜻하며, 높이 배열 풀이기의 방문 상태 수와 직접 비교할 수 없다.

## 실행과 검증

```sh
python -m pip install -r requirements-cpsat.txt
python -m shikaku 9 --config experiments/configs/cpsat.json --time-limit 10
python -m experiments.run --config experiments/configs/cpsat.json --sizes 1 2 3 4 5 6 9 10 --time-limit 10
python -m unittest tests.test_cpsat -v
```

테스트는 n=1..4에서 독립 칸 기반 완전열거의 정확값과 비교하고 모든 증거를 검증한다.
시간 0으로 실제 `UNKNOWN`을 만들며, 초기 구성과 상한이 일치하는 경우도 구별한다.
모의 `FEASIBLE` 응답으로 실행 가능 판정을 최적 판정으로 오인하지 않는지 검사한다.
OR-Tools가 없는 환경에서는 solver 실행 테스트만 skip하고 입력 검사와 선택 의존성
안내 테스트는 실행한다.

참고: [Google CP-SAT 상태 설명](https://developers.google.com/optimization/cp/cp_solver),
[OR-Tools Python 구현](https://github.com/google/or-tools/blob/stable/ortools/sat/python/cp_model.py).
