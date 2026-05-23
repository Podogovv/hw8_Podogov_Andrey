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

## 4. Запуск и проверки
```text
docker compose up -d
```
<img width="1944" height="204" alt="image" src="https://github.com/user-attachments/assets/b37a9686-6fc7-4e13-98c5-a0fb4e38ad95" />

---

```text
Health endpoint
curl http://localhost:8000/health
```
<img width="1039" height="99" alt="image" src="https://github.com/user-attachments/assets/cc5230fa-25f3-4d18-8e45-404559ac3a71" />

---

```text
Predict endpoint
Invoke-RestMethod `
  -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"x":[1,2,3]}'
```
  <img width="523" height="84" alt="image" src="https://github.com/user-attachments/assets/ed509f97-5c3e-4328-bbf1-b74ceca7cdeb" />

---

```text
metrics
curl http://localhost:8000/metrics
```
<img width="1158" height="197" alt="image" src="https://github.com/user-attachments/assets/74c81c4b-b12a-4969-9828-3f9a00db953f" />

---

```text
Prometheus
http://localhost:9090/api/v1/targets
```
<img width="1928" height="330" alt="image" src="https://github.com/user-attachments/assets/7d1dfbe7-d796-48e2-b5ae-724d60318462" />

---

```text
Генерируем трафик
```
<img width="1090" height="248" alt="image" src="https://github.com/user-attachments/assets/77631fa8-44b2-42b1-b54c-ee97c603326d" />

---
## 5. Скриншоты Grafana и Prometheus
```text
Grafana Dashboard
```
<img width="3228" height="1265" alt="image" src="https://github.com/user-attachments/assets/63ee952c-d207-4e0c-89fd-b162f2af8805" />

---

```text
Prometheus
```
<img width="1751" height="561" alt="image" src="https://github.com/user-attachments/assets/a279a996-85d7-42bf-928f-83ad9871b6d3" />

---

```text
Alert
```
<img width="3808" height="1471" alt="alert" src="https://github.com/user-attachments/assets/37c281f2-d956-4055-bc27-ac5b4905f01a" />

## 6. Обнаружить деградацию модели и дрифт

В ходе эксперимента была выполнена проверка модели на наличие деградации и дрифта данных с использованием датасета Wine. В качестве эталонного пакета использовались исходные данные, на которых модель показывала высокое качество классификации. Для имитации data drift распределения нескольких признаков подаваемого в модель пакета данных были искусственно изменены: значения признаков alcohol, malic_acid, color_intensity и proline были масштабированы и смещены относительно эталонного пакета данных. Проведённый KS-тест показал статистически значимое различие распределений между эталонными и текущими данными, что подтверждает наличие дрифта данных. На графиках распределений также видно существенное смещение признаков подаваемого в модель пакета данных относительно эталонного пакета данных. После изменения входных данных наблюдалось снижение точности модели, что свидетельствует о деградации качества модели под влиянием смещение распределения (data drift). Полученные результаты демонстрируют важность мониторинга распределений признаков и качества модели после деплоя ML-системы.

```text
[1] MODEL QUALITY

Reference Accuracy : 1.0000
Current Accuracy   : 0.6111
Accuracy Drop      : 0.3889

```
---

<img width="710" height="400" alt="image" src="https://github.com/user-attachments/assets/da9053b0-a6f0-42dd-8c66-99195b8a61b5" />

---

```text
[3] CLASSIFICATION REPORT
              precision    recall  f1-score   support

           0       0.51      1.00      0.68        18
           1       0.00      0.00      0.00        21
           2       0.79      1.00      0.88        15

    accuracy                           0.61        54
   macro avg       0.43      0.67      0.52        54
weighted avg       0.39      0.61      0.47        54
```
---

<img width="1202" height="852" alt="image" src="https://github.com/user-attachments/assets/715d481a-8f57-4c25-a968-a430a2a9b8ce" />

<img width="456" height="311" alt="image" src="https://github.com/user-attachments/assets/3bc74575-8eb7-4d09-b990-e4766b608a3c" />

