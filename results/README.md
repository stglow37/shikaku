# 실험 결과

`python -m experiments.run`은 실행마다 고유한 디렉터리를 만든다.

- `config.json`: 실제 적용한 알고리즘 옵션, 입력 크기, 시간 제한.
- `report.json`: 실행 환경, Git 상태, 소스 해시, 검증 및 계산 결과.
- `sources.json`: 실행 당시 Python 코드 원문. 미커밋 변경도 재현할 수 있다.

한 실행 중에는 진행 결과를 같은 보고서에 저장하며, 다음 실행은 새 디렉터리를 사용한다.
RUNNING/FAILED/INTERRUPTED는 실험 실행 상태이고, 개별 계산의 OPTIMAL/TIME_LIMIT와 다르다.
시간은 단일 실행 관측값이다. 전체 실험 소요 시간과 solver의 elapsed_seconds는 다르다.

`legacy-baseline/report.json`은 디렉터리 정리 이전의 결과를 그대로 보관한 것이다.
당시 저장하지 않은 코드 스냅샷과 설정 파일은 소급해서 만들어 넣지 않았다.
