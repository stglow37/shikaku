# 실험 결과

## 2026-09-20 연구 결과 안내

- [연구 보고서](../docs/research_progress.md): 증명, 계산 결과, 구현 및 후속 연구.
- [최종 결과표](research-20260920/table.md): n=1,…,40의 하한·상한·정확값.
- [검증된 좌표와 출처](research-20260920/summary.json): 모든 최종 증거와 원본 실행 연결.
- [분할 그림](research-20260920/partitions.png), [상·하한 그림](research-20260920/bounds.png).
- [정보학 논문용 비교 실험](../docs/paper_benchmark_results.md): 동일 예산의 solver 비교와 제거 실험.

`paper-benchmarks/`에는 pilot, 수정 전 진단 실행, 수정 후 최종 159-trial 실행을
보관한다. 각 실행의 `STATUS.md`가 있으면 그 용도를 우선 확인한다.

`20260920T...` 폴더들은 이번 연구의 개별 실행 기록이다. 미확정 결과도
실험 이력으로 보존하며, 최종 결론은 위 집계 자료에서 확인한다.
`20260920T104557975862Z-21e0956c`는 겹쳐 실행한 26∼29 탐색 기록으로,
최종 집계에는 사용하지 않았다. `experiments/strip*_trials.json`은 초기 탐색
기록이며, 소스 스냅샷을 갖춘 본 실험과 구분한다.

## 개별 실행의 형식

`python -m experiments.run`은 실행마다 고유한 디렉터리를 만든다.

- `config.json`: 실제 적용한 알고리즘 옵션, 입력 크기, 시간 제한.
- `report.json`: 실행 환경, Git 상태, 소스 해시, 검증 및 계산 결과.
- `sources.json`: 실행 당시 Python 코드 원문. 미커밋 변경도 재현할 수 있다.

한 실행 중에는 진행 결과를 같은 보고서에 저장하며, 다음 실행은 새 디렉터리를 사용한다.
RUNNING/FAILED/INTERRUPTED는 실험 실행 상태이고, 개별 계산의 OPTIMAL/TIME_LIMIT와 다르다.
시간은 단일 실행 관측값이다. 전체 실험 소요 시간과 solver의 elapsed_seconds는 다르다.

`legacy-baseline/report.json`은 디렉터리 정리 이전의 결과를 그대로 보관한 것이다.
당시 저장하지 않은 코드 스냅샷과 설정 파일은 소급해서 만들어 넣지 않았다.
