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
- 실시간 데이터 관리 (e.g., total asset 계산하기위해선 장 시간 중에는 real time데이터 필요. 미국 장시간, 한국 장시간 고려 필요. graph그릴때도 today 데이터는 계속 바뀜), graph결과 저장하는 db 만들어놓기
  - market_data_service.py 에 새로운 function, is_now_market_open(type) 만들기 (type: 한국, 미국).
  - market_data_service.py 에 새로운 function, is_market_closed(type, date) 만들기 --> true if market open날, closed if 주말이거나 휴일이라서 market open 안하는날
    - FinanceDataReader (fdr) 사용해서 infer하기. 한번 infer성공했을시에 장 휴식날을 내부 db에 넣어놓고 잇는것도 performance 상으로 좋을듯
  - market_data_service.py 안에 있는 get_price(symbol, date, type) 업데이트 (type: 한국, 미국)
    - Abstraction Goal
      - date가 일반날짜일 경우, return closed price
      - date가 쉬는날이라면 (e.g., 주말 or holiday), 마지막 active한 날짜의 closed price 리턴하기
      - date가 오늘이고 장이 열리기 전: 마지막 active한 날짜의 closed price 리턴하기
      - date가 오늘이고 장 중이라면: 최근 5분동안 load햇을경우 그 값 return, 최근 5분동안 load한적 없다면, download 후 최신 realtime price return
      - date가 오늘이고 장 close 후: 오늘 closed price return
    - Performance Goal
      - FinanceDataReader (fdr) 데이터 로드받을때 하루하루씩 받으면 너무 느림
      - congestion control 처럼, db에 현재 얼마나 consecutive하게 (start date ~ end date) 까지 저장되어있는지 기록해놓고, 거기서 벗어났을시에 한번에 1~2달 데이터 한번에 DB 저장해놓으면 좋을듯
      - 로직: 만약 db있을시 바로 read, (db내용도 미리 memory에 올려놓으면 좋을듯). 없을시, 30~60일치 bulk download from FDR한 후에 캐시메모리 올려놓고 그 후 리턴
    - Implementation Detail (정확하지않음, 추후에 수정필요)
      - (1) symbol이 Ticker DB에 없다면 symbol 추가
      - (2) date==today이고 is_now_market_open(type) 일경우
        - 마지막 load시간이 5분 지나지 않았을 경우 --> 마지막 load한 price return
        - 마지막 load시간이 5분 지났을 경우 --> 새로 price download, cache에 insert 후 return
      - (3) date < today이거나, date == today && !is_now_market_open() 일경우
        - ...
- portfolio 그래프 관련 데이터들 db에 저장해놓기. 근데 장 중 데이터는 미리 저장힘드니까 이건 그때그때 불러오게 separate 해두기
  - 혹시 transaction 이 바뀌었을경우, 그래프 결과 reload해야함 --> 버튼만들기
  - 그 후에 graph compute하는 로직과 plot logic separate하기
- 이어서, 대시보드 작업하기 = sigma [모든계좌의 주식보유현황테이블 + 그래프] 이것 또한 db 만들기
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
