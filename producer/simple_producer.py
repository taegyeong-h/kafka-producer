from confluent_kafka import Producer
import sys
import time

# BROKER_LST = 'kafka-broker01:9092,kafka-broker02:9092,kafka-broker03:9092'
BROKER_LST = '192.168.56.100:9092,192.168.56.101:9092,192.168.56.102:9092'
class SimpleProducer:
    def __init__(self, topic, duration=None):
        self.topic = topic
        self.duration = duration if duration is not None else 60
        self.conf = {'bootstrap.servers': BROKER_LST,
                     'queue.buffering.max.messages': 100000,  # 로컬 큐에 최대 10만 건까지 대기 가능
                     'linger.ms': 10  # 10ms 동안 메시지를 모아서 한 번에 쏘는 '배치(Batch)' 치트키
                     }
        self.producer = Producer(self.conf)   # 객체 생성


    def delivery_callback(self, err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            # sys.stderr 출력 버퍼를 강제로 비워주어 터미널 로그가 안 밀리고 즉시 찍히게 개선했네!
            sys.stderr.write(f'%% Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}\n')
            sys.stderr.flush()


    def produce(self):
        cnt = 0
        sys.stdout.write(f"🚀 카프카 대량 데이터 파이프라인 가동 시작 (총 {self.duration}건 발송)\n")

        while cnt < self.duration:
            try:
                self.producer.produce(
                    topic= self.topic,
                    key= str(cnt),
                    value= f"hello world: {cnt}",
                    on_delivery=self.delivery_callback
                )

                # 2. 비동기 이벤트 폴링 (카프카 서버로부터 잘 받았다는 콜백 신호가 왔는지 슥 체크만 하는 명령어일세)
                self.producer.poll(0)

                # [구조 교정] 정상 발송에 성공했으니 카운트를 올리고 0.1초씩 쉬면서 흐름을 제어하세!
                cnt += 1
                time.sleep(0.1)

            except BufferError:
                # 내부 큐가 꽉 차서 터졌을 때만 잠시 멈추고 큐를 비워주는 정석 예외 처리 룰일세!
                sys.stderr.write(f"%% Local queue full ({len(self.producer)} msgs awaiting). Waiting...\n")
                self.producer.poll(1)  # 1초 동안 기다리며 큐를 강제로 비워냄
                time.sleep(1)

            # 3. [최적화 핵심] while 루프가 다 끝나고 '딱 한 번'만 flush()를 때려주는 게 진짜 실무 아키텍처라네!
        sys.stdout.write("📥 모든 메시지 발송 완료! 잔여 데이터 최종 플러시(Flush) 중...\n")
        self.producer.flush()
        sys.stdout.write("✨ 파이프라인 전송 완벽 대성공!\n")

if __name__ == '__main__':
    # 테스트용 'test.hello' 토픽으로 안전하게 60건 슛!
    simple_producer = SimpleProducer(topic='test.hello', duration=60)
    simple_producer.produce()
