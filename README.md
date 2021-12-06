# main function 로직
usr 객체 세팅

🛎 mqtt: subscriber로 `setting/{serial num}` 경로에 세팅 정보가 들어올 경우 usr 객체에 저장

1) if not usr.sleep(잠들지 않았다면)
    -  조도센서로 무드등 관리
    -  human 유무 판단하여 human이 1시간 전부터 있었으면
        수면 시작
    -  버튼 누르는 이벤트 발생하면
        수면 시작
2) if usr.sleep(잠들었다면)
    while True: 수면 종료가 될때까지 무한루프
    -  human==False이면
        -  현재 시각이 기상 목표 시각 이후이면 

            수면 종료

            🛎 mqtt: publisher로 `record` 경로에 수면 기록 서버로 전송

            break

        - 현재 시각이 기상 목표 시각 이전이면
        
            break_out 개수 증가

            방해금지모드가 아니면 human 유무 체크하면서 human이 돌아올때까지 light on
            
            light off
            
            break

# 버전 정보
`2021.11.24`
autolight_version2.py

✔ 조도센서, 버튼으로 조정하도록 무드등 구현 완료

✔ 수면모드 구현 완료

✔ 초음파 센서 인간 탐지 기능 구현 완료

`2021.11.29`
 autolight_version3.py

✔ mqtt 통신 구현 완료

✔ mqtt 세팅 정보 usr 객체 입력 구현

✔ 수면, 기상 설정 시각대로 수면등 관리 기능 추가

# 테스트 파일

- test_led.py

- test_rainbow.py

- mqtt_sample.py