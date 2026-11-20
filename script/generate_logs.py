#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LogCommerce — Générateur de logs e-commerce avec Faker.

Sorties :
  generated_logs/logs_ecommerce.csv   (CSV, extra_data au format JSON)
  generated_logs/logs_ecommerce.json  (JSON Lines / NDJSON)

Les événements sont fictifs et conçus pour tester Logstash, Elasticsearch,
Kibana et les alertes du projet LogCommerce.

Installation :
    pip install Faker

Exécution :
    python generate_logs.py
    python generate_logs.py --count 5000 --payment-spike-count 100
    python generate_logs.py --count 10000 --payment-spike-count 150 \
        --payment-spike-duration 5 --traffic-spike-count 300
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from faker import Faker

fake = Faker("fr_FR")

PRODUCTS = [
    ("PRD-1001", "Smartphone", 899.90),
    ("PRD-1002", "Ordinateur portable", 2499.00),
    ("PRD-1003", "Casque audio", 189.50),
    ("PRD-1004", "Clavier mécanique", 129.00),
    ("PRD-1005", "Écran 27 pouces", 749.00),
    ("PRD-1006", "Souris sans fil", 79.90),
    ("PRD-1007", "Montre connectée", 499.00),
    ("PRD-1008", "Disque SSD", 219.00),
    ("PRD-1009", "Tablette", 1199.00),
    ("PRD-1010", "Webcam", 99.00),
]
SERVICES = ["api-gateway", "order-service", "payment-service",
            "catalog-service", "cart-service", "web-frontend", "database"]
