import json
from kafka import KafkaProducer

class EventProducer:
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers='localhost:9092',  # change if Docker/K8s
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            print("⚠ Kafka connection failed:", e)
            self.producer = None

    def publish(self, topic, event):
        if self.producer:
            self.producer.send(topic, event)
            self.producer.flush()
        else:
            print("Kafka not available. Event skipped:", event)