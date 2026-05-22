## 1. Определить ключевые бизнес- и технические метрики для ML-системы

Для ML-системы онлайн-кинотеатра было выделено четыре основные ветви дерева метрик: бизнес-метрики, метрики приложения, ML-метрики и инфраструктурные метрики. Ветвь бизнес-метрик отражает цели компании и позволяет оценивать влияние ML-системы на продуктовые показатели. В нее входят такие показатели, как рост выручки (Revenue uplift), CTR, Conversion Rate, ARPU, Retention Rate, доступность сервиса и latency p95/p99, поскольку рекомендации напрямую влияют на вовлеченность пользователей и монетизацию платформы.

Ветвь метрик приложения описывает состояние backend-системы и качество разработки. Здесь учитываются CPU и RAM utilization, API latency, throughput, error rate 4xx/5xx, время выполнения запросов, DB latency, slow queries, а также стабильность деплоев и recovery time. Эти метрики помогают принимать архитектурные решения: нужен ли новый сервер, стоит ли переходить на ClickHouse, требуется ли переписывание backend или внедрение Kubernetes.

Отдельная ветвь посвящена ML-метрикам, которые характеризуют качество и эффективность рекомендательной системы. В нее входят inference latency, GPU utilization, CTR, Precision, Recall, Coverage, freshness данных, data drift, concept drift и pipeline success rate. Данные показатели позволяют оценивать качество рекомендаций, необходимость использования GPU, перехода на streaming-архитектуру или внедрения KubeFlow для управления ML-пайплайнами.

Инфраструктурная ветвь дерева включает метрики DevOps и эксплуатации системы. Здесь анализируются CPU/RAM/GPU utilization, network throughput, disk I/O, DB saturation, availability, error budget, container restart count и p95 response time. Эти показатели помогают оценивать эффективность использования существующих ресурсов, выявлять инфраструктурные проблемы, определять допустимые SLO/SLA.


```text
                                  Дерево ML-метрик
                                        │
    ┌------------------------------------------------------------------------┐
    │                       │                        │                       │
    ▼                       ▼                        ▼                       ▼

бизнес                  метрики                  ML                      инфраструктурные 
метрики                 приложения               метрики                 метрики
---------              ------------            ----------------        ----------------
• Revenue              • API latency           • CTR                    • CPU/RAM/GPU
• CTR                  • Throughput            • Recall                 • Disk I/O
• ARPU                 • Error rate            • Drift                  • Availability
• Retention            • DB latency            • GPU usage              • Error budget 
• Availability         • Deploy success        • Inference latency      • p95 latency
```

## 2. SLO
```text
| Метрика     | SLI                            | SLO                | Alert                                            |
|-------------|--------------------------------|--------------------|--------------------------------------------------|
| Latency     | histogram_quantile(0.95, ...)  | p95 < 1 сек        | p95 latency is higher than 1 second for 1 minute |
| Reliability | 5xx / total                    | error rate < 1%    | 5xx error rate is higher than 1% for 2 minutes   |
| Availability| up{job="ml_service"}           | uptime > 99% / 30d | Service is unavailable for more than 1 minute    |
```

## 3. Структура
```text
project/
│
├── app.py
├── requirements.txt
├── Dockerfile
│
├── docker-compose.monitoring.yml
├── prometheus.yml
├── alert_rules.yml
│
└── grafana/
    └── provisioning/
```
