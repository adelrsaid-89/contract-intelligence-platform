#!/bin/bash
set -e

echo "Waiting for Elasticsearch to be ready..."
until curl -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"yellow\|green"'; do
  echo "Waiting for Elasticsearch..."
  sleep 5
done

echo "Creating Elasticsearch indices..."

# Create contracts search index
curl -X PUT "elasticsearch:9200/contracts_search" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "custom_text_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "projectId": {"type": "keyword"},
      "title": {
        "type": "text",
        "analyzer": "custom_text_analyzer",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "clientName": {
        "type": "text",
        "analyzer": "custom_text_analyzer"
      },
      "contractValue": {"type": "double"},
      "startDate": {"type": "date"},
      "endDate": {"type": "date"},
      "status": {"type": "keyword"},
      "country": {"type": "keyword"},
      "paymentTerms": {
        "type": "text",
        "analyzer": "custom_text_analyzer"
      },
      "listOfServices": {
        "type": "text",
        "analyzer": "custom_text_analyzer"
      },
      "metadata": {
        "type": "nested",
        "properties": {
          "key": {"type": "keyword"},
          "value": {
            "type": "text",
            "analyzer": "custom_text_analyzer"
          },
          "confidence": {"type": "float"}
        }
      },
      "createdAt": {"type": "date"},
      "updatedAt": {"type": "date"}
    }
  }
}'

# Create obligations search index
curl -X PUT "elasticsearch:9200/obligations_search" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "custom_text_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "contractId": {"type": "keyword"},
      "projectId": {"type": "keyword"},
      "description": {
        "type": "text",
        "analyzer": "custom_text_analyzer"
      },
      "frequency": {"type": "keyword"},
      "dueDate": {"type": "date"},
      "penaltyText": {
        "type": "text",
        "analyzer": "custom_text_analyzer"
      },
      "status": {"type": "keyword"},
      "assigneeId": {"type": "keyword"},
      "assigneeName": {
        "type": "text",
        "analyzer": "custom_text_analyzer"
      },
      "percentComplete": {"type": "integer"},
      "isOverdue": {"type": "boolean"},
      "penaltyRisk": {"type": "double"},
      "source": {"type": "keyword"},
      "confidence": {"type": "float"},
      "createdAt": {"type": "date"},
      "updatedAt": {"type": "date"}
    }
  }
}'

echo "Elasticsearch indices created successfully!"