COUNTRIES = ["TN", "FR", "DE", "IT", "US", "GB", "ES", "MA"]
PAYMENT_METHODS = ["card", "paypal", "bank_transfer"]
CURRENCIES = ["EUR", "TND"]
CSV_FIELDS = [
    "@timestamp", "event_id", "level", "service", "event_type", "message",
    "environment", "host", "http_method", "http_status", "endpoint",
    "response_time_ms", "db_latency_ms", "user_id", "session_id",
    "ip_address", "country", "user_agent", "is_bot", "order_id",
    "product_id", "product_name", "payment_id", "payment_method",
    "amount", "currency", "status", "processing_time_ms",
    "is_suspicious", "tags", "extra_data",
]


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class LogFactory:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        if args.seed is not None:
            random.seed(args.seed)
            Faker.seed(args.seed)
            fake.seed_instance(args.seed)

        self.start = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        self.end = self.start + timedelta(days=1)
        self.events: list[dict[str, Any]] = []
        self.spike_start = self.start + timedelta(hours=12)
        self.traffic_start = self.start + timedelta(hours=15)

    def time(self) -> datetime:
        return self.start + timedelta(seconds=random.randint(0, 86399))

    def base(self, event_type: str, service: str, level: str,
             timestamp: datetime, message: str, **values: Any) -> dict[str, Any]:
        event = {
            "@timestamp": utc_iso(timestamp),
            "event_id": str(uuid.uuid4()),
            "level": level,
            "service": service,
            "event_type": event_type,
            "message": message,
            "environment": "test",
            "host": f"{service}-{random.randint(1, 3):02d}",
            "http_method": None,
            "http_status": None,
            "endpoint": None,
            "response_time_ms": None,
            "db_latency_ms": None,
            "user_id": None,
            "session_id": None,
            "ip_address": fake.ipv4_public(),
            "country": random.choice(COUNTRIES),
            "user_agent": fake.user_agent(),
            "is_bot": False,
            "order_id": None,
            "product_id": None,
            "product_name": None,
            "payment_id": None,
            "payment_method": None,
            "amount": None,
            "currency": random.choice(CURRENCIES),
            "status": None,
            "processing_time_ms": None,
            "is_suspicious": False,
            "tags": [],
            "extra_data": {},
        }
        event.update(values)
        return event

    def product(self):
        return random.choice(PRODUCTS)

    def add_navigation_journey(self):
        """Crée des étapes reliées par le même utilisateur et la même session."""
        ts = self.time()
        user_id = f"USR-{random.randint(10000, 99999)}"
        session_id = str(uuid.uuid4())
        product_id, product_name, price = self.product()
        is_bot = random.random() < self.args.bot_rate
        user_agent = (
            random.choice([
                "Googlebot/2.1 (+http://www.google.com/bot.html)",
                "Bingbot/2.0",
                "Python-requests/2.31",
                "HeadlessChrome/120.0",
            ]) if is_bot else fake.user_agent()
        )
        ip = fake.ipv4_public()
        country = random.choice(COUNTRIES)
        stages = ["page_view", "product_view"]
        if random.random() < 0.58:
            stages.append("add_to_cart")
            if random.random() < 0.72:
                stages.append("checkout_started")
                if random.random() < 0.78:
                    stages.append("payment_attempt")
                    if random.random() < 0.94:
                        stages.append("order_completed")
                    else:
                        stages.append("cart_abandoned")
                else:
                    stages.append("cart_abandoned")
            else:
                stages.append("cart_abandoned")
        elif random.random() < 0.20:
            stages.append("cart_abandoned")

        cursor = ts
        for stage in stages:
            cursor += timedelta(seconds=random.randint(2, 90))
            endpoint = {
                "page_view": "/", "product_view": f"/products/{product_id}",
                "add_to_cart": "/api/v1/cart/items",
                "checkout_started": "/checkout",
                "payment_attempt": "/api/v1/payments",
                "order_completed": "/order/confirmation",
                "cart_abandoned": "/cart/abandoned",
            }[stage]
            self.events.append(self.base(
                "navigation", "web-frontend", "INFO", cursor,
                f"Étape du tunnel e-commerce : {stage}",
                http_method="POST" if stage in ("add_to_cart", "payment_attempt") else "GET",
                http_status=200, endpoint=endpoint,
                response_time_ms=random.randint(20, 600),
                user_id=user_id, session_id=session_id, ip_address=ip,
                country=country, user_agent=user_agent, is_bot=is_bot,
                product_id=product_id, product_name=product_name,
                amount=price,
                status=stage,
                tags=["bot_traffic"] if is_bot else [],
                extra_data={"funnel_stage": stage, "unit_price": price},
            ))

    def add_order_and_payment(self):
        ts = self.time()
        product_id, product_name, unit_price = self.product()
        quantity = random.randint(1, 4)
        amount = round(unit_price * quantity, 2)
        order_id = f"ORD-{fake.bothify(text='########')}"
        user_id = f"USR-{random.randint(10000, 99999)}"
        processing_ms = random.randint(800, 18000)
        self.events.append(self.base(
            "order", "order-service", "INFO", ts,
            f"Commande {order_id} créée",
            http_method="POST", http_status=201, endpoint="/api/v1/orders",
            response_time_ms=random.randint(50, 800),
            user_id=user_id, order_id=order_id, product_id=product_id,
            product_name=product_name, amount=amount, status="created",
            processing_time_ms=processing_ms,
            extra_data={"quantity": quantity, "unit_price": unit_price,
                        "processing_started_at": utc_iso(ts),
                        "processing_finished_at": utc_iso(ts + timedelta(milliseconds=processing_ms))},
        ))
        payment_ok = random.random() < 0.94
        payment_id = f"PAY-{fake.bothify(text='##########')}"
        self.events.append(self.base(
            "payment", "payment-service", "INFO" if payment_ok else "ERROR",
            ts + timedelta(milliseconds=random.randint(100, 2000)),
            f"Paiement {payment_id} {'accepté' if payment_ok else 'refusé'}",
            http_method="POST", http_status=200 if payment_ok else 502,
            endpoint="/api/v1/payments", response_time_ms=random.randint(100, 2500),
            user_id=user_id, order_id=order_id, product_id=product_id,
            product_name=product_name, payment_id=payment_id,
            payment_method=random.choice(PAYMENT_METHODS), amount=amount,
            status="success" if payment_ok else "failed",
            tags=[] if payment_ok else ["payment_failure"],
            extra_data={"provider": random.choice(["Stripe", "PayPal", "LocalBank"]),
                        "failure_reason": None if payment_ok else random.choice(
                            ["card_declined", "gateway_timeout", "provider_unavailable"])},
        ))
        if payment_ok and random.random() < 0.07:
            refund_ts = ts + timedelta(hours=random.randint(1, 20))
            self.events.append(self.base(
                "refund", "order-service", "INFO", refund_ts,
                f"Remboursement de la commande {order_id}",
                http_method="POST", http_status=200,
                endpoint=f"/api/v1/orders/{order_id}/refund",
                user_id=user_id, order_id=order_id, product_id=product_id,
                product_name=product_name, payment_id=payment_id,
                amount=amount, status="refunded",
                extra_data={"refund_reason": random.choice(
                    ["customer_request", "damaged_product", "duplicate_order"])},
            ))

    def add_http_error(self):
        ts = self.time()
        code = random.choices([404, 500, 504], weights=[45, 40, 15])[0]
        product_id, product_name, _ = self.product()
        service = random.choice(["api-gateway", "catalog-service", "order-service",
                                 "payment-service", "cart-service"])
        endpoint = (f"/api/v1/products/{product_id}" if code == 404 else
                    random.choice(["/api/v1/orders", "/api/v1/payments",
                                   f"/api/v1/products/{product_id}", "/api/v1/cart"]))
        status = "timeout" if code == 504 else "error"
        self.events.append(self.base(
            "application_error", service, "ERROR" if code != 404 else "WARNING",
            ts, f"Erreur HTTP {code} sur {endpoint}",
            http_method=random.choice(["GET", "POST"]),
            http_status=code, endpoint=endpoint,
            response_time_ms=random.randint(3000, 12000) if code == 504 else random.randint(20, 1200),
            user_id=f"USR-{random.randint(10000, 99999)}",
            product_id=product_id, product_name=product_name,
            status=status, tags=[f"http_{code}", "timeout" if code == 504 else "http_error"],
            extra_data={"error_type": {404: "NotFound", 500: "InternalServerError",
                                      504: "GatewayTimeout"}[code],
                        "product_context": product_id},
        ))

    def add_performance(self):
        ts = self.time()
        service = random.choice(SERVICES)
        slow = random.random() < 0.15
        response = random.randint(1800, 8000) if slow else random.randint(15, 700)
        db_latency = random.randint(900, 4000) if slow and service == "database" else random.randint(2, 250)
        endpoint = random.choice(["/api/v1/products", "/api/v1/orders",
                                  "/api/v1/search", "/api/v1/payments"])
        self.events.append(self.base(
            "performance", service, "WARNING" if slow else "INFO", ts,
            f"Mesure de performance : réponse {response} ms",
            http_method="GET", http_status=200, endpoint=endpoint,
            response_time_ms=response, db_latency_ms=db_latency,
            tags=["slow_response"] if slow else [],
            extra_data={"response_threshold_ms": 1500, "db_threshold_ms": 500},
        ))

    def add_fraud(self):
        ts = self.time()
        reason = random.choice(["multiple_payment_attempts", "unusual_amount",
                                "suspicious_ip", "rapid_requests", "bot_detected"])
        is_bot = reason in ("rapid_requests", "bot_detected") or random.random() < 0.25
        product_id, product_name, _ = self.product()
        self.events.append(self.base(
            "fraud", "payment-service", "WARNING", ts,
            f"Activité potentiellement frauduleuse : {reason}",
            http_method="POST", http_status=202,
            endpoint="/api/v1/payments/verify",
            user_id=f"USR-{random.randint(10000, 99999)}",
            product_id=product_id, product_name=product_name,
            amount=round(random.uniform(900, 9000), 2),
            is_bot=is_bot, is_suspicious=True, status="flagged",
            tags=["fraud_suspected", reason] + (["bot_traffic"] if is_bot else []),
            extra_data={"risk_score": round(random.uniform(0.70, 0.99), 2),
                        "reason": reason, "manual_review_required": True},
        ))

    def add_payment_spike(self):
        reasons = ["gateway_timeout", "provider_unavailable", "connection_refused"]
        for _ in range(self.args.payment_spike_count):
            ts = self.spike_start + timedelta(
                seconds=random.randint(0, self.args.payment_spike_duration * 60 - 1))
            product_id, product_name, _ = self.product()
            self.events.append(self.base(
                "payment", "payment-service", "ERROR", ts,
                "PIC INJECTÉ : échec de paiement pour test d'alerte",
                http_method="POST", http_status=502,
                endpoint="/api/v1/payments", response_time_ms=random.randint(2500, 10000),
                user_id=f"USR-{random.randint(10000, 99999)}",
                order_id=f"ORD-{fake.bothify(text='########')}",
                product_id=product_id, product_name=product_name,
                payment_id=f"PAY-{fake.bothify(text='##########')}",
                payment_method=random.choice(PAYMENT_METHODS),
                amount=round(random.uniform(20, 2500), 2), status="failed",
                is_suspicious=False,
                tags=["payment_failure", "injected_spike"],
                extra_data={"failure_reason": random.choice(reasons),
                            "injected_for_alert_test": True,
                            "spike_duration_minutes": self.args.payment_spike_duration},
            ))

    def add_traffic_spike(self):
        # Trafic web additionnel concentré sur une courte fenêtre pour visualiser
        # les pics de requêtes et distinguer les bots du trafic utilisateur.
        for _ in range(self.args.traffic_spike_count):
            ts = self.traffic_start + timedelta(seconds=random.randint(0, 119))
            is_bot = random.random() < 0.65
            product_id, product_name, _ = self.product()
            self.events.append(self.base(
                "traffic", "api-gateway", "WARNING" if is_bot else "INFO", ts,
                "Pic de trafic détecté — requête entrante",
                http_method="GET", http_status=200,
                endpoint=f"/api/v1/products/{product_id}",
                response_time_ms=random.randint(10, 900),
                user_id=None if is_bot else f"USR-{random.randint(10000, 99999)}",
                session_id=str(uuid.uuid4()), product_id=product_id,
                product_name=product_name, is_bot=is_bot,
                tags=["traffic_spike"] + (["bot_traffic"] if is_bot else []),
                extra_data={"traffic_spike_test": True, "source": "synthetic"},
            ))

    def generate(self):
        # Nombre de parcours utilisateur : chaque parcours produit plusieurs
        # événements cohérents, utiles pour analyser conversion et abandon.
        journeys = max(1, int(self.args.count * 0.20))
        for _ in range(journeys):
            self.add_navigation_journey()
        while len(self.events) < self.args.count:
            choice = random.choices(
                ["transaction", "error", "performance", "fraud", "navigation"],
                weights=[30, 20, 18, 8, 24],
            )[0]
            if choice == "transaction":
                self.add_order_and_payment()
            elif choice == "error":
                self.add_http_error()
            elif choice == "performance":
                self.add_performance()
            elif choice == "fraud":
                self.add_fraud()
            else:
                self.add_navigation_journey()

        # Les injections sont ajoutées en supplément : le total final peut donc
        # dépasser --count. Cela garantit le nombre exact d'événements injectés.
        self.add_payment_spike()
        self.add_traffic_spike()
        self.events.sort(key=lambda e: e["@timestamp"])
        return self.events


