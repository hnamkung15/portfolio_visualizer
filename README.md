# First time setup

```
- Install homebrew
- Install pyenv
- Install python 3.11.9 using pyenv
$ python3 -m venv .venv
$ source env_load.sh
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

# Todo List

- style.css 대시보드에도 적용하기, 리펙토링
- 실시간 데이터 관리 (e.g., total asset 계산하기위해선 장 시간 중에는 real time데이터 필요. 미국 장시간, 한국 장시간 고려 필요. graph그릴때도 today 데이터는 계속 바뀜).
- graph결과 저장하는 db 만들어놓기
- 이어서, 대시보드 작업하기 = sigma [모든계좌의 주식보유현황테이블 + 그래프] 이것 또한 db 만들기
- 혹시 transaction 이 바뀌었을경우, 그래프 결과 reload해야함 --> 버튼만들기
- 전체 자산 Pie chart
  - 카테고리별로 (e.g., 채권, 현금, 주식, etf, 등등)
  - 주식별로
  - S&P 여개 etf했을경우 합쳐주기, QQQ 여러 etf로했을경우 합쳐주기
  - 401k roth / 401k pretax 별로 나눠주기

# Database

```
$ alembic revision -m "baseline"    # analogoous to git init
$ alembic history --verbose         # analogoous to git log
$ alembic revision --autogenerate -m "add country column to account" # analogoous to git commit -m "msg"
$ alembic upgrade head
```
