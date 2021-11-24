# main function 로직

1) if not usr.sleep(잠들지 않았다면)
    -  조도센서로 무드등 관리
    -  human 유무 판단하여 human이 1시간 전부터 있었으면
        수면 시작
    -  버튼 누르는 이벤트 발생하면
        수면 시작
2) if usr.sleep(잠들었다면)
    while True: 수면 종료가 될때까지 무한루프
    -  human==False이면
        -  현재 시각이 6시 이후이면 

            수면 종료

            break

        - 현재 시각이 6시 이전이고 방해금지모드가 아니면 
        
            break_out 개수 증가
            
            human 유무 체크하면서 human이 돌아올때까지 light on
            
            break