def write_outputs(events: list[dict[str, Any]], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "logs_ecommerce.csv"
    json_path = output_dir / "logs_ecommerce.json"

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for event in events:
            row = dict(event)
            row["tags"] = ",".join(row["tags"])
            row["extra_data"] = json.dumps(row["extra_data"], ensure_ascii=False)
            writer.writerow(row)

    with json_path.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return csv_path, json_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Générer des logs e-commerce synthétiques pour LogCommerce."
    )
    parser.add_argument("--count", type=int, default=2000,
                        help="Nombre de base d'événements avant injections (défaut 2000).")
    parser.add_argument("--payment-spike-count", type=int, default=60,
                        help="Nombre d'échecs de paiement injectés (défaut 60).")
    parser.add_argument("--payment-spike-duration", type=int, default=5,
                        help="Durée du pic de paiements en minutes (défaut 5).")
    parser.add_argument("--traffic-spike-count", type=int, default=100,
                        help="Nombre de requêtes ajoutées au pic de trafic (défaut 100).")
    parser.add_argument("--bot-rate", type=float, default=0.08,
                        help="Probabilité de bot dans les parcours (entre 0 et 1).")
    parser.add_argument("--start-date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        help="Date de début UTC YYYY-MM-DD.")
    parser.add_argument("--output-dir", default="generated_logs",
                        help="Dossier de sortie.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Graine aléatoire pour reproduire la génération.")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count doit être >= 1")
    if args.payment_spike_count < 0 or args.traffic_spike_count < 0:
        parser.error("Les nombres d'injection ne peuvent pas être négatifs.")
    if args.payment_spike_duration < 1:
        parser.error("--payment-spike-duration doit être >= 1")
    if not 0 <= args.bot_rate <= 1:
        parser.error("--bot-rate doit être compris entre 0 et 1")
    try:
        datetime.strptime(args.start_date, "%Y-%m-%d")
    except ValueError:
        parser.error("--start-date doit respecter YYYY-MM-DD")
    return args


def main():
    args = parse_args()
    events = LogFactory(args).generate()
    csv_path, json_path = write_outputs(events, Path(args.output_dir))

    counts = Counter(event["event_type"] for event in events)
    payment_failures = sum(
        e["event_type"] == "payment" and e["status"] == "failed" for e in events
    )
    suspicious = sum(e["is_suspicious"] for e in events)
    bots = sum(e["is_bot"] for e in events)
    print("\n=== Génération LogCommerce terminée ===")
    print(f"Total événements : {len(events)}")
    print(f"Échecs de paiement : {payment_failures}")
    print(f"Échecs injectés : {args.payment_spike_count}")
    print(f"Événements suspects : {suspicious}")
    print(f"Événements identifiés comme bots : {bots}")
    print("\nRépartition par catégorie :")
    for name, number in sorted(counts.items()):
        print(f"  {name:22s} {number}")
    print(f"\nCSV  : {csv_path}")
    print(f"JSON : {json_path}")
    print("\nLes champs session_id, status, processing_time_ms, service,")
    print("product_id, is_bot et @timestamp facilitent le calcul des KPI.")


if __name__ == "__main__":
    main()
