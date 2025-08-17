{{/*
Expand the name of the chart.
*/}}
{{- define "legal-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "legal-backend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "legal-backend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "legal-backend.labels" -}}
helm.sh/chart: {{ include "legal-backend.chart" . }}
{{ include "legal-backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "legal-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "legal-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "legal-backend.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "legal-backend.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create MongoDB connection string
*/}}
{{- define "legal-backend.mongodbUrl" -}}
{{- if .Values.mongodb.password }}
{{- printf "mongodb://%s:%s@%s:%s/%s" .Values.mongodb.username .Values.mongodb.password .Values.mongodb.host .Values.mongodb.port .Values.mongodb.database }}
{{- else }}
{{- printf "mongodb://%s:%s/%s" .Values.mongodb.host .Values.mongodb.port .Values.mongodb.database }}
{{- end }}
{{- end }}

{{/*
Create Redis connection string
*/}}
{{- define "legal-backend.redisUrl" -}}
{{- if .Values.redis.password }}
{{- printf "redis://:%s@%s:%s/0" .Values.redis.password .Values.redis.host .Values.redis.port }}
{{- else }}
{{- printf "redis://%s:%s/0" .Values.redis.host .Values.redis.port }}
{{- end }}
{{- end }}
