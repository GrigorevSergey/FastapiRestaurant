#!/bin/bash

echo "Testing payment service..."
echo "Making request to http://localhost:8004/payments/create"

curl -X POST http://localhost:8004/payments/create \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": 1, "amount": 1300}' \
  -v

echo ""
echo "Request completed."