# 쫄지마

개인용 생존 금융 대시보드 웹앱입니다. 은행 연동이나 API 없이, 직접 입력한 자산/수입/고정비/지출을 기준으로 “아직 얼마나 버틸 수 있는지”를 보여줍니다.

## 1단계 MVP 기능

- 대시보드
- 현재 자산 입력
- 수입 모드 선택
- 고정비 입력
- 지출 기록
- 자동 계산
- 로컬 JSON 저장
- 간단한 카테고리 분석

## 실행 방법

PowerShell에서 이 폴더로 이동한 뒤 실행하세요.

```powershell
cd D:\01졍\JJol-JiMa
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

브라우저가 열리면 쫄지마 앱을 사용할 수 있습니다.

## 데이터 저장 위치

입력한 데이터는 아래 파일에 저장됩니다.

```text
data/jjol-jima-data.json
```

외부 서버, 은행 API, 결제 기능은 사용하지 않습니다.

## 계산 기준

- 총 자산: 현금, 통장 잔고, 비상금, 받을 돈, 기타 자산 합계
- 이번 달 예상 수입: 선택한 수입 모드 또는 직접 입력값
- 이번 달 변동 지출: 현재 월에 기록된 지출 합계
- 이번 달 남은 돈: 예상 수입 - 고정비 - 변동 지출
- 생존 가능 기간: 총 자산 / 월 순소진액
- 월 순소진액: 고정비 + 이번 달 변동 지출 - 예상 수입

월 순소진액이 0 이하이면 현재 입력값 기준으로는 자산이 줄지 않는 상태로 표시합니다.

## Streamlit Community Cloud 배포

1. 이 저장소를 GitHub에 올립니다.
2. https://share.streamlit.io 에 로그인합니다.
3. New app을 누릅니다.
4. Repository: `ddjung8894-byte/JJol-JiMa`
5. Branch: `main`
6. Main file path: `app.py`
7. Deploy를 누릅니다.

주의: Community Cloud의 로컬 파일 저장은 서버 재시작 시 초기화될 수 있습니다. 중요한 개인 기록은 가끔 `data/jjol-jima-data.json`을 따로 백업하는 편이 좋습니다.
